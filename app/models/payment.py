from sqlalchemy.orm import relationship
from app.db.base import Base
from enum import Enum
from sqlalchemy import (
    Column,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    status = Column(
        SQLEnum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING,
        index=True,
    )

    authority = Column(
        String,
        nullable=True,
        unique=True,
        index=True,
    )

    ref_id = Column(
        String,
        nullable=True,
        index=True,
    )

    gateway = Column(
        String,
        nullable=False,
        default="zarinpal",
    )

    order = relationship(
        "Order",
        back_populates="payments",
    )
