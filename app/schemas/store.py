from typing import Optional

from pydantic import BaseModel, ConfigDict


# =====================================================
# CREATE / UPDATE STORE
# =====================================================

class CreateAndUpdateStore(BaseModel):
    instagram: Optional[str] = None
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None

    bale: Optional[str] = None
    eita: Optional[str] = None
    rubika: Optional[str] = None

    address: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# STORE OUTPUT
# =====================================================

class StoreOut(BaseModel):
    id: int

    instagram: Optional[str] = None
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None

    bale: Optional[str] = None
    eita: Optional[str] = None
    rubika: Optional[str] = None

    address: Optional[str] = None
    phone: Optional[str] = None


    model_config = ConfigDict(
        from_attributes=True
    )