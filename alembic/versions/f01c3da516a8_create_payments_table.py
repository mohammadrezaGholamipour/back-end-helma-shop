"""create payments table

Revision ID: f01c3da516a8
Revises: 046965a2c67e
Create Date: 2026-08-13 11:05:56.126092

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# =========================================================
# Revision identifiers
# =========================================================

revision: str = "f01c3da516a8"
down_revision: Union[str, Sequence[str], None] = "046965a2c67e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# =========================================================
# UPGRADE
# =========================================================

def upgrade() -> None:

    # =====================================================
    # CREATE PAYMENT STATUS ENUM
    # =====================================================

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'paymentstatus'
            ) THEN

                CREATE TYPE paymentstatus AS ENUM (
                    'PENDING',
                    'SUCCESS',
                    'FAILED'
                );

            END IF;
        END
        $$;
        """
    )

    # =====================================================
    # CREATE PAYMENTS TABLE
    # =====================================================

    op.create_table(
        "payments",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "order_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "amount",
            sa.Numeric(12, 2),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default="PENDING",
        ),

        sa.Column(
            "authority",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "ref_id",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "gateway",
            sa.String(),
            nullable=False,
            server_default="zarinpal",
        ),

        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    # =====================================================
    # CONVERT STATUS TEXT → ENUM
    # =====================================================

    # First remove the TEXT default.
    op.execute(
        """
        ALTER TABLE payments
        ALTER COLUMN status DROP DEFAULT;
        """
    )

    # Convert status column to PostgreSQL ENUM.
    op.execute(
        """
        ALTER TABLE payments
        ALTER COLUMN status
        TYPE paymentstatus
        USING status::paymentstatus;
        """
    )

    # Set the correct ENUM default.
    op.execute(
        """
        ALTER TABLE payments
        ALTER COLUMN status
        SET DEFAULT 'PENDING'::paymentstatus;
        """
    )

    # =====================================================
    # INDEXES
    # =====================================================

    op.create_index(
        "ix_payments_id",
        "payments",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_payments_order_id",
        "payments",
        ["order_id"],
        unique=False,
    )

    op.create_index(
        "ix_payments_status",
        "payments",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_payments_authority",
        "payments",
        ["authority"],
        unique=True,
    )

    op.create_index(
        "ix_payments_ref_id",
        "payments",
        ["ref_id"],
        unique=False,
    )


# =========================================================
# DOWNGRADE
# =========================================================

def downgrade() -> None:

    # =====================================================
    # DROP INDEXES
    # =====================================================

    op.drop_index(
        "ix_payments_ref_id",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_authority",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_status",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_order_id",
        table_name="payments",
    )

    op.drop_index(
        "ix_payments_id",
        table_name="payments",
    )

    # =====================================================
    # DROP TABLE
    # =====================================================

    op.drop_table(
        "payments",
    )

    # =====================================================
    # DROP ENUM
    # =====================================================

    op.execute(
        """
        DROP TYPE IF EXISTS paymentstatus;
        """
    )