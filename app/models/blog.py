from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.blog import BlogStatus
from app.models.blog_category import BlogCategory


class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("blog_categories.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    image: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    status: Mapped[BlogStatus] = mapped_column(
        Enum(BlogStatus, name="blogstatus"),
        nullable=False,
        default=BlogStatus.DRAFT,
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reading_time: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    views: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    meta_title: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    meta_description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category: Mapped["BlogCategory"] = relationship(
        back_populates="blogs",
    )