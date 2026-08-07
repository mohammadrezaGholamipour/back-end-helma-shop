"""add roles permissions remove application id

Revision ID: d301c1732e28
Revises: f17bb6d0df23
Create Date: 2026-08-07 20:54:54.219254

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d301c1732e28"
down_revision: Union[str, Sequence[str], None] = "f17bb6d0df23"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # =========================
    # Categories
    # =========================

    op.drop_index(
        op.f("ix_categories_application_id"),
        table_name="categories"
    )

    op.drop_column(
        "categories",
        "application_id"
    )


    # =========================
    # Stores
    # =========================

    op.drop_column(
        "stores",
        "application_id"
    )


    # =========================
    # Users new fields
    # =========================

    # password_hash
    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(),
            nullable=True
        )
    )

    op.execute("""
        UPDATE users
        SET password_hash = password
    """)

    op.alter_column(
        "users",
        "password_hash",
        nullable=False
    )


    # role enum
    userrole = sa.Enum(
        "ADMIN",
        "CUSTOMER",
        name="userrole"
    )

    userrole.create(
        op.get_bind()
    )


    op.add_column(
        "users",
        sa.Column(
            "role",
            userrole,
            nullable=True
        )
    )

    # کاربر فعلی ادمین
    op.execute("""
        UPDATE users
        SET role='ADMIN'
    """)

    op.alter_column(
        "users",
        "role",
        nullable=False
    )


    # active
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=True
        )
    )


    op.execute("""
        UPDATE users
        SET is_active=true
    """)


    op.alter_column(
        "users",
        "is_active",
        nullable=False
    )


    # verified
    op.add_column(
        "users",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=True
        )
    )


    op.execute("""
        UPDATE users
        SET is_verified=true
    """)


    op.alter_column(
        "users",
        "is_verified",
        nullable=False
    )


    # =========================
    # Indexes
    # =========================

    op.drop_index(
        op.f("ix_users_application_id"),
        table_name="users"
    )

    op.drop_index(
        op.f("ix_users_username"),
        table_name="users"
    )


    op.create_index(
        op.f("ix_users_username"),
        "users",
        ["username"],
        unique=True
    )


    op.create_index(
        op.f("ix_users_mobile"),
        "users",
        ["mobile"],
        unique=True
    )


    # =========================
    # Remove old fields
    # =========================

    op.drop_column(
        "users",
        "application_id"
    )

    op.drop_column(
        "users",
        "password"
    )


def downgrade() -> None:
    pass