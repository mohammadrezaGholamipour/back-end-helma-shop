from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")
    store = relationship("Store", back_populates="owner", uselist=False)
    application_id = Column(Integer, index=True, nullable=False, unique=True)
    userName = Column(String, index=True, nullable=False, name="username")
    id = Column(Integer, primary_key=True, index=True)
    password = Column(String, nullable=False)
    mobile = Column(String, nullable=False)
