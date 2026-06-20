from pydantic import BaseModel
from typing import Optional


class CreateAndUpdateStore(BaseModel):
    instagram: Optional[str] = None
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None
    address: str
    phone: str
    name: str
    logo: str


class StoreOut(BaseModel):
    instagram: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    logo: str | None
    address: str
    phone: str
    name: str
    id: int

    model_config = {"from_attributes": True}
