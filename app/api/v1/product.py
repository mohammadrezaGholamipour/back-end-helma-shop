from fastapi import (
    APIRouter,
    Depends,
    Form,
    UploadFile,
    File,
    HTTPException,
    Query,
    status,
)
from app.enums.product import ProductType, ProductModel, OilType
from app.schemas.product import ProductOut, ProductVariantOut
from app.models.product_variant import ProductVariant
from app.core.security import get_current_user
from app.models.category import Category
from app.models.product import Product
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from typing import List
import uuid
import os

router = APIRouter(prefix="/helma-shop-api/v1/product", tags=["Product"])

UPLOAD_DIR = "uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===================== CREATE PRODUCT =====================
@router.post("/create", response_model=ProductOut)
async def create_product(
    name: str = Form(...),
    slug: str = Form(...),
    category_id: int = Form(...),
    description: str | None = Form(None),
    meta_title: str | None = Form(None),
    meta_description: str | None = Form(None),
    product_type: ProductType | None = Form(None),
    product_model: ProductModel | None = Form(None),
    oil_type: OilType | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    is_packaged: bool | None = Form(None),
    current_user: User = Depends(get_current_user),
):
    # چک کردن تکراری نبودن اسلاگ
    if db.query(Product).filter(Product.slug == slug).first():
        raise HTTPException(status_code=400, detail="این اسلاگ قبلاً ثبت شده است")

    image_url = None
    if image:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())
        image_url = f"/uploads/products/{filename}"

    last_order = (
        db.query(func.max(Product.display_order))
        .filter(Product.category_id == category_id)
        .scalar()
    ) or 0

    product = Product(
        name=name,
        slug=slug,
        category_id=category_id,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        display_order=last_order + 1,
        product_type=product_type,
        product_model=product_model,
        oil_type=oil_type,
        is_packaged=is_packaged,
        image=image_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# ===================== list PRODUCT =====================
@router.get("/me", response_model=list[ProductOut])
def get_my_products(
    application_id: str = Query(...),
    search: str | None = Query(None),

    min_price: int | None = Query(None, ge=0),
    max_price: int | None = Query(None, ge=0),

    product_type: ProductType | None = Query(None),
    product_model: ProductModel | None = Query(None),
    oil_type: OilType | None = Query(None),

    db: Session = Depends(get_db),
):
    query = (
        db.query(Product)
        .join(Category)
        .filter(Category.application_id == application_id)
    )

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if product_type:
        query = query.filter(Product.product_type == product_type)

    if product_model:
        query = query.filter(Product.product_model == product_model)

    if oil_type:
        query = query.filter(Product.oil_type == oil_type)

    if min_price is not None or max_price is not None:
        query = query.join(ProductVariant)

        if min_price is not None:
            query = query.filter(ProductVariant.price >= min_price)

        if max_price is not None:
            query = query.filter(ProductVariant.price <= max_price)

        query = query.distinct()

    return query.order_by(Product.display_order).all()
# ===================== GET PRODUCT BY SLUG =====================
@router.get("/{slug}", response_model=ProductOut)
def get_product_by_slug(
    slug: str,
    application_id: str = Query(...),
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .options(
            joinedload(Product.variants),
            joinedload(Product.category),
        )
        .join(Category)
        .filter(
            Product.slug == slug,
            Category.application_id == application_id,
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail={"message": "محصول یافت نشد"},
        )

    return product


# ===================== UPDATE PRODUCT =====================
@router.put("/update", response_model=ProductOut)
def update_product(
    product_id: int = Form(...),
    name: str | None = Form(None),
    slug: str | None = Form(None),
    description: str | None = Form(None),
    meta_title: str | None = Form(None),
    meta_description: str | None = Form(None),
    product_type: ProductType | None = Form(None),
    product_model: ProductModel | None = Form(None),
    oil_type: OilType | None = Form(None),
    category_id: int | None = Form(None),
    display_order: int | None = Form(None),
    image: UploadFile | None = File(None),
    is_packaged: bool | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = (
        db.query(Product)
        .join(Category)
        .filter(Product.id == product_id, Category.owner_id == current_user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail={"message": "محصول یافت نشد"})

    if category_id is not None:
        new_cat = (
            db.query(Category)
            .filter(Category.id == category_id, Category.owner_id == current_user.id)
            .first()
        )
        if not new_cat:
            raise HTTPException(
                status_code=400, detail={"message": "دسته بندی نامعتبر"}
            )
        product.category_id = category_id

    if display_order is not None:
        product.display_order = display_order

    if product_type is not None:
        product.product_type = product_type

    if product_model is not None:
        product.product_model = product_model

    if oil_type is not None:
        product.oil_type = oil_type
        
    if is_packaged is not None:
        product.is_packaged = is_packaged
    
    if slug:
        existing = (
            db.query(Product)
            .filter(Product.slug == slug, Product.id != product_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail={"message": "این اسلاگ قبلاً ثبت شده است"}
            )
        product.slug = slug

    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if meta_title is not None:
        product.meta_title = meta_title
    if meta_description is not None:
        product.meta_description = meta_description

    if image:
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail={"message": "فایل باید تصویر باشد"}
            )
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())
        product.image = f"/uploads/products/{filename}"

    db.commit()
    db.refresh(product)
    return product


# ===================== Delete PRODUCT =====================


@router.delete("/delete/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = (
        db.query(Product)
        .join(Category)
        .filter(Product.id == product_id, Category.owner_id == current_user.id)
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail={"message": "محصول یافت نشد"})

    db.delete(product)
    db.commit()
    return {"message": "محصول با موفقیت حذف شد"}
