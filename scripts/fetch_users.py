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
        yield from data.get("value", [])
        url = data.get("@odata.nextLink")
    print("", flush=True)


def main():
    url = "https://graph.microsoft.com/v1.0/users?$select=id,displayName,mail&$top=999"

    rows: list[dict[str, str]] = list(iter_graph_collection(os.environ["MIGRATION_ACCESS_TOKEN"], url))

    email_map = {}
    name_map = {}

    for row in rows:
        if not row["mail"] or not row["mail"].endswith("@arm.com"):
            continue

        if row["mail"].lower() in email_map:
            raise ValueError(f"Duplicate email: {row["mail"].lower()}")
        if row["displayName"] in name_map:
            name_map[row["displayName"]] = None
            continue

        email_map[row["mail"].lower()] = {"uid": row["id"], "name": row["displayName"]}
        name_map[row["displayName"]] = {"uid": row["id"], "email": row["mail"].lower()}

    with open(f"{os.path.dirname(os.path.realpath(__file__))}/../alembic/user_map.json", "w", encoding="utf-8") as f:
        json.dump({"email_map": email_map, "name_map": name_map}, f, indent=4)


if __name__ == "__main__":
    main()
