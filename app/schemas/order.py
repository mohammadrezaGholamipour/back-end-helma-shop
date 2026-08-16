from app.schemas.order_item import OrderItemCreate, OrderItemOut
from pydantic import BaseModel, ConfigDict, Field
from app.enums.order import OrderStatus
from decimal import Decimal


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# اطلاعات مینیمال کاربر برای نمایش در پنل ادمین
class OrderUserOut(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    mobile: str

    model_config = ConfigDict(from_attributes=True)


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


class OrderOut(OrderBase):
    id: int
    user_id: int
    user: OrderUserOut | None = None

    items: list[OrderItemOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)