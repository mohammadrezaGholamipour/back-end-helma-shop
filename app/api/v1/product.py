from app.schemas.product import ProductOut, CreateAndUpdateProduct
from fastapi import APIRouter, Depends, Form, UploadFile, File
from app.core.security import get_current_user
from app.models.product import Product
from app.models.category import Category
from sqlalchemy.orm import Session
from app.db.session import get_db
from fastapi import HTTPException
from app.models import User
import uuid
import os

router = APIRouter(prefix="/helma-shop-api/v1/product", tags=["Product"])


# ===================== CREATE PRODUCT =====================
@router.post("/create", response_model=ProductOut)
def create_product(
        name: str = Form(...),
        price: int = Form(...),
        volume: int = Form(...),
        description: str | None = Form(None),
        category_id: int = Form(...),
        image: UploadFile = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    UPLOAD_DIR = "uploads/products"

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.owner_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail={"field": "Category", "message": "دسته‌بندی یافت نشد یا متعلق به شما نیست"}
        )

    image_url = None

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail={"field": "Product", "message": "فایل باید تصویر باشد"}
            )

        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())

        image_url = f"/uploads/products/{filename}"

    product = Product(
        name=name,
        price=price,
        volume=volume,
        description=description,
        category_id=category_id,
        image=image_url
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# ===================== LIST (MY PRODUCTS) =====================
@router.get("/me", response_model=list[ProductOut])
def get_my_products(
        search: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        min_volume: int | None = None,
        max_volume: int | None = None,
        db: Session = Depends(get_db),
        application_id: str | None = None,
):
    if application_id is None:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "application_id",
                "message": "شناسه اپلیکیشن ارسال نشده است"
            }
        )
    query = (
        db.query(Product)
        .filter(Product.category.has(application_id=application_id))
    )

    # 🔍 search by name
    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    # 💰 price range
    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # ⚖️ volume (weight) range
    if min_volume is not None:
        query = query.filter(Product.volume >= min_volume)

    if max_volume is not None:
        query = query.filter(Product.volume <= max_volume)

    products = query.all()
    return products


# ===================== DELETE PRODUCT =====================

@router.delete("/delete")
def delete_product(
        product_id: int | None = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if product_id is None:
        raise HTTPException(
            status_code=400,
            detail={"field": "product_id", "message": "شناسه محصول ارسال نشده است"}
        )

    product = (
        db.query(Product)
        .join(Category)
        .filter(
            Product.id == product_id,
            Category.owner_id == current_user.id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail={"field": "Product", "message": "محصول یافت نشد یا متعلق به شما نیست"}
        )

    db.delete(product)
    db.commit()

    return {"message": "محصول با موفقیت حذف شد"}


# ===================== UPDATE PRODUCT =====================
@router.put("/update", response_model=ProductOut)
def update_product(
        product_id: int = Form(...),
        name: str | None = Form(None),
        price: int | None = Form(None),
        volume: int | None = Form(None),
        description: str | None = Form(None),
        category_id: int | None = Form(None),
        image: UploadFile = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    UPLOAD_DIR = "uploads/products"

    product = (
        db.query(Product)
        .join(Category)
        .filter(
            Product.id == product_id,
            Category.owner_id == current_user.id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail={"field": "Product", "message": "محصول یافت نشد یا متعلق به شما نیست"}
        )

    # If changing category, ensure it belongs to current user
    if category_id is not None and category_id != product.category_id:
        new_cat = db.query(Category).filter(
            Category.id == category_id,
            Category.owner_id == current_user.id
        ).first()
        if not new_cat:
            raise HTTPException(
                status_code=404,
                detail={"field": "Category", "message": "دسته بندی جدید یافت نشد یا متعلق به شما نیست"}
            )
        product.category_id = category_id

    if name is not None:
        product.name = name

    if price is not None:
        product.price = price

    if volume is not None:
        product.volume = volume

    if description is not None:
        product.description = description

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail={"field": "Product", "message": "فایل باید تصویر باشد"}
            )

        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())

        product.image = f"/uploads/products/{filename}"

    db.add(product)
    db.commit()
    db.refresh(product)

    return product
