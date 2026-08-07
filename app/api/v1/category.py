from fastapi import (
    APIRouter,
    Depends,
    Form,
    UploadFile,
    File,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.category import Category
from app.models.product import Product
from app.models.user import User

from app.schemas.category import (
    CategoryOut,
    CategoryOrderItem,
)

from app.core.security import get_current_user

import uuid
import os

router = APIRouter(
    prefix="/helma-shop-api/v1/category",
    tags=["Category"],
)


UPLOAD_DIR = "uploads/categories"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =====================================================
# CREATE CATEGORY
# =====================================================


@router.post(
    "/create",
    response_model=CategoryOut,
)
def create_category(
    name: str = Form(...),
    slug: str = Form(...),
    meta_title: str | None = Form(None),
    meta_description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    exists_name = (
        db.query(Category)
        .filter(
            Category.name == name,
            Category.owner_id == current_user.id,
        )
        .first()
    )

    if exists_name:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "name",
                "message": "این نام قبلاً ثبت شده است",
            },
        )

    exists_slug = db.query(Category).filter(Category.slug == slug).first()

    if exists_slug:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "slug",
                "message": "این اسلاگ قبلاً استفاده شده است",
            },
        )

    image_url = None

    if image:

        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail={"message": "فایل باید تصویر باشد"},
            )

        ext = os.path.splitext(image.filename)[1]

        filename = f"{uuid.uuid4().hex}{ext}"

        path = os.path.join(UPLOAD_DIR, filename)

        with open(path, "wb") as buffer:
            buffer.write(image.file.read())

        image_url = f"/uploads/categories/{filename}"

    last_order = (
        db.query(func.max(Category.display_order))
        .filter(Category.owner_id == current_user.id)
        .scalar()
        or 0
    )

    category = Category(
        owner_id=current_user.id,
        name=name,
        slug=slug,
        image=image_url,
        meta_title=meta_title,
        meta_description=meta_description,
        display_order=last_order + 1,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


# =====================================================
# GET MY CATEGORIES
# =====================================================


@router.get(
    "/me",
    response_model=list[CategoryOut],
)
def get_my_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return (
        db.query(Category)
        .filter(Category.owner_id == current_user.id)
        .order_by(Category.display_order.asc())
        .all()
    )


# =====================================================
# DELETE CATEGORY
# =====================================================


@router.delete("/delete/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            Category.owner_id == current_user.id,
        )
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail={"message": "دسته بندی یافت نشد"})

    db.delete(category)
    db.commit()

    return {"message": "دسته بندی و محصولات آن حذف شدند"}


# =====================================================
# GET CATEGORY PRODUCTS
# =====================================================


@router.get("/{slug}")
def get_category_products(
    slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):

    category = db.query(Category).filter(Category.slug == slug).first()

    if not category:
        raise HTTPException(status_code=404, detail={"message": "دسته بندی یافت نشد"})

    query = db.query(Product).filter(Product.category_id == category.id)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    total = query.count()

    products = (
        query.order_by(Product.display_order)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "category": category,
        "products": products,
        "total": total,
        "page": page,
        "per_page": per_page,
        "last_page": (total + per_page - 1) // per_page,
    }


# =====================================================
# UPDATE CATEGORY
# =====================================================


@router.put("/update", response_model=CategoryOut)
def update_category(
    category_id: int = Form(...),
    name: str | None = Form(None),
    slug: str | None = Form(None),
    display_order: int | None = Form(None),
    meta_title: str | None = Form(None),
    meta_description: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            Category.owner_id == current_user.id,
        )
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail={"message": "دسته بندی یافت نشد"})

    if name is not None:
        category.name = name

    if slug is not None:

        exists = (
            db.query(Category)
            .filter(
                Category.slug == slug,
                Category.id != category_id,
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=400, detail={"message": "این اسلاگ قبلاً استفاده شده"}
            )

        category.slug = slug

    if display_order is not None:
        category.display_order = display_order

    if meta_title is not None:
        category.meta_title = meta_title

    if meta_description is not None:
        category.meta_description = meta_description

    if image:

        ext = os.path.splitext(image.filename)[1]

        filename = f"{uuid.uuid4().hex}{ext}"

        path = os.path.join(UPLOAD_DIR, filename)

        with open(path, "wb") as buffer:
            buffer.write(image.file.read())

        category.image = f"/uploads/categories/{filename}"

    db.commit()
    db.refresh(category)

    return category


# =====================================================
# UPDATE DISPLAY ORDER
# =====================================================


@router.put("/display-order")
def update_category_display_order(
    items: list[CategoryOrderItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    ids = [item.id for item in items]


    categories = (
        db.query(Category)
        .filter(
            Category.id.in_(ids),
            Category.owner_id == current_user.id,
        )
        .all()
    )


    if len(categories) != len(ids):
        raise HTTPException(
            status_code=404,
            detail={
                "message": "برخی دسته بندی‌ها یافت نشدند"
            }
        )


    category_map = {
        category.id: category
        for category in categories
    }


    for item in items:
        category_map[item.id].display_order = item.display_order


    db.commit()


    return {
        "message": "ترتیب دسته بندی‌ها با موفقیت بروزرسانی شد"
    }