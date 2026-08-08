
from app.core.security import get_current_user
from fastapi import APIRouter, Depends
from app.schemas.user import UserOut
from app.models.user import User

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
