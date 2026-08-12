from pydantic import BaseModel, ConfigDict, EmailStr
from decimal import Decimal


class CustomerProfileBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    address: str | None = None
    postal_code: str | None = None


class CustomerProfileUpdate(CustomerProfileBase):
    pass


class CustomerProfileOut(CustomerProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )