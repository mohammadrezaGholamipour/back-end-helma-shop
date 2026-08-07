from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.enums.product import (
    ProductType,
    ProductModel,
    OilType,
)


# =====================================================
# PRODUCT VARIANT
# =====================================================

class ProductVariantBase(BaseModel):
    volume: int
    price: int
    stock: int = 0

    model_config = ConfigDict(
        from_attributes=True
    )


class ProductVariantOut(ProductVariantBase):
    id: int

    product_id: int

    image: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# PRODUCT
# =====================================================

class ProductOut(BaseModel):
    id: int

    category_id: int

    name: str

    slug: str

    description: Optional[str] = None


    # بسته بندی
    is_packaged: bool = True


    display_order: int


    # Enum ها
    product_type: Optional[ProductType] = None

    product_model: Optional[ProductModel] = None

    oil_type: Optional[OilType] = None


    image: Optional[str] = None


    meta_title: Optional[str] = None

    meta_description: Optional[str] = None


    # روابط
    category: Optional["CategoryOut"] = None

    variants: List[ProductVariantOut] = Field(
        default_factory=list
    )


    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )