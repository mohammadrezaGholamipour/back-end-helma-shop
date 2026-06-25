from app.schemas.pagination import PaginationMeta
from app.schemas.category import CategoryOut
from pydantic import BaseModel, ConfigDict
from app.schemas.product import ProductOut
from app.schemas.product import ProductOut
from typing import Optional, List
from pydantic import Field

class CreateAndUpdateCategory(BaseModel):
    name: str
    slug: str
    image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    image: Optional[str] = None
    name: str
    slug: str
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



class CategoryWithProductsOut(BaseModel):
    id: int
    image: Optional[str] = None
    name: str
    slug: str
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    products: List[ProductOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
    
    


class CategoryProductsResponse(BaseModel):
    category: CategoryOut
    products: List[ProductOut]
    meta: PaginationMeta