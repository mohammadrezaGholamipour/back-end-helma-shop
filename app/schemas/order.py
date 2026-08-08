from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.enums.order import OrderStatus
from app.schemas.order_item import OrderItemOut


class OrderBase(BaseModel):
    status: OrderStatus
    total_amount: Decimal
    discount_amount: Decimal
    shipping_amount: Decimal
    payable_amount: Decimal


class OrderOut(OrderBase):
    id: int
    user_id: int
    items: list[OrderItemOut] = []

    model_config = ConfigDict(
        from_attributes=True,
    )