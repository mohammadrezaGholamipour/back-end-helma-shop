from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    UploadFile,
    File,
    Query,
)

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.schemas.blog import (
    BlogOut,
    BlogListOut,
    BlogCategoryOut,
)

from app.models.blog_category import BlogCategory
from app.models.blog import Blog
from app.models.user import User

from app.enums.blog import BlogStatus

from app.core.security import get_current_user
from app.db.session import get_db

from datetime import datetime

import uuid
import os

router = APIRouter(
    prefix="/helma-shop-api/v1/blog",
    tags=["Blog"],
)


UPLOAD_DIR = "uploads/blogs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_image(image: UploadFile | None):

    if not image:
        return None

    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="فایل باید تصویر باشد")

    ext = os.path.splitext(image.filename)[1]

    filename = f"{uuid.uuid4().hex}{ext}"

    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        buffer.write(image.file.read())

    return f"/uploads/blogs/{filename}"


# =====================================================
# CREATE BLOG CATEGORY
# =====================================================


@router.post("/create-category", response_model=BlogCategoryOut)
def create_blog_category(
    name: str = Form(...),
    slug: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    exists = (
        db.query(BlogCategory)
        .filter(BlogCategory.slug == slug, BlogCategory.owner_id == current_user.id)
        .first()
    )

    if exists:
        raise HTTPException(status_code=400, detail="این اسلاگ قبلا ثبت شده است")

    order = (
        db.query(func.max(BlogCategory.display_order))
        .filter(BlogCategory.owner_id == current_user.id)
        .scalar()
        or 0
    )

    category = BlogCategory(
        owner_id=current_user.id,
        name=name,
        slug=slug,
        display_order=order + 1,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


# =====================================================
# UPDATE BLOG CATEGORY
# =====================================================


@router.put("/category/{category_id}", response_model=BlogCategoryOut)
def update_blog_category(
    category_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    display_order: int | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    category = (
        db.query(BlogCategory)
        .filter(
            BlogCategory.id == category_id, BlogCategory.owner_id == current_user.id
        )
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="دسته بندی یافت نشد")

    exists = (
        db.query(BlogCategory)
        .filter(BlogCategory.slug == slug, BlogCategory.id != category_id)
        .first()
    )

    if exists:
        raise HTTPException(status_code=400, detail="این اسلاگ قبلا استفاده شده")

    category.name = name
    category.slug = slug

    if display_order is not None:
        category.display_order = display_order

    db.commit()
    db.refresh(category)

    return category


# =====================================================
# DELETE BLOG CATEGORY
# =====================================================


@router.delete("/category/{category_id}")
def delete_blog_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    category = (
        db.query(BlogCategory)
        .filter(
            BlogCategory.id == category_id, BlogCategory.owner_id == current_user.id
        )
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="دسته بندی یافت نشد")

    if category.blogs:
        raise HTTPException(status_code=400, detail="این دسته بندی دارای مقاله است")

    db.delete(category)
    db.commit()

    return {"message": "دسته بندی حذف شد"}


# =====================================================
# WEBSITE CATEGORY LIST
# =====================================================


@router.get("/website/categories/list", response_model=list[BlogCategoryOut])
def website_categories(
    db: Session = Depends(get_db),
):

    return db.query(BlogCategory).order_by(BlogCategory.display_order.asc()).all()


# =====================================================
# CREATE BLOG
# =====================================================


@router.post("/create-blog", response_model=BlogOut)
async def create_blog(
    title: str = Form(...),
    slug: str = Form(...),
    category_id: int = Form(...),
    content: str = Form(...),
    summary: str | None = Form(None),
    status: BlogStatus = Form(BlogStatus.DRAFT),
    display_order: int | None = Form(None),
    reading_time: int | None = Form(None),
    is_featured: bool = Form(False),
    meta_title: str | None = Form(None),
    meta_description: str | None = Form(None),
    published_at: datetime | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    exists = db.query(Blog).filter(Blog.slug == slug).first()

    if exists:
        raise HTTPException(status_code=400, detail="این اسلاگ قبلا ثبت شده")

    category = (
        db.query(BlogCategory)
        .filter(
            BlogCategory.id == category_id, BlogCategory.owner_id == current_user.id
        )
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="دسته بندی یافت نشد")

    if display_order is None:

        display_order = (
            db.query(func.max(Blog.display_order))
            .filter(Blog.category_id == category_id)
            .scalar()
            or 0
        ) + 1

    blog = Blog(
        owner_id=current_user.id,
        title=title,
        slug=slug,
        category_id=category_id,
        content=content,
        summary=summary,
        status=status,
        display_order=display_order,
        reading_time=reading_time,
        is_featured=is_featured,
        meta_title=meta_title,
        meta_description=meta_description,
        published_at=published_at,
        image=save_image(image),
        views=0,
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return blog
