from fastapi import (
    APIRouter,
    Depends,
    Form,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks,
    status,
)

from sqlalchemy.orm import Session

from app.services.social_manager import notify_new_product
from app.models.product_variant import ProductVariant
from app.schemas.product import ProductVariantOut
from app.core.security import get_current_admin
from app.models.product import Product
from app.models.user import User
from app.db.session import get_db

import uuid
import os

router = APIRouter(
    prefix="/helma-shop-api/v1/variant",
    tags=["Product Variant"],
)


UPLOAD_DIR = "uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_image(image: UploadFile | None):

    if not image:
        return None

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail={"message": "فایل باید تصویر باشد"},
        )

    ext = os.path.splitext(image.filename)[1]

    filename = f"var_{uuid.uuid4().hex}{ext}"

    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(image.file.read())

    return f"/uploads/products/{filename}"


# =====================================================
# CREATE VARIANT
# =====================================================


@router.post(
    "/{product_id}",
    response_model=ProductVariantOut,
)
async def create_variant(
    product_id: int,
    background_tasks: BackgroundTasks,
    volume: int = Form(...),
    price: int = Form(...),
    stock: int = Form(0),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):

    product = (
        db.query(Product)
        .join(Product.category)
        .filter(
            Product.id == product_id, Product.category.has(owner_id=current_user.id)
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail={"message": "محصول یافت نشد"},
        )

    exists = (
        db.query(ProductVariant)
        .filter(
            ProductVariant.product_id == product_id,
            ProductVariant.volume == volume,
        )
        .first()
    )

    if exists:
        raise HTTPException(
            status_code=400,
            detail={"message": "این وزن قبلاً ثبت شده است"},
        )

    image_url = save_image(image)

    variant = ProductVariant(
        product_id=product_id,
        volume=volume,
        price=price,
        stock=stock,
        image=image_url,
    )

    db.add(variant)
    db.commit()
    db.refresh(variant)

    background_tasks.add_task(
        notify_new_product,
        product.image,
        product.name,
        price,
        volume,
    )

    return variant


# =====================================================
# UPDATE VARIANT
# =====================================================


@router.patch(
    "/{variant_id}",
    response_model=ProductVariantOut,
)
async def update_variant(
    variant_id: int,
    volume: int | None = Form(None),
    price: int | None = Form(None),
    stock: int | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):

    variant = (
        db.query(ProductVariant)
        .join(Product)
        .join(Product.category)
        .filter(
            ProductVariant.id == variant_id,
            Product.category.has(owner_id=current_user.id),
        )
        .first()
    )

    if not variant:
        raise HTTPException(
            status_code=404,
            detail={"message": "وریانت یافت نشد"},
        )

    if volume is not None:
        exists = (
            db.query(ProductVariant)
            .filter(
                ProductVariant.product_id == variant.product_id,
                ProductVariant.volume == volume,
                ProductVariant.id != variant_id,
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=400,
                detail={"message": "این وزن قبلاً برای این محصول ثبت شده است"},
            )

        variant.volume = volume

    if price is not None:
        variant.price = price

    if stock is not None:
        variant.stock = stock

    if image:

        variant.image = save_image(image)

    db.commit()
    db.refresh(variant)

    return variant


# =====================================================
# DELETE VARIANT
# =====================================================


@router.delete(
    "/{variant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):

    variant = (
        db.query(ProductVariant)
        .join(Product)
        .join(Product.category)
        .filter(
            ProductVariant.id == variant_id,
            Product.category.has(owner_id=current_user.id),
        )
        .first()
    )

    if not variant:
        raise HTTPException(
            status_code=404,
            detail={"message": "وریانت یافت نشد"},
        )

    db.delete(variant)
    db.commit()

    return None
