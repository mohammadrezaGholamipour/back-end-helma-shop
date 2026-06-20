from fastapi import APIRouter, Depends, status, HTTPException, Path
from app.core.security import get_current_user
from app.schemas.user import UserOut
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User

router = APIRouter(prefix="/helma-shop-api/v1/user", tags=["User"], dependencies=[Depends(get_current_user)])


# ===================== list =====================
@router.get("/me", response_model=UserOut)
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = (
        db.query(User)
        .filter(User.id == current_user.id)
        .first()
    )
    return user
