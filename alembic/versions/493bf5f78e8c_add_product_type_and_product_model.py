from alembic import op
import sqlalchemy as sa

revision = "493bf5f78e8c"
down_revision = "e63f73778ee3"
branch_labels = None
depends_on = None


product_type_enum = sa.Enum(
    "SOHAN",
    "GAZ",
    name="producttype",
)

product_model_enum = sa.Enum(
    "HOBEH",
    "BAGHLAVAEI",
    "GOL",
    "SEKKEI",
    "LOGHMEH",
    "COMBINATION",
    name="productmodel",
)


def upgrade():
    bind = op.get_bind()

    product_type_enum.create(bind, checkfirst=True)
    product_model_enum.create(bind, checkfirst=True)

    op.add_column(
        "products",
        sa.Column("product_type", product_type_enum, nullable=True),
    )

    op.add_column(
        "products",
        sa.Column("product_model", product_model_enum, nullable=True),
    )


def downgrade():
    op.drop_column("products", "product_model")
    op.drop_column("products", "product_type")

    bind = op.get_bind()

    product_model_enum.drop(bind, checkfirst=True)
    product_type_enum.drop(bind, checkfirst=True)