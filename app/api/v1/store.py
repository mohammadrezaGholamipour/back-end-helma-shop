from fastapi import APIRouter, Depends, Form, HTTPException
from app.core.security import get_current_user
from app.schemas.store import StoreOut
from sqlalchemy.orm import Session
from app.models.store import Store
from app.db.session import get_db
from app.models.user import User

router = APIRouter(prefix="/helma-shop-api/v1/store", tags=["Store"])


# =====================
# CREATE / UPSERT STORE
# =====================


@router.post("/create", response_model=StoreOut)
def create_store(
    phone: str | None = Form(None),
    address: str | None = Form(None),
    instagram: str | None = Form(None),
    bale: str | None = Form(None),
    eita: str | None = Form(None),
    rubika: str | None = Form(None),
    telegram: str | None = Form(None),
    whatsapp: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    if store:

        update_data = {
            "phone": phone,
            "address": address,
            "instagram": instagram,
            "telegram": telegram,
            "whatsapp": whatsapp,
            "rubika": rubika,
            "eita": eita,
            "bale": bale,
        }

        for key, value in update_data.items():
            if value is not None:
                setattr(store, key, value)

    else:

        store = Store(
            owner_id=current_user.id,
            phone=phone,
            address=address,
            instagram=instagram,
            telegram=telegram,
            whatsapp=whatsapp,
            rubika=rubika,
            eita=eita,
            bale=bale,
        )

        db.add(store)

    db.commit()
    db.refresh(store)

    return store


# =====================
# UPDATE STORE
# =====================


@router.put("/update", response_model=StoreOut)
def update_store(
    instagram: str | None = Form(None),
    telegram: str | None = Form(None),
    whatsapp: str | None = Form(None),
    bale: str | None = Form(None),
    eita: str | None = Form(None),
    rubika: str | None = Form(None),
    address: str | None = Form(None),
    phone: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    if not store:
        raise HTTPException(
            status_code=404,
            detail={"field": "store", "message": "فروشگاه مورد نظر یافت نشد"},
        )

    update_data = {
        "instagram": instagram,
        "telegram": telegram,
        "whatsapp": whatsapp,
        "bale": bale,
        "eita": eita,
        "rubika": rubika,
        "address": address,
        "phone": phone,
    }

    for key, value in update_data.items():
        if value is not None:
            setattr(store, key, value)

    db.commit()
    db.refresh(store)

    return store


# =====================
# GET MY STORE
# =====================


@router.get("/me", response_model=StoreOut)
def get_my_store(
    db: Session = Depends(get_db),
):

    store = db.query(Store).first()

    if not store:
        raise HTTPException(
            status_code=404,
            detail={"field": "store", "message": "اطلاعات فروشگاه یافت نشد"},
        )

    return store
