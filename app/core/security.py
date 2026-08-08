from fastapi.security import OAuth2PasswordBearer
from app.models.user import User, UserRole
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.core.config import settings
from sqlalchemy.orm import Session
from fastapi.params import Depends
from app.db.session import get_db
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/helma-shop-api/v1/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str | None = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "کاربر مورد نظر پیدا نشد"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "لطفا ابتدا احراز هویت خود را انجام دهید"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "کاربر مورد نظر پیدا نشد"},
        )
    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "شما دسترسی لازم برای انجام این عملیات را ندارید"},
        )

    return current_user


# هش کردن پسورد
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# بررسی پسورد
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ساخت access token
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt
