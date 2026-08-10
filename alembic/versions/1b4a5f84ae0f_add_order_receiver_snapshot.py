"""add order receiver snapshot

Revision ID: 1b4a5f84ae0f
Revises: 2c64709c938e
Create Date: 2026-08-10 08:02:26.482950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b4a5f84ae0f'
down_revision: Union[str, Sequence[str], None] = '2c64709c938e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =====================
    # CUSTOMER PROFILE
    # =====================

    op.add_column(
        "customer_profiles",
        sa.Column("address", sa.String(), nullable=True),
    )

    op.add_column(
        "customer_profiles",
        sa.Column("postal_code", sa.String(), nullable=True),
    )

    op.add_column(
        "customer_profiles",
        sa.Column(
            "latitude",
            sa.Numeric(precision=10, scale=7),
            nullable=True,
        ),
    )

    op.add_column(
        "customer_profiles",
        sa.Column(
            "longitude",
            sa.Numeric(precision=10, scale=7),
            nullable=True,
        ),
    )

    # =====================
    # ORDER ITEMS
    # =====================

    op.add_column(
        "order_items",
        sa.Column(
            "product_name",
            sa.String(),
            nullable=False,
        ),
    )

    op.alter_column(
        "order_items",
        "product_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )

    op.drop_constraint(
        op.f("order_items_product_id_fkey"),
        "order_items",
        type_="foreignkey",
    )

    # =====================
    # ORDER RECEIVER SNAPSHOT
    # =====================

    op.add_column(
        "orders",
        sa.Column(
            "receiver_first_name",
            sa.String(),
            nullable=False,
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "receiver_last_name",
            sa.String(),
            nullable=False,
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "receiver_mobile",
            sa.String(),
            nullable=False,
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "receiver_address",
            sa.String(),
            nullable=False,
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "receiver_postal_code",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "receiver_latitude",
            sa.Numeric(precision=10, scale=7),
            nullable=True,
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "receiver_longitude",
            sa.Numeric(precision=10, scale=7),
            nullable=True,
        ),
    )

def downgrade() -> None:
    op.drop_column(
        "orders",
        "receiver_longitude",
    )

    op.drop_column(
        "orders",
        "receiver_latitude",
    )

    op.drop_column(
        "orders",
        "receiver_postal_code",
    )

    op.drop_column(
        "orders",
        "receiver_address",
    )

    op.drop_column(
        "orders",
        "receiver_mobile",
    )

    op.drop_column(
        "orders",
        "receiver_last_name",
    )

    op.drop_column(
        "orders",
        "receiver_first_name",
    )

    op.create_foreign_key(
        op.f("order_items_product_id_fkey"),
        "order_items",
        "products",
        ["product_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.alter_column(
        "order_items",
        "product_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    op.drop_column(
        "order_items",
        "product_name",
    )

    op.drop_column(
        "customer_profiles",
        "longitude",
    )

    op.drop_column(
        "customer_profiles",
        "latitude",
    )

    op.drop_column(
        "customer_profiles",
        "postal_code",
    )

    op.drop_column(
        "customer_profiles",
        "address",
    )
