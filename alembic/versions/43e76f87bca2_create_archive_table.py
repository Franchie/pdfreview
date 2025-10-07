"""Create archive table

Revision ID: 43e76f87bca2
Revises: 3591e07be8d9
Create Date: 2025-10-03 11:15:34.307885

"""

import sys

# Add to import path, so `import migration_support` works
from os import path

from sqlalchemy import VARCHAR, Column, Integer, Text

from alembic import op

sys.path.append(path.dirname(__file__) + "/../")


# revision identifiers, used by Alembic.
revision = "43e76f87bca2"
down_revision = "3591e07be8d9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "archives",
        Column("id", Integer, primary_key=True),
        Column("archiveid", VARCHAR(32, collation="utf8mb4_bin"), nullable=False, unique=True),
        Column("reviewid", Text(collation="utf8mb4_bin"), nullable=False),
        Column("type", Text(collation="utf8mb4_bin"), nullable=False),
        Column("filename", Text(collation="utf8mb4_bin"), nullable=False),
        Column("created", Integer(), nullable=False),
    )


def downgrade():
    op.drop_table("archives")
