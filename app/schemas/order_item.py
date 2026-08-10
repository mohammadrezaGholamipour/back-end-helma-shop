from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderItemOut(BaseModel):
    id: int
    order_id: int

    product_id: int | None = None
    product_name: str

    quantity: int
    unit_price: Decimal
    total_price: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )
