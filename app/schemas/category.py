from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# =====================================================
# CREATE / UPDATE
# =====================================================

class CreateAndUpdateCategory(BaseModel):
    name: str

    slug: str

    image: Optional[str] = None

    display_order: Optional[int] = None

    meta_title: Optional[str] = None

    meta_description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# CATEGORY OUTPUT
# =====================================================

class CategoryOut(BaseModel):
    id: int

    name: str

    slug: str

    image: Optional[str] = None

    display_order: int

    meta_title: Optional[str] = None

    meta_description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# PRODUCTS INSIDE CATEGORY
# =====================================================

class ProductInCategory(BaseModel):
    id: int

    name: str

    slug: str

    image: Optional[str] = None

    description: Optional[str] = None

    meta_title: Optional[str] = None

    meta_description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# CATEGORY PRODUCTS PAGINATION
# =====================================================

class CategoryProductsResponse(BaseModel):
    category: CategoryOut

    products: List[ProductInCategory]

    total: int

    page: int

    per_page: int

    last_page: int

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# DRAG & DROP ORDER
# =====================================================

class CategoryOrderItem(BaseModel):
    id: int

    display_order: int