from sqlalchemy import Column, Integer, ForeignKey, String,UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("product_id", "volume", name="uq_variant_product_volume"),
    )
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)

    volume = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    image = Column(String, nullable=True)

    product = relationship("Product", back_populates="variants")
    
