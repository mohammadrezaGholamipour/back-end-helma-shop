from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate, UserOut, TokenResponse
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from typing import Annotated

router = APIRouter(prefix="/helma-shop-api/v1/auth", tags=["Auth"])


# ===================== REGISTER =====================

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if user.mobile:
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

    last_user = (
        db.query(User)
        .order_by(User.application_id.desc())
        .first()
    )

    next_application_id = (
            (last_user.application_id if last_user and last_user.application_id else 0) + 1
    )

    new_user = User(
        password=hash_password(user.password),
        application_id=next_application_id,
        userName=user.userName,
        mobile=user.mobile,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ===================== LOGIN =====================
@router.post("/login", response_model=TokenResponse)
def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.userName == form_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"field": "email or password", "message": "نام کاربری یا رمز عبور اشتباه است"}
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"field": "email or password", "message": "نام کاربری یا رمز عبور اشتباه است"}
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
