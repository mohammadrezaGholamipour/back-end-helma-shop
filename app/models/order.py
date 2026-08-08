from enum import Enum

from sqlalchemy import (
    Column,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status = Column(
        SQLEnum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
        index=True,
    )

    total_amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    discount_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    shipping_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    payable_amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="orders",
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
