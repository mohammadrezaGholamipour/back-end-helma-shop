from app.schemas.category import CategoryOut, CreateAndUpdateCategory
from fastapi import APIRouter, Depends, Form, UploadFile, File, Query
from app.core.security import get_current_user
from app.models.category import Category
from sqlalchemy.orm import Session
from app.db.session import get_db
from fastapi import HTTPException
from app.models import User
import uuid
import os

router = APIRouter(prefix="/helma-shop-api/v1/category", tags=["Category"])


# ===================== create =====================
@router.post("/create", response_model=CreateAndUpdateCategory)
def create_category(
        name: str = Form(...),
        image: UploadFile = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    UPLOAD_DIR = "uploads/categories"
    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail={"field": "Category", "message": "دسته بندی با این نام ثبت شده است"}
        )

    image_url = None
    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail={"field": "Category", "message": "عکس باید فرمت تصویر باشد"}
            )
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())

        image_url = f"/uploads/categories/{filename}"

    category = Category(
        application_id=current_user.application_id,
        owner_id=current_user.id,
        image=image_url,
        name=name,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


# ===================== list me =====================
@router.get("/me", response_model=list[CategoryOut])
def get_categories(
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
    categories = (
        db.query(Category)
        .filter(Category.application_id == application_id)
        .all()
    )

    return categories


# ===================== delete =====================
@router.delete("/delete", response_model=CategoryOut)
def delete_category(
        category_id: int | None = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if category_id is None:
        raise HTTPException(
            status_code=400,
            detail={"field": "Category_id", "message": "شناسه دسته‌بندی ارسال نشده است"}
        )

    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail={"field": "Category", "message": "دسته بندی مورد نظر یافت نشد"}
        )

    if category.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"field": "Category", "message": "شما مجاز به حذف این دسته بندی نیستید"}
        )

    db.delete(category)
    db.commit()

    return {"message": "دسته بندی مورد نظر حذف شد"}


# ===================== update =====================
@router.put("/update", response_model=CreateAndUpdateCategory)
def update_category(
        category_id: int = Form(...),
        name: str | None = Form(None),
        image: UploadFile = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    UPLOAD_DIR = "uploads/categories"

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=404,
            detail={"field": "Category", "message": "دسته بندی مورد نظر یافت نشد"}
        )

    if category.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"field": "Category", "message": "شما مجاز به ویرایش این دسته بندی نیستید"}
        )

    if name:
        existing = db.query(Category).filter(Category.name == name, Category.id != category_id).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail={"field": "Category", "message": "دسته بندی با این نام قبلا ثبت شده است"}
            )
        category.name = name

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail={"field": "Category", "message": "عکس باید فرمت تصویر باشد"}
            )

        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())

        category.image = f"/uploads/categories/{filename}"

    db.add(category)
    db.commit()
    db.refresh(category)

    return category
