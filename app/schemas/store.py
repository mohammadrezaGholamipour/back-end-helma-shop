from pydantic import BaseModel
from typing import Optional


class CreateAndUpdateStore(BaseModel):
    instagram: Optional[str] = None
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None
    bale: Optional[str] = None
    eita: Optional[str] = None
    rubika: Optional[str] = None
    address: str
    phone: str


class StoreOut(BaseModel):
    instagram: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    bale: Optional[str] = None
    eita: Optional[str] = None
    rubika: Optional[str] = None
    address: str
    phone: str
    id: int

    model_config = {"from_attributes": True}
