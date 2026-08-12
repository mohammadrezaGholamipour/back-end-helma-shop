from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.security import get_current_user, get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.models.order import Order
from app.schemas.user import UserOut, UserListOut

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
    orders_count_subq = (
        select(Order.user_id, func.count(Order.id).label("orders_count"))
        .group_by(Order.user_id)
        .subquery()
    )

    rows = (
        db.query(User, orders_count_subq.c.orders_count)
        .outerjoin(
            orders_count_subq,
            User.id == orders_count_subq.c.user_id,
        )
        .options(selectinload(User.customer_profile))
        .order_by(User.id.desc())
        .all()
    )

    result: List[UserListOut] = []
    for user, orders_count in rows:
        item = UserListOut.model_validate(user)
        item.orders_count = orders_count or 0
        result.append(item)

    return result