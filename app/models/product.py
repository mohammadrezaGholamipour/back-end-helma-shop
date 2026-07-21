from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean
from app.enums.product import ProductType, ProductModel, OilType
from sqlalchemy.orm import relationship
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    is_packaged = Column(Boolean, nullable=True, default=True)
    description = Column(String, nullable=True)
    image = Column(String, nullable=True)
    product_type = Column(Enum(ProductType), nullable=True)
    product_model = Column(Enum(ProductModel), nullable=True)
    oil_type = Column(Enum(OilType, name="oiltype"), nullable=True)
    meta_title = Column(String, nullable=True)
    meta_description = Column(String, nullable=True)
    display_order = Column(Integer, nullable=False)
    category = relationship("Category", back_populates="products")
    variants = relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan"
    )
