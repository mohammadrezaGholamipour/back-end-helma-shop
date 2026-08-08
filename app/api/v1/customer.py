from app.schemas.customer import CustomerProfileOut, CustomerProfileUpdate
from app.models.customer_profile import CustomerProfile
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User

router = APIRouter(
    prefix="/helma-shop-api/v1/customer",
    tags=["Customer"],
)


# =====================
# GET MY PROFILE
# =====================


@router.get(
    "/profile",
    response_model=CustomerProfileOut,
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = (
        db.query(CustomerProfile)
        .filter(CustomerProfile.user_id == current_user.id)
        .first()
    )

    if not profile:
        profile = CustomerProfile(
            user_id=current_user.id,
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile


# =====================
# UPDATE MY PROFILE
# =====================


@router.put(
    "/profile",
    response_model=CustomerProfileOut,
)
def update_my_profile(
    data: CustomerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = (
        db.query(CustomerProfile)
        .filter(CustomerProfile.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={
                "field": "profile",
                "message": "اطلاعات کاربری یافت نشد",
            },
        )

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return profile
