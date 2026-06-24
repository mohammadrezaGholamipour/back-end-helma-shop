from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from app.schemas.store import CreateAndUpdateStore, StoreOut
from app.core.security import get_current_user
from sqlalchemy.orm import Session
from app.models.store import Store
from app.db.session import get_db
from app.models.user import User
import uuid
import os

router = APIRouter(prefix="/helma-shop-api/v1/store", tags=["Store"])


# ===================== CREATE / UPDATE STORE =====================

@router.post("/create", response_model=StoreOut)
def create_or_update_store(
        phone: str = Form(None),
        address: str = Form(None),
        instagram: str = Form(None),
        bale: str = Form(None),
        eita: str = Form(None),
        rubika: str = Form(None),
        telegram: str = Form(None),
        whatsapp: str = Form(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):

    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    if store:
        update_data = {
            "phone": phone,
            "address": address,
            "instagram": instagram,
            "telegram": telegram,
            "whatsapp": whatsapp,
            "whatsapp": whatsapp,
            "rubika": rubika,
            "eita": eita,
            "bale": bale,
        }

        for key, value in update_data.items():
            if value is not None:
                setattr(store, key, value)

        if logo_url:
            store.logo = logo_url
    else:

        store = Store(
            application_id=current_user.application_id,
            owner_id=current_user.id,
            instagram=instagram,
            telegram=telegram,
            whatsapp=whatsapp,
            address=address,
            rubika=rubika,
            phone=phone,
            eita=eita,
            bale=bale,

        )
        db.add(store)

    db.commit()
    db.refresh(store)

    return store


# ===================== Get =====================

@router.get("/me", response_model=StoreOut)
def get_my_store(
        application_id: str | None = None,
        db: Session = Depends(get_db),

):
    if application_id is None:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "application_id",
                "message": "شناسه اپلیکیشن ارسال نشده است"
            }
        )

    store = db.query(Store).filter(Store.application_id == application_id).first()

    if not store:
        raise HTTPException(
            status_code=404,
            detail={"field": "store", "message": "اطلاعات فروشگاه یافت نشد"}
        )

    return store
