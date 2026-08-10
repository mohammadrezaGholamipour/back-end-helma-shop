from app.schemas.order_item import (OrderItemCreate,OrderItemOut)
from pydantic import BaseModel, ConfigDict, Field
from app.enums.order import OrderStatus
from decimal import Decimal


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(
        min_length=1,
    )


class OrderBase(BaseModel):
    status: OrderStatus

    total_amount: Decimal
    discount_amount: Decimal
    shipping_amount: Decimal
    payable_amount: Decimal

    receiver_first_name: str
    receiver_last_name: str
    receiver_mobile: str
    receiver_address: str
    receiver_postal_code: str | None = None

    receiver_latitude: Decimal | None = None
    receiver_longitude: Decimal | None = None


class OrderOut(OrderBase):
    id: int
    user_id: int

    items: list[OrderItemOut] = Field(
        default_factory=list,
    )

    model_config = ConfigDict(
        from_attributes=True,
    )