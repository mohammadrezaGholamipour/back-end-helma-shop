from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.enums.blog import BlogStatus


class BlogCategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    display_order: int

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class BlogListOut(BaseModel):
    blogs: list[BlogOut]

    total: int
    page: int
    per_page: int
    last_page: int

    model_config = ConfigDict(from_attributes=True)


from pydantic import BaseModel, ConfigDict


class BlogCategoryCreate(BaseModel):
    name: str
    slug: str


class BlogCategoryUpdate(BaseModel):
    name: str
    slug: str
    display_order: int


