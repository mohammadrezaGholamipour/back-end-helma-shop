from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)


class ProductVariantBase(BaseModel):
    volume: int
    price: int
    stock: int = 0


class ProductVariantOut(ProductVariantBase):
    id: int
    product_id: int
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductOut(BaseModel):
    id: int
    category_id: int
    name: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    category: Optional[CategoryOut] = None
    variants: List[ProductVariantOut] = []

    model_config = ConfigDict(from_attributes=True)
