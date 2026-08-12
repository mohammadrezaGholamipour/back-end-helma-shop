from app.core.security import get_current_user, get_current_admin
from sqlalchemy.orm import Session, selectinload
from app.schemas.user import UserOut, UserListOut
from app.models.order_item import OrderItem
from app.models.product import Product
from fastapi import APIRouter, Depends
from app.models.order import Order
from app.db.session import get_db
from app.models.user import User
from typing import List



router = APIRouter(
    prefix="/helma-shop-api/v1/user",
    tags=["User"],
)


@router.get(
    "/me",
    response_model=UserOut,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get(
    "/list",
    response_model=List[UserListOut],
    dependencies=[Depends(get_current_admin)],
)
def list_users(db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .options(
            selectinload(User.customer_profile),
            selectinload(User.orders)
            .selectinload(Order.items)
            .selectinload(OrderItem.product)
            .selectinload(Product.variants),
        )
        .order_by(User.id.desc())
        .all()
    )

    return users