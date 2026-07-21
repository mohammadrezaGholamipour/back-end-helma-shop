"""add oil_type to products

Revision ID: 0db0124619fb
Revises: 493bf5f78e8c
Create Date: 2026-07-21 06:51:14.872508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0db0124619fb'
down_revision: Union[str, Sequence[str], None] = '493bf5f78e8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


oil_type_enum = sa.Enum(
    "ANIMAL",
    "VEGETABLE_BUTTER",
    "VEGETABLE_OIL",
    name="oiltype",
)

def upgrade():
    bind = op.get_bind()

    oil_type_enum.create(bind, checkfirst=True)

    op.add_column(
        "products",
        sa.Column(
            "oil_type",
            oil_type_enum,
            nullable=True,
        ),
    )

def downgrade():
    op.drop_column("products", "oil_type")

    bind = op.get_bind()

    oil_type_enum.drop(bind, checkfirst=True)