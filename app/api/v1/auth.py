from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.schemas.user import (
    UserCreate,
    UserOut,
    TokenResponse
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole

from typing import Annotated


router = APIRouter(
    prefix="/helma-shop-api/v1/auth",
    tags=["Auth"]
)


# =====================
# REGISTER
# =====================

@router.post(
    "/register",
    response_model=UserOut
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_mobile = (
        db.query(User)
        .filter(User.mobile == user.mobile)
        .first()
    )

    if existing_mobile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "field": "mobile",
                "message": "این شماره موبایل قبلاً ثبت شده است"
            }
        )


    existing_username = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "field": "username",
                "message": "این نام کاربری قبلاً ثبت شده است"
            }
        )


    new_user = User(
        username=user.username,
        mobile=user.mobile,
        password_hash=hash_password(user.password),

        role=UserRole.CUSTOMER,
    )


    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    return new_user



# =====================
# LOGIN
# =====================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ],
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(
            User.username == form_data.username
        )
        .first()
    )


    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "field": "username or password",
                "message": "نام کاربری یا رمز عبور اشتباه است"
            }
        )


    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "field": "username or password",
                "message": "نام کاربری یا رمز عبور اشتباه است"
            }
        )


    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role.value
        }
    )


    return {
        "access_token": access_token,
        "token_type": "bearer"
    }