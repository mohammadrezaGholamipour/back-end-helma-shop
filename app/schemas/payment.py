from pydantic import BaseModel


class PaymentRequestOut(BaseModel):
    payment_id: int
    authority: str
    payment_url: str

    class Config:
        from_attributes = True


class PaymentOut(BaseModel):
    id: int
    order_id: int
    amount: float
    status: str
    ref_id: str | None = None
    card_pan: str | None = None

    class Config:
        from_attributes = True