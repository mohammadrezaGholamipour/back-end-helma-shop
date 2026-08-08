from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerProfileBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None


class CustomerProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None


class CustomerProfileOut(CustomerProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )