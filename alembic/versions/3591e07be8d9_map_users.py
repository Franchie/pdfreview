"""map users

Revision ID: 3591e07be8d9
Revises: 7fb15edbe163
Create Date: 2025-09-30 10:59:02.975249

"""

import json
import os
import sys
from decimal import InvalidOperation

# Add to import path, so `import migration_support` works
from os import path
from typing import Callable

from sqlalchemy import VARCHAR, Column, Integer, Text, sql

from alembic import op

sys.path.append(path.dirname(__file__) + "/../")


# revision identifiers, used by Alembic.
revision = "3591e07be8d9"
down_revision = "7fb15edbe163"
branch_labels = None
depends_on = None


def upgrade():
    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "user_map.json"), "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        email_map = data["email_map"]
        name_map = data["name_map"]

    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "override.json"), "r", encoding="utf-8"
    ) as f:
        for name, email in json.load(f).items():
            name_map[name] = email_map[email]

    conn = op.get_bind()
    seen_emails: set[str] = set()
    seen_names: set[str] = set()

    seen_emails = seen_emails.union(
        {x.owner for x in conn.execute(sql.text("SELECT DISTINCT owner FROM reviews")).fetchall()}
    )
    seen_emails = seen_emails.union(
        {x.owner for x in conn.execute(sql.text("SELECT DISTINCT owner FROM activity")).fetchall()}
    )
    seen_emails = seen_emails.union(
        {x.reader for x in conn.execute(sql.text("SELECT DISTINCT reader FROM myreviews")).fetchall()}
    )
    seen_emails = seen_emails.union(
        {x.reader for x in conn.execute(sql.text("SELECT DISTINCT reader FROM myread")).fetchall()}
    )

    seen_names = {x.author for x in conn.execute(sql.text("SELECT DISTINCT author FROM comments")).fetchall()}

    email_transform: dict[str, dict[str, str]] = {}
    for email in seen_emails:
        real_email = (email + "@arm.com" if not email.endswith("@arm.com") else email).lower()
        if real_email not in email_map:
            raise ValueError(f"Unknown email: {real_email}")
        email_transform[email] = email_map[real_email]

    def determine_user(
        func: Callable[[dict[str, dict[str, str]], list[str]], list[dict[str, str]]], candidates: list[str]
    ):
        seen_candidates = func(email_transform, candidates)
        if len({x["uid"] for x in seen_candidates}) == 1:
            return seen_candidates[0]

        any_candidates = func(email_map, candidates)
        if len({x["uid"] for x in any_candidates}) == 1:
            return any_candidates[0]

        return None

    name_transform: dict[str, dict[str, str]] = {}
    for name in seen_names:
        if name not in name_map:
            # In case of an unknown name, try variants of the standard email format
            email = name.replace(".", "").lower() + "@arm.com"
            email_versions = set(
                [(email[:i] + "." + email[i + 1 :]).replace(" ", "") for i, ch in enumerate(email) if ch == " "]
                + [email.replace(" ", ".")]
            )
            user = determine_user(
                lambda map, candidates: list(filter(None, [map.get(x) for x in candidates])), list(email_versions)
            )
            if user:
                name_transform[name] = user
            else:
                raise ValueError(f"Unknown name: {name}")
        elif name_map[name] is None:
            # In case of duiplicate name, see if we have seen a single uid assosicated
            # with this name in the email transform
            user = determine_user(
                lambda map, candidates: [x for x in map.values() if x["name"] == candidates[0]], [name]
            )
            if user:
                name_transform[name] = user
            else:
                raise ValueError(f"Name is duplicated across org, cannot determine user: {name}")
        else:
            name_transform[name] = name_map[name]

    cases = " ".join([f"WHEN :x{i} THEN :y{i}" for i in range(len(email_transform))])
    params = {f"{k}{i}": v for i, (x, y) in enumerate(email_transform.items()) for k, v in (("x", x), ("y", y["uid"]))}
    conn.execute(sql.text(f"UPDATE reviews SET owner = CASE owner {cases} ELSE owner END"), params)
    conn.execute(sql.text(f"UPDATE activity SET owner = CASE owner {cases} ELSE owner END"), params)
    conn.execute(sql.text(f"UPDATE myreviews SET reader = CASE reader {cases} ELSE reader END"), params)
    conn.execute(sql.text(f"UPDATE myread SET reader = CASE reader {cases} ELSE reader END"), params)

    cases = " ".join([f"WHEN :x{i} THEN :y{i}" for i in range(len(name_transform))])
    params = {f"{k}{i}": v for i, (x, y) in enumerate(name_transform.items()) for k, v in (("x", x), ("y", y["uid"]))}
    conn.execute(sql.text(f"UPDATE comments SET author = CASE author {cases} ELSE author END"), params)

    op.create_table(
        "user_info",
        Column("uid", VARCHAR(64, collation="utf8mb4_bin"), primary_key=True),
        Column("name", Text(collation="utf8mb4_bin"), nullable=False),
        Column("email", VARCHAR(128, collation="utf8mb4_bin"), nullable=False, unique=True),
        Column("last_active", Integer(), nullable=False),
    )
    conn.execute(sql.text("ALTER TABLE user_info CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_bin'"))

    for user in list(email_transform.values()) + list(name_transform.values()):
        conn.execute(
            sql.text(
                "INSERT INTO user_info (uid, name, email, last_active) VALUES (:uid, :name, :email, 0) ON DUPLICATE KEY UPDATE name=VALUES(name), email=VALUES(email)"
            ),
            {"uid": user["uid"], "name": user["name"], "email": user["email"]},
        )


def downgrade():
    conn = op.get_bind()
    seen_uids: set[str] = set()
    uid_map: dict[str, dict[str, str]] = {}

    seen_uids = seen_uids.union(
        {x.owner for x in conn.execute(sql.text("SELECT DISTINCT owner FROM reviews")).fetchall()}
    )
    seen_uids = seen_uids.union(
        {x.owner for x in conn.execute(sql.text("SELECT DISTINCT owner FROM activity")).fetchall()}
    )
    seen_uids = seen_uids.union(
        {x.reader for x in conn.execute(sql.text("SELECT DISTINCT reader FROM myreviews")).fetchall()}
    )
    seen_uids = seen_uids.union(
        {x.reader for x in conn.execute(sql.text("SELECT DISTINCT reader FROM myread")).fetchall()}
    )
    seen_uids = seen_uids.union(
        {x.author for x in conn.execute(sql.text("SELECT DISTINCT author FROM comments")).fetchall()}
    )

    results = conn.execute(sql.text("SELECT uid, email, name FROM user_info")).fetchall()
    for uid in seen_uids:
        user = [x for x in results if x.uid == uid]
        if len(user) == 0:
            raise InvalidOperation(f"Cannot find uid in user_info: {uid}")
        uid_map[uid] = {"email": user[0].email, "name": user[0].name}

    cases = " ".join([f"WHEN :x{i} THEN :y{i}" for i in range(len(seen_uids))])
    params = {f"{k}{i}": v for i, x in enumerate(seen_uids) for k, v in (("x", x), ("y", uid_map[x]["email"]))}
    conn.execute(sql.text(f"UPDATE reviews SET owner = CASE owner {cases} ELSE owner END"), params)
    conn.execute(sql.text(f"UPDATE activity SET owner = CASE owner {cases} ELSE owner END"), params)
    conn.execute(sql.text(f"UPDATE myreviews SET reader = CASE reader {cases} ELSE reader END"), params)
    conn.execute(sql.text(f"UPDATE myread SET reader = CASE reader {cases} ELSE reader END"), params)

    cases = " ".join([f"WHEN :x{i} THEN :y{i}" for i in range(len(seen_uids))])
    params = {f"{k}{i}": v for i, x in enumerate(seen_uids) for k, v in (("x", x), ("y", uid_map[x]["name"]))}
    conn.execute(sql.text(f"UPDATE comments SET author = CASE author {cases} ELSE author END"), params)

    op.drop_table("user_info")
