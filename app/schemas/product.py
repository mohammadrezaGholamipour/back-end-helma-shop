from pydantic import BaseModel, ConfigDict
from typing import Optional, List


# اسکیمای ایجاد و آپدیت محصول
class CreateAndUpdateProduct(BaseModel):
    name: str
    slug: str
    category_id: int # اضافه کردن این مورد ضروری است چون در مدل دیتابیس اجباری است
    description: Optional[str] = None
    image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    
    # لیست وریانت‌هایی که باید همراه محصول ساخته شوند
    variants: List[ProductVariantCreate]

# اسکیمای نمایش محصول در خروجی (مثلاً در لیست محصولات یا صفحه جزئیات)
class ProductOut(BaseModel):
    id: int
    category_id: int
    name: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    
    # نمایش لیستی از تمام وزن‌ها و قیمت‌های این محصول
    variants: List[ProductVariantOut]

    model_config = ConfigDict(from_attributes=True)

# اسکیمای پایه برای وریانت
class ProductVariantBase(BaseModel):
    volume: int
    price: int
    stock: int = 0
    image: Optional[str] = None

# برای ایجاد وریانت (درون ایجاد محصول استفاده می‌شود)
class ProductVariantCreate(ProductVariantBase):
    pass

# برای نمایش وریانت در خروجی API
class ProductVariantOut(ProductVariantBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


