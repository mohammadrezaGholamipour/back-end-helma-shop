from sqlalchemy import Column, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.db.base import Base


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    first_name = Column(
        String,
        nullable=True,
    )

    last_name = Column(
        String,
        nullable=True,
    )

    email = Column(
        String,
        nullable=True,
        unique=True,
        index=True,
    )

    address = Column(
        String,
        nullable=True,
    )

    postal_code = Column(
        String,
        nullable=True,
    )

    latitude = Column(
        Numeric(10, 7),
        nullable=True,
    )

    longitude = Column(
        Numeric(10, 7),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="customer_profile",
    )
