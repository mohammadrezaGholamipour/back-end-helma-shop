from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# ===================== وریانت (Variant) =====================

class ProductVariantBase(BaseModel):
    volume: int
    price: int
    stock: int = 0

class ProductVariantOut(ProductVariantBase):
    id: int
    product_id: int
    image: Optional[str] = None # آدرس تصویر در خروجی

    model_config = ConfigDict(from_attributes=True)

# ===================== محصول (Product) =====================

class CreateAndUpdateProduct(BaseModel):
    name: str
    slug: str
    category_id: int
    description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    category_id: int
    name: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    
    # نمایش لیستی از وریانت‌ها در خروجی محصول
    variants: List[ProductVariantOut] = []

    model_config = ConfigDict(from_attributes=True)
