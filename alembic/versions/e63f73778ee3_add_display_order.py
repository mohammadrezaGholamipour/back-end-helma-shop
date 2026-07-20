"""add display_order

Revision ID: e63f73778ee3
Revises: 883662bc5afd
Create Date: 2026-07-20 20:40:28.760934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e63f73778ee3'
down_revision: Union[str, Sequence[str], None] = '883662bc5afd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "categories",
        sa.Column("display_order", sa.Integer(), nullable=True)
    )

    op.execute("""
        UPDATE categories
        SET display_order = t.rn
        FROM (
            SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
            FROM categories
        ) t
        WHERE categories.id = t.id
    """)

    op.alter_column(
        "categories",
        "display_order",
        nullable=False
    )


def downgrade():
    op.drop_column("categories", "display_order")