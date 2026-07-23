from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from app.db.base import Base

class BlogCategory(Base):
    __tablename__ = "blog_categories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    blogs: Mapped[list["Blog"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )
