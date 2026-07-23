from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.enums.blog import BlogStatus


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)

    category_id = Column(
        Integer,
        ForeignKey("blog_categories.id"),
        nullable=False,
    )

    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)

    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)

    image = Column(String, nullable=True)

    status = Column(
        Enum(BlogStatus, name="blogstatus"),
        nullable=False,
        default=BlogStatus.DRAFT,
    )

    display_order = Column(Integer, nullable=False)

    reading_time = Column(Integer, nullable=True)

    views = Column(Integer, nullable=False, default=0)

    is_featured = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    meta_title = Column(String, nullable=True)
    meta_description = Column(String, nullable=True)

    published_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category = relationship(
        "BlogCategory",
        back_populates="blogs",
    )