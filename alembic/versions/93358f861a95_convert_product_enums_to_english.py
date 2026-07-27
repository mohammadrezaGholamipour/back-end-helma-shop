"""convert product enums to english

Revision ID: 93358f861a95
Revises: 887c206e9b36
Create Date: 2026-07-27 11:37:57.469807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93358f861a95'
down_revision: Union[str, Sequence[str], None] = '887c206e9b36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op

def upgrade():
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