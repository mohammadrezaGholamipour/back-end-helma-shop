"""add values to oiltype enum

Revision ID: ae5d4e8da434
Revises: 9add62fe988c
Create Date: 2026-07-22 05:13:11.613031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae5d4e8da434'
down_revision: Union[str, Sequence[str], None] = '9add62fe988c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("ALTER TYPE oiltype ADD VALUE IF NOT EXISTS 'NABATI_OIL';")


def downgrade():
    pass
