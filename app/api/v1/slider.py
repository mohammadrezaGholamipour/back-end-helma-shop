import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.slider import Slider
from app.models.user import User
from app.schemas.slider import SliderOut
from app.core.security import get_current_admin

router = APIRouter(
    prefix="/helma-shop-api/v1/slider",
    tags=["Slider"],
)


UPLOAD_DIR = "uploads/sliders"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =====================================================
# CREATE SLIDER
# =====================================================


@router.post(
    "/create",
    response_model=SliderOut,
)
def create_slider(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    # بررسی نوع فایل
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail={
                "message": "فایل باید تصویر باشد",
            },
        )

    # پسوند فایل
    ext = os.path.splitext(image.filename or "")[1]

    if not ext:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "فایل تصویر دارای پسوند معتبر نیست",
            },
        )

    # نام یکتا
    filename = f"{uuid.uuid4().hex}{ext}"

    path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    # ذخیره فایل
    with open(path, "wb") as buffer:
        buffer.write(image.file.read())

    image_url = f"/uploads/sliders/{filename}"

    # آخرین ترتیب Slider
    last_order = (
        db.query(func.max(Slider.display_order))
        .filter(
            Slider.owner_id == current_user.id,
        )
        .scalar()
        or 0
    )

    slider = Slider(
        owner_id=current_user.id,
        image=image_url,
        display_order=last_order + 1,
    )

    db.add(slider)
    db.commit()
    db.refresh(slider)

    return slider


# =====================================================
# GET ALL SLIDERS
# =====================================================


@router.get(
    "/list",
    response_model=list[SliderOut],
)
def get_sliders(
    db: Session = Depends(get_db),
):
    sliders = (
        db.query(Slider)
        .order_by(
            Slider.display_order.asc(),
        )
        .all()
    )

    return sliders


# =====================================================
# UPDATE SLIDER
# =====================================================


@router.put(
    "/{slider_id}",
    response_model=SliderOut,
)
def update_slider(
    slider_id: int,
    image: UploadFile | None = File(None),
    display_order: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    slider = (
        db.query(Slider)
        .filter(
            Slider.id == slider_id,
            Slider.owner_id == current_user.id,
        )
        .first()
    )

    if not slider:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "اسلایدر پیدا نشد",
            },
        )

    # ==========================================
    # UPDATE IMAGE
    # ==========================================

    if image:
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "فایل باید تصویر باشد",
                },
            )

        ext = os.path.splitext(image.filename or "")[1]

        if not ext:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "فایل تصویر دارای پسوند معتبر نیست",
                },
            )

        filename = f"{uuid.uuid4().hex}{ext}"

        path = os.path.join(
            UPLOAD_DIR,
            filename,
        )

        with open(path, "wb") as buffer:
            buffer.write(image.file.read())

        # حذف تصویر قبلی
        if slider.image:
            old_path = slider.image.lstrip("/")

            if os.path.exists(old_path):
                os.remove(old_path)

        slider.image = f"/uploads/sliders/{filename}"

    # ==========================================
    # UPDATE DISPLAY ORDER
    # ==========================================

    if display_order is not None:
        if display_order < 1:
            raise HTTPException(
                status_code=400,
                detail={
                    "field": "display_order",
                    "message": "ترتیب باید بزرگ‌تر از صفر باشد",
                },
            )

        slider.display_order = display_order

    db.commit()
    db.refresh(slider)

    return slider


# =====================================================
# DELETE SLIDER
# =====================================================


@router.delete(
    "/{slider_id}",
)
def delete_slider(
    slider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    slider = (
        db.query(Slider)
        .filter(
            Slider.id == slider_id,
            Slider.owner_id == current_user.id,
        )
        .first()
    )

    if not slider:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "اسلایدر پیدا نشد",
            },
        )

    # حذف فایل تصویر
    if slider.image:
        image_path = slider.image.lstrip("/")

        if os.path.exists(image_path):
            os.remove(image_path)

    db.delete(slider)
    db.commit()

    return {
        "message": "اسلایدر با موفقیت حذف شد",
    }
