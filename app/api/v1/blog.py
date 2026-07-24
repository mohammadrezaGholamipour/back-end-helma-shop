from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query
from app.schemas.blog import BlogOut, BlogListOut, BlogCategoryOut
from app.models.blog_category import BlogCategory
from app.core.security import get_current_user
from app.enums.blog import BlogStatus
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.blog import Blog
from datetime import datetime
from sqlalchemy import func
import uuid
import os

router = APIRouter(prefix="/helma-shop-api/v1/blog", tags=["Blog"])


UPLOAD_DIR = "uploads/blogs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/create-category", response_model=BlogCategoryOut)
def create_blog_category(
    name: str = Form(...),
    slug: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if db.query(BlogCategory).filter(BlogCategory.slug == slug).first():
        raise HTTPException(
            status_code=400,
            detail="این اسلاگ قبلاً ثبت شده است",
        )

    # ترتیب نمایش
    last_order = db.query(func.max(BlogCategory.display_order)).scalar() or 0

    category = BlogCategory(
        name=name,
        slug=slug,
        display_order=last_order + 1,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.put("/{category_id}", response_model=BlogCategoryOut)
def update_blog_category(
    category_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    display_order: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(BlogCategory).filter(BlogCategory.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="دسته‌بندی یافت نشد",
        )

    # بررسی تکراری نبودن اسلاگ
    slug_exists = (
        db.query(BlogCategory)
        .filter(
            BlogCategory.slug == slug,
            BlogCategory.id != category_id,
        )
        .first()
    )

    if slug_exists:
        raise HTTPException(
            status_code=400,
            detail="این اسلاگ قبلاً ثبت شده است",
        )

    category.name = name
    category.slug = slug
    category.display_order = display_order

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}")
def delete_blog_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(BlogCategory).filter(BlogCategory.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="دسته‌بندی یافت نشد",
        )

    if category.blogs:
        raise HTTPException(
            status_code=400,
            detail="این دسته‌بندی دارای مقاله است و قابل حذف نیست.",
        )

    db.delete(category)
    db.commit()

    return {"message": "دسته‌بندی با موفقیت حذف شد."}


@router.get("/list", response_model=list[BlogCategoryOut])
def get_blog_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    categories = db.query(BlogCategory).order_by(BlogCategory.display_order.asc()).all()

    return categories


@router.get("/{category_id}", response_model=BlogCategoryOut)
def get_blog_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(BlogCategory).filter(BlogCategory.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="دسته‌بندی یافت نشد",
        )

    return category


@router.get("/website/categories/list", response_model=list[BlogCategoryOut])
def get_website_blog_categories(
    db: Session = Depends(get_db),
):
    categories = db.query(BlogCategory).order_by(BlogCategory.display_order.asc()).all()

    return categories


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
    # بررسی تکراری نبودن اسلاگ
    if db.query(Blog).filter(Blog.slug == slug).first():
        raise HTTPException(
            status_code=400,
            detail="این اسلاگ قبلاً ثبت شده است",
        )

    # بررسی وجود دسته‌بندی
    category = db.query(BlogCategory).filter(BlogCategory.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="دسته‌بندی یافت نشد.",
        )

    # آپلود تصویر
    image_url = None

    if image:
        if image.filename is None:
            raise HTTPException(
                status_code=400,
                detail="نام فایل معتبر نیست.",
            )

        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"

        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())

        image_url = f"/uploads/blogs/{filename}"

    # تعیین ترتیب نمایش داخل همان دسته‌بندی
    if display_order is None:
        last_order = (
            db.query(func.max(Blog.display_order))
            .filter(Blog.category_id == category_id)
            .scalar()
            or 0
        )

        display_order = last_order + 1

    blog = Blog(
        title=title,
        slug=slug,
        category_id=category_id,
        summary=summary,
        content=content,
        image=image_url,
        status=status,
        display_order=display_order,
        reading_time=reading_time,
        views=0,
        is_featured=is_featured,
        meta_title=meta_title,
        meta_description=meta_description,
        published_at=published_at,
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return blog


@router.put("/{blog_id}", response_model=BlogOut)
async def update_blog(
    blog_id: int,
    title: str = Form(...),
    slug: str = Form(...),
    category_id: int = Form(...),
    content: str = Form(...),
    summary: str | None = Form(None),
    status: BlogStatus = Form(BlogStatus.DRAFT),
    display_order: int = Form(...),
    reading_time: int | None = Form(None),
    is_featured: bool = Form(False),
    meta_title: str | None = Form(None),
    meta_description: str | None = Form(None),
    published_at: datetime | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="مقاله یافت نشد.",
        )

    # بررسی تکراری نبودن اسلاگ
    slug_exists = (
        db.query(Blog)
        .filter(
            Blog.slug == slug,
            Blog.id != blog_id,
        )
        .first()
    )

    if slug_exists:
        raise HTTPException(
            status_code=400,
            detail="این اسلاگ قبلاً ثبت شده است",
        )

    # بررسی وجود دسته‌بندی
    category = db.query(BlogCategory).filter(BlogCategory.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="دسته‌بندی یافت نشد.",
        )

    # آپلود تصویر جدید
    if image:
        if blog.image:
            old_image = blog.image.lstrip("/")
            if os.path.exists(old_image):
                os.remove(old_image)

        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"

        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())

        blog.image = f"/uploads/blogs/{filename}"

    blog.title = title
    blog.slug = slug

    blog.category_id = category_id

    blog.summary = summary
    blog.content = content

    blog.status = status

    blog.display_order = display_order

    blog.reading_time = reading_time

    blog.is_featured = is_featured

    blog.meta_title = meta_title
    blog.meta_description = meta_description

    blog.published_at = published_at

    db.commit()
    db.refresh(blog)

    return blog


@router.delete("/{blog_id}")
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="مقاله یافت نشد.",
        )

    # حذف تصویر
    if blog.image:
        image_path = blog.image.lstrip("/")
        if os.path.exists(image_path):
            os.remove(image_path)

    db.delete(blog)
    db.commit()

    return {"message": "مقاله با موفقیت حذف شد."}


@router.get("/list", response_model=BlogListOut)
def get_blogs(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    category_id: int | None = Query(None),
    status: BlogStatus | None = Query(None),
    featured: bool | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Blog)

    if search:
        query = query.filter(Blog.title.ilike(f"%{search}%"))

    if category_id:
        query = query.filter(Blog.category_id == category_id)

    if status:
        query = query.filter(Blog.status == status)

    if featured is not None:
        query = query.filter(Blog.is_featured == featured)

    total = query.count()

    blogs = (
        query.order_by(Blog.category_id.asc(), Blog.display_order.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    last_page = (total + per_page - 1) // per_page

    return {
        "blogs": blogs,
        "total": total,
        "page": page,
        "per_page": per_page,
        "last_page": last_page,
    }


@router.get("/{blog_id}", response_model=BlogOut)
def get_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="مقاله یافت نشد.",
        )

    return blog


@router.get("/website/{slug}", response_model=BlogOut)
def get_blog_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    blog = (
        db.query(Blog)
        .filter(
            Blog.slug == slug,
            Blog.status == BlogStatus.PUBLISHED,
        )
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="مقاله یافت نشد.",
        )

    blog.views += 1

    db.commit()
    db.refresh(blog)

    return blog
