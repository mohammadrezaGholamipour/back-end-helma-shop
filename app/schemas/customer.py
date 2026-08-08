from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerProfileBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None


class CustomerProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


class CustomerProfileOut(CustomerProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )