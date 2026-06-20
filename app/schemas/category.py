from app.schemas.product import ProductOut
from typing import Optional, List
from pydantic import BaseModel

class CreateAndUpdateCategory(BaseModel):
    name: str
    image: Optional[str] = None

class CategoryOut(BaseModel):
    id: int
    image: Optional[str] = None
    name: str
    products: List[ProductOut] = []
    model_config = {
        "from_attributes": True
    }

