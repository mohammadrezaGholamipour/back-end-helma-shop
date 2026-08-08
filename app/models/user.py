from sqlalchemy import Column, Enum as SQLEnum, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    mobile = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    username = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash = Column(
        String,
        nullable=False,
    )

    role = Column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.CUSTOMER,
    )

    categories = relationship(
        "Category",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    store = relationship(
        "Store",
        back_populates="owner",
        uselist=False,
    )
