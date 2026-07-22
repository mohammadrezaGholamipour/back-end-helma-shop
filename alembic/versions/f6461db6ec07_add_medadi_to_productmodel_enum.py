"""add medadi to productmodel enum

Revision ID: f6461db6ec07
Revises: ae5d4e8da434
Create Date: 2026-07-22 05:15:41.190281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6461db6ec07'
down_revision: Union[str, Sequence[str], None] = 'ae5d4e8da434'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        "ALTER TYPE productmodel ADD VALUE IF NOT EXISTS 'MEDADI';"
    )


def downgrade():
    # PostgreSQL حذف مقدار Enum را پشتیبانی نمی‌کند.
    pass