from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.security import get_current_user
from app.schemas.order import OrderOut
from app.models.order import Order
from app.db.session import get_db
from app.models.user import User

router = APIRouter(
    prefix="/helma-shop-api/v1/order",
    tags=["Order"],
)


# =====================
# GET MY ORDERS
# =====================

@router.get("", response_model=list[OrderOut])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.id.desc())
        .all()
    )

    return orders


# =====================
# GET MY ORDER DETAILS
# =====================

@router.get("/{order_id}", response_model=OrderOut)
def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = (
        db.query(Order)
        .options(
            joinedload(Order.items),
        )
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail={
                "field": "order",
                "message": "سفارش مورد نظر یافت نشد",
            },
        )

    return order