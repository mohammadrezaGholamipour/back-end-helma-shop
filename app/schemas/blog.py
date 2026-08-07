from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.enums.blog import BlogStatus


# =====================================================
# BLOG CATEGORY
# =====================================================

class BlogCategoryOut(BaseModel):
    id: int

    name: str
    slug: str

    display_order: int

    model_config = ConfigDict(
        from_attributes=True
    )


class BlogCategoryCreate(BaseModel):
    name: str
    slug: str

    model_config = ConfigDict(
        from_attributes=True
    )


class BlogCategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    display_order: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True
    )


class BlogCategoryOrderItem(BaseModel):
    id: int
    display_order: int


# =====================================================
# BLOG
# =====================================================

class BlogOut(BaseModel):
    id: int

    category_id: int

    title: str
    slug: str

    summary: Optional[str] = None
    content: str

    image: Optional[str] = None

    status: BlogStatus

    display_order: int

    reading_time: Optional[int] = None

    views: int

    is_featured: bool

    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    published_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    category: Optional[BlogCategoryOut] = None

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )


class BlogCreate(BaseModel):
    title: str
    slug: str
    category_id: int

    summary: Optional[str] = None
    content: str

    status: BlogStatus = BlogStatus.DRAFT

    display_order: Optional[int] = None

    reading_time: Optional[int] = None

    is_featured: bool = False

    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    published_at: Optional[datetime] = None


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None

    category_id: Optional[int] = None

    summary: Optional[str] = None
    content: Optional[str] = None

    status: Optional[BlogStatus] = None

    display_order: Optional[int] = None

    reading_time: Optional[int] = None

    is_featured: Optional[bool] = None

    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    published_at: Optional[datetime] = None


class BlogOrderItem(BaseModel):
    id: int
    display_order: int


# =====================================================
# BLOG LIST
# =====================================================

class BlogListOut(BaseModel):
    blogs: list[BlogOut]

    total: int

    page: int

    per_page: int

    last_page: int

    model_config = ConfigDict(
        from_attributes=True
    )