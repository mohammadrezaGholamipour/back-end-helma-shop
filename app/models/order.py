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
from enum import Enum


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

    # =========================
    # Receiver Snapshot
    # =========================

    receiver_first_name = Column(
        String,
        nullable=False,
    )

    receiver_last_name = Column(
        String,
        nullable=False,
    )

    receiver_mobile = Column(
        String,
        nullable=False,
    )

    receiver_address = Column(
        String,
        nullable=False,
    )

    receiver_postal_code = Column(
        String,
        nullable=True,
    )

    # =========================
    # Order
    # =========================

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