from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.blog_category import BlogCategory
from app.schemas.blog import BlogCategoryOut
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/blog-category", tags=["Blog Category"])


@router.post("/create", response_model=BlogCategoryOut)
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


@router.get("/website/list", response_model=list[BlogCategoryOut])
def get_website_blog_categories(
    db: Session = Depends(get_db),
):
    categories = db.query(BlogCategory).order_by(BlogCategory.display_order.asc()).all()

    return categories
