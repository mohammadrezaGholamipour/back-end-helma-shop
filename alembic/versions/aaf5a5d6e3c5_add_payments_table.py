"""add payments table

Revision ID: aaf5a5d6e3c5
Revises: 6f9d1a742258
Create Date: 2026-08-16 15:48:35.609616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaf5a5d6e3c5'
down_revision: Union[str, Sequence[str], None] = '6f9d1a742258'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
