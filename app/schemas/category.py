from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class CreateAndUpdateCategory(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[str] = None

    slug: str
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    application_id: Optional[int] = None

    slug: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductInCategory(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None

    slug: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryProductsResponse(BaseModel):
    category: CategoryOut
    products: List[ProductInCategory]
    total: int
    page: int
    per_page: int
    last_page: int
