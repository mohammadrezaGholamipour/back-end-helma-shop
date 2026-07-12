from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Query
from app.services.social_manager import notify_new_product
from app.models.product_variant import ProductVariant
from app.core.security import get_current_user
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
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    slug: str = Form(...),
    category_id: int = Form(...),
    description: str | None = Form(None),
    meta_title: str | None = Form(None),
    meta_description: str | None = Form(None),

    # وریانت‌ها به صورت JSON string داخل فرم
    variants_json: str = Form(...),

    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # مالکیت دسته‌بندی
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.owner_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail={"message": "دسته‌بندی یافت نشد"})

    # اسلاگ یونیک
    if db.query(Product).filter(Product.slug == slug).first():
        raise HTTPException(status_code=400, detail={"message": "این اسلاگ قبلاً ثبت شده است"})

    # parse variants
    try:
        variants_data = json.loads(variants_json)
        if not isinstance(variants_data, list) or len(variants_data) == 0:
            raise ValueError()
    except Exception:
        raise HTTPException(status_code=422, detail={"message": "variants_json نامعتبر است (باید لیست JSON باشد)"})

    # اعتبارسنجی ساده و جلوگیری از حجم تکراری
    seen_volumes = set()
    for v in variants_data:
        vol = int(v.get("volume"))
        price = int(v.get("price"))
        stock = int(v.get("stock", 0))
        if vol <= 0 or price < 0 or stock < 0:
            raise HTTPException(status_code=422, detail={"message": "مقادیر volume/price/stock نامعتبر است"})
        if vol in seen_volumes:
            raise HTTPException(status_code=422, detail={"message": "volume تکراری در variants مجاز نیست"})
        seen_volumes.add(vol)

    # upload product image
    image_url = None
    if image:
        if not image.content_type or not image.content_type.startswith("image/"):
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
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        category_id=category_id,
        image=image_url,
    )

    # ساخت وریانت‌ها
    for v in variants_data:
        product.variants.append(ProductVariant(
            volume=int(v["volume"]),
            price=int(v["price"]),
            stock=int(v.get("stock", 0)),
            image=v.get("image"),  # اگر خواستی بعداً برای هر وریانت تصویر مستقل هم بگیری
        ))

    db.add(product)
    db.commit()
    db.refresh(product)

    # برای نوتیف، مثلاً کمترین قیمت و اولین حجم
    min_variant = min(product.variants, key=lambda x: x.price)
    background_tasks.add_task(
        notify_new_product,
        product.image,
        product.name,
        min_variant.price,
        min_variant.volume
    )

    return product

# ===================== LIST (MY PRODUCTS) =====================
@router.get("/me", response_model=list[ProductOut])
def get_my_products(
    application_id: str = Query(...),
    search: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Product)
        .join(Category)
        .filter(Category.application_id == application_id)
    )

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    # فیلتر قیمت بر اساس وریانت‌ها
    if min_price is not None or max_price is not None:
        query = query.join(ProductVariant)

        if min_price is not None:
            query = query.filter(ProductVariant.price >= min_price)
        if max_price is not None:
            query = query.filter(ProductVariant.price <= max_price)

        query = query.distinct()

    return query.all()


# ===================== UPDATE PRODUCT =====================
@router.put("/update", response_model=ProductOut)
def update_product(
    product_id: int = Form(...),
    name: str | None = Form(None),
    slug: str | None = Form(None),
    description: str | None = Form(None),
    meta_title: str | None = Form(None),
    meta_description: str | None = Form(None),
    category_id: int | None = Form(None),

    variants_json: str | None = Form(None),  # اختیاری: اگر ارسال شد وریانت‌ها را جایگزین می‌کنیم

    image: UploadFile | None = File(None),
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
        new_cat = db.query(Category).filter(
            Category.id == category_id,
            Category.owner_id == current_user.id
        ).first()
        if not new_cat:
            raise HTTPException(status_code=400, detail={"message": "دسته بندی نامعتبر"})
        product.category_id = category_id

    if slug:
        existing = db.query(Product).filter(Product.slug == slug, Product.id != product_id).first()
        if existing:
            raise HTTPException(status_code=400, detail={"message": "این اسلاگ قبلاً ثبت شده است"})
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
            raise HTTPException(status_code=400, detail={"message": "فایل باید تصویر باشد"})
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())
        product.image = f"/uploads/products/{filename}"

    # اگر variants_json آمد: کل variants را replace کن
    if variants_json is not None:
        try:
            variants_data = json.loads(variants_json)
            if not isinstance(variants_data, list) or len(variants_data) == 0:
                raise ValueError()
        except Exception:
            raise HTTPException(status_code=422, detail={"message": "variants_json نامعتبر است"})

        # پاک کردن وریانت‌های قبلی (به خاطر delete-orphan)
        product.variants.clear()

        seen_volumes = set()
        for v in variants_data:
            vol = int(v.get("volume"))
            price = int(v.get("price"))
            stock = int(v.get("stock", 0))
            if vol <= 0 or price < 0 or stock < 0:
                raise HTTPException(status_code=422, detail={"message": "مقادیر volume/price/stock نامعتبر است"})
            if vol in seen_volumes:
                raise HTTPException(status_code=422, detail={"message": "volume تکراری در variants مجاز نیست"})
            seen_volumes.add(vol)

            product.variants.append(ProductVariant(
                volume=vol,
                price=price,
                stock=stock,
                image=v.get("image"),
            ))

    db.commit()
    db.refresh(product)
    return product

# ===================== Delete PRODUCT =====================

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