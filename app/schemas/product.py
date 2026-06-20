from pydantic import BaseModel
from typing import Optional


class CreateAndUpdateProduct(BaseModel):
    name: str
    price: int
    volume: int
    description: Optional[str] = None
    image: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    price: int
    volume: int
    description: Optional[str] = None
    image: Optional[str] = None
    model_config = {
        "from_attributes": True
    }

