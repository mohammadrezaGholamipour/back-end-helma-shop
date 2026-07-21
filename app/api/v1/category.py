from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Query
from app.schemas.category import CategoryOut, CreateAndUpdateCategory
from app.core.security import get_current_user
from app.models.category import Category
from app.models.product import Product
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
import uuid
import os

router = APIRouter(prefix="/helma-shop-api/v1/category", tags=["Category"])

UPLOAD_DIR = "uploads/categories"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===================== create =====================
@router.post("/create", response_model=CategoryOut)
def create_category(
    name: str = Form(...),
    slug: str = Form(...),  # اضافه شد برای سئو
    meta_title: str | None = Form(None),  # اضافه شد
    meta_description: str | None = Form(None),  # اضافه شد
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # بررسی تکراری نبودن نام
    if db.query(Category).filter(Category.name == name).first():
        raise HTTPException(
            status_code=400,
            detail={"field": "name", "message": "این نام قبلاً ثبت شده است"},
        )

    # بررسی تکراری نبودن اسلاگ (حیاتی برای سئو)
    if db.query(Category).filter(Category.slug == slug).first():
        raise HTTPException(
            status_code=400,
            detail={
                "field": "slug",
                "message": "این اسلاگ (URL) قبلاً استفاده شده است",
            },
        )

    image_url = None
    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail={"message": "فایل باید تصویر باشد"}
            )

        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())
        image_url = f"/uploads/categories/{filename}"

    last_order = db.query(func.max(Category.display_order)).scalar() or 0

    category = Category(
        application_id=current_user.application_id,
        meta_description=meta_description,
        display_order=last_order + 1,
        owner_id=current_user.id,
        meta_title=meta_title,
        image=image_url,
        name=name,
        slug=slug,
    )

    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# ===================== list me =====================
@router.get("/me", response_model=list[CategoryOut])
def get_categories(
    application_id: int | None = None,  # معمولا آیدی ها int هستند
    db: Session = Depends(get_db),
):
    if not application_id:
        raise HTTPException(
            status_code=400, detail={"message": "شناسه اپلیکیشن الزامی است"}
        )

    return (
        db.query(Category)
        .filter(Category.application_id == application_id)
        .order_by(Category.display_order.asc())
        .all()
    )


# ===================== delete =====================
@router.delete("/delete/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail={"message": "یافت نشد"})

    if category.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail={"message": "عدم دسترسی"})

    db.delete(category)
    db.commit()
    return {"message": "دسته بندی و تمام محصولات زیرمجموعه حذف شدند"}


# ===================== get category products =====================
@router.get("/{slug}")
def get_category_products(
    slug: str,
    application_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    category_query = db.query(Category).filter(Category.slug == slug)

    if application_id:
        category_query = category_query.filter(
            Category.application_id == application_id
        )

    category = category_query.first()

    if not category:
        raise HTTPException(status_code=404, detail={"message": "دسته‌بندی یافت نشد"})

    products_query = db.query(Product).filter(Product.category_id == category.id)

    if search:
        products_query = products_query.filter(Product.name.ilike(f"%{search}%"))

    total = products_query.count()

    products = (
        products_query.order_by(Product.display_order)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    last_page = (total + per_page - 1) // per_page

    return {
        "category": category,
        "products": products,
        "total": total,
        "page": page,
        "per_page": per_page,
        "last_page": last_page,
    }


# ===================== update =====================
@router.put("/update", response_model=CategoryOut)
def update_category(
    category_id: int = Form(...),
    name: str | None = Form(None),
    slug: str | None = Form(None),
    display_order: int | None = Form(None),
    meta_title: str | None = Form(None),
    meta_description: str | None = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail={"message": "یافت نشد"})

    if category.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail={"message": "عدم دسترسی"})

    if name:
        category.name = name

    if display_order:
        category.display_order = display_order

    if slug:
        # چک کردن اینکه اسلاگ جدید با اسلاگ دیگران تداخل نداشته باشد
        existing = (
            db.query(Category)
            .filter(Category.slug == slug, Category.id != category_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail={"message": "این اسلاگ قبلاً توسط دسته دیگری رزرو شده است"},
            )
        category.slug = slug

    if meta_title:
        category.meta_title = meta_title
    if meta_description:
        category.meta_description = meta_description

    if image:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())
        category.image = f"/uploads/categories/{filename}"

    db.commit()
    db.refresh(category)
    return category
