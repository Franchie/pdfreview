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

    conn = op.get_bind()
    seen_emails: set[str] = set()
    seen_names: set[str] = set()

    for result in conn.execute(sql.text("SELECT DISTINCT owner FROM reviews")).fetchall():
        if result.owner not in email_map:
            raise ValueError(f"Unknown email in reviews.owner: {result.owner}")
        seen_emails.add(result.owner)

    for result in conn.execute(sql.text("SELECT DISTINCT reader FROM myreviews")).fetchall():
        if result.reader not in email_map:
            raise ValueError(f"Unknown email in myreviews.reader: {result.reader}")
        seen_emails.add(result.reader)

    for result in conn.execute(sql.text("SELECT DISTINCT owner FROM activity")).fetchall():
        if result.owner not in email_map:
            raise ValueError(f"Unknown email in activity.owner: {result.owner}")
        seen_emails.add(result.owner)

    for result in conn.execute(sql.text("SELECT DISTINCT reader FROM myread")).fetchall():
        if result.reader not in email_map:
            raise ValueError(f"Unknown email in myread.reader: {result.reader}")
        seen_emails.add(result.reader)

    for result in conn.execute(sql.text("SELECT DISTINCT author FROM comments")).fetchall():
        if result.author not in name_map:
            raise ValueError(f"Unknown name in comments.author: {result.author}")
        if name_map[result.author] is None:
            raise ValueError(f"Name is duplicated across org, cannot determine user: {result.author}")
        seen_names.add(result.author)

    for email in seen_emails:
        conn.execute(
            sql.text("UPDATE reviews SET owner=:uid WHERE owner=:email"),
            {"uid": email_map[email]["uid"], "email": email},
        )
        conn.execute(
            sql.text("UPDATE myreviews SET reader=:uid WHERE reader=:email"),
            {"uid": email_map[email]["uid"], "email": email},
        )
        conn.execute(
            sql.text("UPDATE activity SET owner=:uid WHERE owner=:email"),
            {"uid": email_map[email]["uid"], "email": email},
        )
        conn.execute(
            sql.text("UPDATE myread SET reader=:uid WHERE reader=:email"),
            {"uid": email_map[email]["uid"], "email": email},
        )

    for name in seen_names:
        conn.execute(
            sql.text("UPDATE comments SET author=:uid WHERE author=:name"),
            {"uid": name_map[name]["uid"], "name": name},
        )

    op.create_table(
        "user_info",
        Column("uid", VARCHAR(64, collation="utf8mb4_bin"), primary_key=True),
        Column("name", Text(collation="utf8mb4_bin"), nullable=False),
        Column("email", VARCHAR(128, collation="utf8mb4_bin"), nullable=False, unique=True),
        Column("last_active", Integer(), nullable=False),
    )
    conn.execute(sql.text("ALTER TABLE user_info CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_bin'"))

    for email in seen_emails:
        conn.execute(
            sql.text(
                "INSERT INTO user_info (uid, name, email, last_active) VALUES (:uid, :name, :email, 0) ON DUPLICATE KEY UPDATE name=VALUES(name), email=VALUES(email)"
            ),
            {"uid": email_map[email]["uid"], "name": email_map[email]["name"], "email": email},
        )


def downgrade():
    conn = op.get_bind()
    seen_uids: set[str] = set()
    uid_map: dict[str, dict[str, str]] = {}

    for result in conn.execute(sql.text("SELECT DISTINCT owner FROM reviews")).fetchall():
        seen_uids.add(result.owner)
    for result in conn.execute(sql.text("SELECT DISTINCT reader FROM myreviews")).fetchall():
        seen_uids.add(result.reader)
    for result in conn.execute(sql.text("SELECT DISTINCT owner FROM activity")).fetchall():
        seen_uids.add(result.owner)
    for result in conn.execute(sql.text("SELECT DISTINCT reader FROM myread")).fetchall():
        seen_uids.add(result.reader)
    for result in conn.execute(sql.text("SELECT DISTINCT author FROM comments")).fetchall():
        seen_uids.add(result.author)

    for uid in seen_uids:
        result = conn.execute(sql.text("SELECT email, name FROM user_info WHERE uid=:uid"), {"uid": uid}).fetchone()
        if not result:
            raise InvalidOperation(f"Cannot find uid in user_info: {uid}")
        uid_map[uid] = {"email": result.email, "name": result.name}

    for uid in seen_uids:
        conn.execute(
            sql.text("UPDATE reviews SET owner=:email WHERE owner=:uid"),
            {"uid": uid, "email": uid_map[uid]["email"]},
        )
        conn.execute(
            sql.text("UPDATE myreviews SET reader=:email WHERE reader=:uid"),
            {"uid": uid, "email": uid_map[uid]["email"]},
        )
        conn.execute(
            sql.text("UPDATE activity SET owner=:email WHERE owner=:uid"),
            {"uid": uid, "email": uid_map[uid]["email"]},
        )
        conn.execute(
            sql.text("UPDATE myread SET reader=:email WHERE reader=:uid"),
            {"uid": uid, "email": uid_map[uid]["email"]},
        )
        conn.execute(
            sql.text("UPDATE comments SET author=:name WHERE author=:uid"),
            {"uid": uid, "name": uid_map[uid]["name"]},
        )

    op.drop_table("user_info")
