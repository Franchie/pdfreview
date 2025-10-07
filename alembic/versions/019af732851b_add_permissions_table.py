"""Add permissions table

Revision ID: 019af732851b
Revises: 43e76f87bca2
Create Date: 2025-10-07 12:06:14.323572

"""

import sys

# Add to import path, so `import migration_support` works
from os import path

from sqlalchemy import VARCHAR, Column, Integer, Text, column, func, or_

from alembic import op

sys.path.append(path.dirname(__file__) + "/../")


# revision identifiers, used by Alembic.
revision = "019af732851b"
down_revision = "43e76f87bca2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "acl",
        Column("id", Integer, primary_key=True),
        Column("reviewid", Text(collation="utf8mb4_bin"), nullable=False),
        Column("uid", VARCHAR(64, collation="utf8mb4_bin"), nullable=True),
        Column("gid", VARCHAR(64, collation="utf8mb4_bin"), nullable=True),
    )

    op.create_check_constraint(
        "only_one_gid_or_uid", "acl", func.coalesce(column("uid", VARCHAR), column("gid", VARCHAR)).is_not(None)
    )
    op.create_check_constraint(
        "not_both_uid_and_gid", "acl", or_(column("uid", VARCHAR).is_(None), column("gid", VARCHAR).is_(None))
    )


def downgrade():
    op.drop_table("acl")
