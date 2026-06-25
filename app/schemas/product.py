from pydantic import BaseModel, ConfigDict
from typing import Optional


class CreateAndUpdateProduct(BaseModel):
    name: str
    slug: str
    price: int
    volume: int
    description: Optional[str] = None
    image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    slug: str
    price: int
    volume: int
    description: Optional[str] = None
    image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
