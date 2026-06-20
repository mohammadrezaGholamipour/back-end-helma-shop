from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="categories")
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, index=True)
    image = Column(String, nullable=True)
    name = Column(String, nullable=False)
