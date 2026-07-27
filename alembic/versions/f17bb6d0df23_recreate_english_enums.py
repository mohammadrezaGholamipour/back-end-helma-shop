"""recreate english enums

Revision ID: f17bb6d0df23
Revises: 93358f861a95
Create Date: 2026-07-27 11:44:52.287301

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f17bb6d0df23"
down_revision: Union[str, Sequence[str], None] = "93358f861a95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TYPE producttype AS ENUM (
            'SOHAN',
            'GAZ'
        );
    """)

    op.execute("""
        CREATE TYPE productmodel AS ENUM (
            'HOBEH',
            'BAGHLAVAEI',
            'GOL',
            'SEKKEI',
            'LOGHMEH',
            'MEDADI',
            'COMBINATION'
        );
    """)

    op.execute("""
        CREATE TYPE oiltype AS ENUM (
            'ANIMAL_OIL',
            'VEGETABLE_BUTTER',
            'NABATI_OIL'
        );
    """)

    op.execute("""
        ALTER TABLE products
        ALTER COLUMN product_type
        TYPE producttype
        USING product_type::producttype;
    """)

    op.execute("""
        ALTER TABLE products
        ALTER COLUMN product_model
        TYPE productmodel
        USING product_model::productmodel;
    """)

    op.execute("""
        ALTER TABLE products
        ALTER COLUMN oil_type
        TYPE oiltype
        USING oil_type::oiltype;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE products
        ALTER COLUMN product_type
        TYPE VARCHAR
        USING product_type::text;
    """)

    op.execute("""
        ALTER TABLE products
        ALTER COLUMN product_model
        TYPE VARCHAR
        USING product_model::text;
    """)

    op.execute("""
        ALTER TABLE products
        ALTER COLUMN oil_type
        TYPE VARCHAR
        USING oil_type::text;
    """)

    op.execute("DROP TYPE producttype;")
    op.execute("DROP TYPE productmodel;")
    op.execute("DROP TYPE oiltype;")
