"""remove adal

Revision ID: 7fb15edbe163
Revises: c472597eb7ac
Create Date: 2025-09-30 10:41:32.547215

"""

import sys

# Add to import path, so `import migration_support` works
from os import path

from sqlalchemy import Column, Integer, Text, sql

from alembic import op

sys.path.append(path.dirname(__file__) + "/../")


# revision identifiers, used by Alembic.
revision = "7fb15edbe163"
down_revision = "c472597eb7ac"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("adal_auth")


def downgrade():
    op.create_table(
        "adal_auth",
        Column("id", Integer, primary_key=True),
        Column("authkey", Text(collation="utf8mb4_bin")),
        Column("name", Text(collation="utf8mb4_bin")),
        Column("email", Text(collation="utf8mb4_bin")),
        Column("expire", Integer),
    )
    op.get_bind().execute(sql.text("ALTER TABLE adal_auth CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_bin'"))
