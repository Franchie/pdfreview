import json
import time
from datetime import timedelta
from typing import Any

import jwt
import requests
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows, SecuritySchemeType
from fastapi.responses import RedirectResponse
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from jwt.algorithms import RSAAlgorithm
from msal import ConfidentialClientApplication  # type:ignore
from msal import SerializableTokenCache  # type:ignore
from pydantic import BaseModel, ConfigDict, Field

import config


class UserInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    email: str | None = None
    display_name: str | None = Field(None, alias="name")
    user_id: str | None = Field(None, alias="oid")
    roles: list[str] | None = None
    groups: list[str] = []

    def is_admin(self):
        return self.roles and config.config["msal_admin_role"] in list(self.roles)


class SessionTokenCache:
    cache: dict[str, str] = {}

    @classmethod
    def write(cls, session_id: str, value: str):
        cls.cache.update({session_id: value})

    @classmethod
    def read(cls, session_id: str) -> str | None:
        return cls.cache.get(session_id, None)


class GroupsCache:
    cache: dict[str, tuple[int, list[str]]] = {}

    @classmethod
    def write(cls, uid: str, value: list[str]):
        cls.cache.update({uid: (int(time.time()), value)})

    @classmethod
    def read(cls, uid: str) -> list[str] | None:
        result = cls.cache.get(uid, None)

        if result and time.time() - result[0] < timedelta(minutes=10).seconds:
            return result[1]

        return None


class MSALAuthHandler:
    _session_id_key = "session_id"
    _flow_key = "flow"
    _next_path_key = "next_uri"
    _LINK_MAX_AGE = 5 * 60  # 5 minutes

    def __init__(self, client_id: str, client_credential: str, tenant: str, scopes: list[str]):
        self._client_id = client_id
        self._client_credential = client_credential
        self._tenant = tenant
        self._scopes = scopes
        self._http_cache: dict[Any, Any] = {}
        self.serializer = URLSafeTimedSerializer(client_credential)

    def _fetch_jwt_keys(self):
        response = requests.get("https://login.microsoftonline.com/common/discovery/keys", timeout=10)

        keys: dict[str, RSAPublicKey] = {}
        for jwk in response.json()["keys"]:
            kid = jwk["kid"]
            key = RSAAlgorithm.from_jwk(json.dumps(jwk))
            if isinstance(key, RSAPublicKey):
                keys[kid] = key

        return keys

    def _load_token_cache(self, session: dict[str, Any]):
        cache = SerializableTokenCache()
        session_id = session.get(self._session_id_key)
        if session_id:
            token_cache = SessionTokenCache.read(session_id)
            if token_cache:
                cache.deserialize(token_cache)  # type:ignore
        return cache

    def _save_token_cache(self, session: dict[str, Any], cache: SerializableTokenCache):
        if cache.has_state_changed:
            session_id = session.get(self._session_id_key)
            if session_id:
                SessionTokenCache.write(session_id, cache.serialize())

    def _build_msal(self, cache: SerializableTokenCache | None = None):
        return ConfidentialClientApplication(
            self._client_id,
            client_credential=self._client_credential,
            authority=f"https://login.microsoftonline.com/{self._tenant}",
            token_cache=cache,
            http_cache=self._http_cache,
            instance_discovery=False,
        )

    def _validate_token(self, token: str):
        keys = self._fetch_jwt_keys()

        kid = jwt.get_unverified_header(token)["kid"]
        payload = jwt.decode(
            token,
            key=keys[kid],
            algorithms=["RS256"],
            audience=[self._client_id],
            options={"verify_signature": True},
        )

        if payload["tid"] != self._tenant:
            raise jwt.InvalidTokenError("Invalid tenant")

        return payload

    def sign_path(self, path: str):
        return self.serializer.dumps(path)

    def unsign_path(self, token: str):
        try:
            return str(self.serializer.loads(token, max_age=self._LINK_MAX_AGE))
        except (SignatureExpired, BadSignature):
            return None

    def is_safe_path(self, uri: str | None):
        if not uri:
            return False
        if not uri.startswith("/"):
            return False
        if uri.startswith("//"):
            return False
        if "/.." in uri or "\\" in uri:
            return False
        return True

    def authorize_redirect(self, request: Request, next_path: str | None, state: str | None = None):
        auth_code: dict[str, str] = self._build_msal().initiate_auth_code_flow(  # type:ignore
            scopes=self._scopes, redirect_uri=str(request.url_for("_token_route")), state=state
        )
        request.session[self._session_id_key] = auth_code["state"]
        request.session[self._flow_key] = auth_code
        request.session[self._next_path_key] = next_path
        return auth_code["auth_uri"]

    def authorize_access_token(self, request: Request, code: str, state: str | None = None):
        http_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Error")

        auth_code = request.session.get(self._flow_key)
        if not auth_code or not auth_code["state"]:
            raise http_exception
        if state and state != auth_code["state"]:
            raise http_exception

        cache = self._load_token_cache(request.session)
        auth_token: dict[str, str] = self._build_msal(cache).acquire_token_by_auth_code_flow(  # type:ignore
            auth_code, {"code": code, "state": state}, scopes=self._scopes
        )
        if auth_token.get("error") or not auth_token.get("id_token"):
            if auth_token.get("error_description"):
                http_exception.detail = f"{auth_token["error"]}: {auth_token["error_description"]}"
            raise http_exception
        self._save_token_cache(request.session, cache)

        next_path = self.unsign_path(str(request.session.get(self._next_path_key)))
        if not next_path or not self.is_safe_path(next_path):
            next_path = "/"

        return next_path

    def get_id_token_from_session(self, request: Request) -> str | None:
        cache = self._load_token_cache(request.session)
        cca = self._build_msal(cache)
        accounts = cca.get_accounts()  # type:ignore
        if accounts:
            cca.acquire_token_silent(self._scopes, account=accounts[0])  # type:ignore
            self._save_token_cache(request.session, cache)
            return cache.find(  # type:ignore
                cache.CredentialType.ID_TOKEN,
                query={
                    "home_account_id": accounts[0]["home_account_id"],
                },
            )[0]["secret"]
        return None

    def populate_user(self, token_claims: str):
        user = UserInfo.model_validate(self._validate_token(token_claims))
        if not user.user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid user")

        groups = GroupsCache.read(user.user_id)
        if not groups:
            auth_result: dict[str, str] | None = self._build_msal().acquire_token_on_behalf_of(  # type:ignore
                token_claims, ["https://graph.microsoft.com/.default"]
            )

            if "access_token" not in auth_result:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    f"OBO failed: {auth_result.get('error')}: {auth_result.get('error_description')}",
                )

            headers = {"Authorization": f"Bearer {auth_result["access_token"]}"}
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me/transitiveMemberOf/microsoft.graph.group?$select=id&$top=999",
                headers=headers,
                timeout=10,
            ).json()

            if "error" in response:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    f"Graph API call failed: {response.get('error')}: {response.get('error_description')}",
                )

            groups = [x["id"] for x in response["value"]]
            GroupsCache.write(user.user_id, groups)

        user.groups = groups
        return user


class MSALScheme(SecurityBase):
    def __init__(self, authorization_url: str, token_url: str, handler: MSALAuthHandler):
        self.handler = handler
        self.scheme_name = self.__class__.__name__

        flows = OAuthFlows(
            authorizationCode=OAuthFlowAuthorizationCode(
                authorizationUrl=authorization_url,
                tokenUrl=token_url,
                scopes={},
                refreshUrl=None,
            )
        )

        self.model = OAuth2(flows=flows, type=SecuritySchemeType.oauth2)

    async def __call__(self, request: Request):
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token_claims: str | None = None

        authorization = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if authorization and scheme.lower() == "bearer":
            token_claims = token
        else:
            token_claims = self.handler.get_id_token_from_session(request)

        if not token_claims:
            http_exception.detail = "No token found"
            raise http_exception

        try:
            return self.handler.populate_user(token_claims)
        except Exception as ex:
            raise http_exception from ex


class MSALAuth:
    def __init__(self, client_id: str, client_credential: str, tenant: str, scopes: list[str]):
        self.handler = MSALAuthHandler(client_id, client_credential, tenant, scopes)

        self.router = APIRouter()
        self.router.add_api_route(
            name="_login_route", path="/login", endpoint=self._login_route, include_in_schema=False, methods=["GET"]
        )
        self.router.add_api_route(
            name="_token_route", path="/token", endpoint=self._get_token_route, include_in_schema=False, methods=["GET"]
        )

    def _login_route(
        self, request: Request, next_path: str | None = Query(None, alias="next"), state: str | None = None
    ) -> Response:
        auth_uri = self.handler.authorize_redirect(request, next_path, state)
        return RedirectResponse(auth_uri)

    def _get_token_route(self, request: Request, code: str, state: str | None = None) -> Response:
        next_path = self.handler.authorize_access_token(request, code, state)
        return RedirectResponse(url=next_path, headers=dict(request.headers.items()))

    def get_current_user(self, request: Request) -> UserInfo | None:
        token = self.handler.get_id_token_from_session(request)
        if token:
            return self.handler.populate_user(token)
        return None

    @property
    def scheme(self) -> MSALScheme:
        return MSALScheme(
            authorization_url=self.router.url_path_for("_login_route"),
            token_url=self.router.url_path_for("_token_route"),
            handler=self.handler,
        )
