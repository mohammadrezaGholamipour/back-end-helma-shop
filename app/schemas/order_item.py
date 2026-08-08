from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OrderItemOut(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )