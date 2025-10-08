#!/usr/bin/env python3

import json
import os
from typing import Any, Generator

import requests


def iter_graph_collection(access_token: str, initial_url: str) -> Generator[dict[str, str], None, None]:
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    session = requests.Session()
    url = initial_url

    print("Fetching data", end="", flush=True)
    while url:
        print(".", end="", flush=True)
        data: dict[str, Any] = session.request("GET", url, headers=headers).json()
        if "error" in data:
            raise requests.RequestException(data["error"])
        yield from data.get("value", [])
        url = data.get("@odata.nextLink")
    print("", flush=True)


def main():
    url = "https://graph.microsoft.com/v1.0/users?$select=id,displayName,mail,proxyAddresses&$top=999"

    rows: list[dict[str, Any]] = list(iter_graph_collection(os.environ["MIGRATION_ACCESS_TOKEN"], url))

    email_map = {}
    name_map = {}

    for row in [x for x in rows if x["mail"]]:
        current_email = row["mail"].lower()
        other_email = [x.split(":")[-1].lower() for x in row["proxyAddresses"]]

        if not current_email.endswith("@arm.com"):
            continue

        for email in set([current_email] + [x for x in other_email if x.endswith("@arm.com")]):
            if email in email_map:
                raise ValueError(f"Duplicate email: {email}")

            email_map[email] = {"uid": row["id"], "name": row["displayName"], "email": email}

        if row["displayName"] in name_map:
            name_map[row["displayName"]] = None
        else:
            name_map[row["displayName"]] = email_map[current_email]

    with open(f"{os.path.dirname(os.path.realpath(__file__))}/../alembic/user_map.json", "w", encoding="utf-8") as f:
        json.dump({"email_map": email_map, "name_map": name_map}, f, indent=4)


if __name__ == "__main__":
    main()
