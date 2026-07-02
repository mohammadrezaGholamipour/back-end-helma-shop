from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Query
from app.core.security import get_current_user
from app.services.eitaa import send_product
from app.schemas.product import ProductOut
from app.models.category import Category
from app.models.product import Product
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
import uuid
import os

router = APIRouter(prefix="/helma-shop-api/v1/product", tags=["Product"])

UPLOAD_DIR = "uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ===================== CREATE PRODUCT =====================
@router.post("/create", response_model=ProductOut)
def create_product(
    background_tasks: BackgroundTasks = None,
    name: str = Form(...),
    slug: str = Form(...), # اضافه شده برای سئو
    price: int = Form(...),
    volume: int = Form(...),
    description: str | None = Form(None),
    meta_title: str | None = Form(None), # اضافه شده
    meta_description: str | None = Form(None), # اضافه شده
    category_id: int = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # بررسی دسترسی به دسته‌بندی
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.owner_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail={"message": "دسته‌بندی یافت نشد"})

    # بررسی تکراری نبودن اسلاگ محصول
    if db.query(Product).filter(Product.slug == slug).first():
        raise HTTPException(status_code=400, detail={"message": "این اسلاگ (URL) قبلاً برای محصول دیگری ثبت شده است"})

    image_url = None
    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail={"message": "فایل باید تصویر باشد"})
        
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())
        image_url = f"/uploads/products/{filename}"

    product = Product(
        name=name,
        slug=slug,
        price=price,
        volume=volume,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        category_id=category_id,
        image=image_url
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    if product.image:
        caption = f"""
📦 {product.name}

💰 قیمت:
{product.price:,} تومان

⚖️ وزن:
{product.volume} گرم
"""

        background_tasks.add_task(
            send_product,
            product.image.lstrip("/"),
            product.name,
            caption,
        )

    return product

# ===================== LIST (MY PRODUCTS) =====================
@router.get("/me", response_model=list[ProductOut])
def get_my_products(
    application_id: str = Query(...), # اجباری کردن پارامتر
    search: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    db: Session = Depends(get_db)
):
    # استفاده از Join برای کوئری دقیق‌تر بر اساس اپلیکیشن
    query = db.query(Product).join(Category).filter(Category.application_id == application_id)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    return query.all()

# ===================== DELETE PRODUCT =====================
@router.delete("/delete/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).join(Category).filter(
        Product.id == product_id,
        Category.owner_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail={"message": "محصول یافت نشد"})

    db.delete(product)
    db.commit()
    return {"message": "محصول با موفقیت حذف شد"}

# ===================== UPDATE PRODUCT =====================
@router.put("/update", response_model=ProductOut)
def update_product(
    product_id: int = Form(...),
    name: str | None = Form(None),
    slug: str | None = Form(None), # اضافه شده
    price: int | None = Form(None),
    volume: int | None = Form(None),
    description: str | None = Form(None),
    meta_title: str | None = Form(None),
    meta_description: str | None = Form(None),
    category_id: int | None = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).join(Category).filter(
        Product.id == product_id,
        Category.owner_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail={"message": "محصول یافت نشد"})

    if category_id:
        # چک کردن مالکیت دسته‌بندی جدید
        new_cat = db.query(Category).filter(Category.id == category_id, Category.owner_id == current_user.id).first()
        if not new_cat:
            raise HTTPException(status_code=400, detail={"message": "دسته بندی نامعتبر"})
        product.category_id = category_id

    if slug:
        # چک کردن تکراری نبودن اسلاگ جدید
        existing = db.query(Product).filter(Product.slug == slug, Product.id != product_id).first()
        if existing:
            raise HTTPException(status_code=400, detail={"message": "این اسلاگ قبلاً ثبت شده است"})
        product.slug = slug

    if name: product.name = name
    if price: product.price = price
    if volume: product.volume = volume
    if description: product.description = description
    if meta_title: product.meta_title = meta_title
    if meta_description: product.meta_description = meta_description

    if image:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())
        product.image = f"/uploads/products/{filename}"

    db.commit()
    db.refresh(product)
    return product
