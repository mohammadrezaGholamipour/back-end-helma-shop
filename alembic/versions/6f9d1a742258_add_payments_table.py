"""rebuild payments table to match Payment model

Revision ID: 6f9d1a742258
Revises: f01c3da516a8
Create Date: 2026-08-16 15:47:06.675921

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# =========================================================
# Revision identifiers
# =========================================================

revision: str = "6f9d1a742258"
down_revision: Union[str, Sequence[str], None] = "f01c3da516a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# =========================================================
# UPGRADE
# =========================================================

def upgrade() -> None:

    # =====================================================
    # DROP OLD TABLE + ENUM (جدول فعلاً خالی است)
    # =====================================================

    op.drop_index("ix_payments_ref_id", table_name="payments")
    op.drop_index("ix_payments_authority", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_order_id", table_name="payments")
    op.drop_index("ix_payments_id", table_name="payments")
    op.drop_table("payments")
    op.execute("DROP TYPE IF EXISTS paymentstatus;")

    # =====================================================
    # CREATE NEW PAYMENT STATUS ENUM (۶ مقدار)
    # =====================================================

    # توجه: اینجا enum رو دستی create نمی‌کنیم؛ چون در create_table پایین‌تر
    # با همین Enum object به‌عنوان نوع ستون status استفاده می‌شه و خودِ
    # SQLAlchemy موقع ساخت جدول به‌صورت خودکار CREATE TYPE رو هم اجرا می‌کنه.
    # اگه اینجا هم دستی create کنیم، دوبار تلاش برای ساخت میشه و خطای
    # DuplicateObject می‌ده.
    payment_status_enum = sa.Enum(
        "PENDING",
        "INITIATED",
        "SUCCESS",
        "VERIFIED",
        "FAILED",
        "CANCELLED",
        name="paymentstatus",
    )

    # =====================================================
    # CREATE NEW PAYMENTS TABLE (مطابق مدل Payment)
    # =====================================================

    op.create_table(
        "payments",

        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),

        # ---- درخواست پرداخت ----
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("mobile", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("callback_url", sa.String(), nullable=False),
        sa.Column(
            "status",
            payment_status_enum,
            nullable=False,
            server_default="PENDING",
        ),

        # ---- پاسخ درخواست پرداخت ----
        sa.Column("authority", sa.String(length=36), nullable=True),
        sa.Column("request_code", sa.Integer(), nullable=True),
        sa.Column("request_message", sa.Text(), nullable=True),

        # ---- تأیید پرداخت ----
        sa.Column("ref_id", sa.String(), nullable=True),
        sa.Column("verify_code", sa.Integer(), nullable=True),
        sa.Column("verify_message", sa.Text(), nullable=True),
        sa.Column("card_pan", sa.String(), nullable=True),
        sa.Column("card_hash", sa.String(), nullable=True),
        sa.Column("fee_type", sa.String(), nullable=True),
        sa.Column("fee", sa.Numeric(12, 2), nullable=True),

        # ---- زمان‌بندی ----
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # =====================================================
    # INDEXES
    # =====================================================

    op.create_index("ix_payments_id", "payments", ["id"], unique=False)
    op.create_index("ix_payments_order_id", "payments", ["order_id"], unique=False)
    op.create_index("ix_payments_status", "payments", ["status"], unique=False)
    op.create_index(
        "ix_payments_authority", "payments", ["authority"], unique=True
    )
    op.create_index("ix_payments_ref_id", "payments", ["ref_id"], unique=False)


# =========================================================
# DOWNGRADE
# =========================================================

def downgrade() -> None:

    op.drop_index("ix_payments_ref_id", table_name="payments")
    op.drop_index("ix_payments_authority", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_order_id", table_name="payments")
    op.drop_index("ix_payments_id", table_name="payments")
    op.drop_table("payments")
    op.execute("DROP TYPE IF EXISTS paymentstatus;")

    # نکته: downgrade جدول ساده‌ی قدیمی (نسخه‌ی f01c3da516a8) رو بازسازی
    # نمی‌کنه، چون این migration جایگزینِ اون بود، نه ادامه‌ش. اگه لازم شد
    # برگردی به نسخه‌ی قدیمی، باید مستقیماً به قبل از f01c3da516a8 برگردی.