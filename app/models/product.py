from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category",back_populates="products")
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=True)
    volume = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    image = Column(String, nullable=True)
