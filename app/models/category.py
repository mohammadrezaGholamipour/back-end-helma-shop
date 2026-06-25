from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)

    image = Column(String, nullable=True)
    meta_title = Column(String, nullable=True)
    meta_description = Column(String, nullable=True)

    owner = relationship("User", back_populates="categories")
    products = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan"
    )
