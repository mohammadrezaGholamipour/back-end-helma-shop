from app.core.security import get_current_user, get_current_admin
from app.schemas.payment import PaymentRequestOut, PaymentOut
from fastapi import APIRouter, Depends, HTTPException
from app.models.payment import Payment, PaymentStatus
from app.models.order import Order, OrderStatus
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
import httpx

from app.core.zarinpal_service import (
    request_payment,
    verify_payment,
    get_startpay_url,
)

router = APIRouter(
    prefix="/helma-shop-api/v1/payment",
    tags=["Payment"],
)


# =====================
# CREATE PAYMENT REQUEST
# =====================

@router.post(
    "/request/{order_id}",
    response_model=PaymentRequestOut,
)
def create_payment_request(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # =====================
    # GET ORDER
    # =====================

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail={
                "field": "order",
                "message": "سفارش مورد نظر یافت نشد",
            },
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "order",
                "message": "این سفارش قابل پرداخت نیست",
            },
        )

    if order.payable_amount is None or order.payable_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "order",
                "message": "مبلغ قابل پرداخت سفارش نامعتبر است",
            },
        )

    # =====================
    # CHECK EXISTING VERIFIED PAYMENT
    # =====================

    already_paid = (
        db.query(Payment)
        .filter(
            Payment.order_id == order.id,
            Payment.status == PaymentStatus.VERIFIED,
        )
        .first()
    )

    if already_paid:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "order",
                "message": "این سفارش قبلاً پرداخت شده است",
            },
        )

    # =====================
    # CREATE PAYMENT RECORD
    # =====================

    payment = Payment(
        order_id=order.id,
        amount=order.payable_amount,
        description=f"پرداخت سفارش شماره {order.id}",
        mobile=current_user.mobile,
        email=getattr(current_user, "email", None),
        callback_url=settings.ZARINPAL_CALLBACK_URL,
        status=PaymentStatus.PENDING,
    )

    db.add(payment)
    db.flush()

    # =====================
    # CALL ZARINPAL REQUEST API
    # =====================

    try:
        result = request_payment(
            amount=int(order.payable_amount),
            description=payment.description,
            callback_url=payment.callback_url,
            mobile=payment.mobile,
            email=payment.email,
        )
    except httpx.HTTPError:
        payment.status = PaymentStatus.FAILED
        payment.request_message = "خطا در برقراری ارتباط با درگاه پرداخت"
        db.commit()
        raise HTTPException(
            status_code=502,
            detail={
                "field": "gateway",
                "message": "خطا در برقراری ارتباط با درگاه پرداخت",
            },
        )

    data = result.get("data") or {}
    errors = result.get("errors") or {}

    if data.get("code") == 100 and data.get("authority"):
        payment.authority = data["authority"]
        payment.request_code = data.get("code")
        payment.request_message = data.get("message")
        payment.status = PaymentStatus.INITIATED

        db.commit()
        db.refresh(payment)

        return PaymentRequestOut(
            payment_id=payment.id,
            authority=payment.authority,
            payment_url=get_startpay_url(payment.authority),
        )

    # =====================
    # REQUEST FAILED
    # =====================

    payment.status = PaymentStatus.FAILED
    payment.request_code = data.get("code")
    payment.request_message = str(errors) if errors else "خطای نامشخص از درگاه پرداخت"

    db.commit()

    raise HTTPException(
        status_code=400,
        detail={
            "field": "gateway",
            "message": "خطا در ایجاد درخواست پرداخت",
            "gateway_errors": errors,
        },
    )


# =====================
# ZARINPAL CALLBACK
# =====================
# این مسیر خودِ زرین‌پال (نه فرانت) صدا می‌زند، پس بدون احراز هویت کاربر است.

@router.get("/callback")
def payment_callback(
    Authority: str,
    Status: str,
    db: Session = Depends(get_db),
):
    payment = (
        db.query(Payment)
        .filter(Payment.authority == Authority)
        .first()
    )

    if not payment:
        return RedirectResponse(
            url=f"{settings.FRONTEND_PAYMENT_RESULT_URL}?status=not_found",
        )

    order = db.query(Order).filter(Order.id == payment.order_id).first()

    # =====================
    # USER CANCELLED
    # =====================

    if Status != "OK":
        payment.status = PaymentStatus.CANCELLED
        db.commit()

        return RedirectResponse(
            url=f"{settings.FRONTEND_PAYMENT_RESULT_URL}"
                f"?status=cancelled&order_id={payment.order_id}",
        )

    # =====================
    # VERIFY WITH ZARINPAL
    # =====================

    try:
        result = verify_payment(
            amount=int(payment.amount),
            authority=Authority,
        )
    except httpx.HTTPError:
        payment.status = PaymentStatus.FAILED
        payment.verify_message = "خطا در برقراری ارتباط با درگاه پرداخت"
        db.commit()

        return RedirectResponse(
            url=f"{settings.FRONTEND_PAYMENT_RESULT_URL}"
                f"?status=failed&order_id={payment.order_id}",
        )

    data = result.get("data") or {}
    errors = result.get("errors") or {}

    # کد 100 یعنی تأیید موفق تازه، 101 یعنی این تراکنش قبلاً هم تأیید شده بود
    if data.get("code") in (100, 101):
        payment.status = PaymentStatus.VERIFIED
        payment.ref_id = str(data.get("ref_id"))
        payment.verify_code = data.get("code")
        payment.verify_message = data.get("message")
        payment.card_pan = data.get("card_pan")
        payment.card_hash = data.get("card_hash")
        payment.fee_type = data.get("fee_type")
        payment.fee = data.get("fee")
        payment.verified_at = datetime.now(timezone.utc)

        if order:
            order.status = OrderStatus.PROCESSING

        db.commit()

        return RedirectResponse(
            url=f"{settings.FRONTEND_PAYMENT_RESULT_URL}"
                f"?status=success&order_id={payment.order_id}&ref_id={payment.ref_id}",
        )

    # =====================
    # VERIFY FAILED
    # =====================

    payment.status = PaymentStatus.FAILED
    payment.verify_code = data.get("code")
    payment.verify_message = str(errors) if errors else "تأیید تراکنش ناموفق بود"

    db.commit()

    return RedirectResponse(
        url=f"{settings.FRONTEND_PAYMENT_RESULT_URL}"
            f"?status=failed&order_id={payment.order_id}",
    )


# =====================
# GET MY PAYMENT
# =====================

@router.get(
    "/{payment_id}",
    response_model=PaymentOut,
)
def get_my_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .join(Order, Order.id == Payment.order_id)
        .filter(
            Payment.id == payment_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail={
                "field": "payment",
                "message": "پرداخت مورد نظر یافت نشد",
            },
        )

    return payment


# =====================
# ADMIN: GET PAYMENTS OF AN ORDER
# =====================

@router.get(
    "/admin/order/{order_id}",
    response_model=list[PaymentOut],
)
def get_order_payments_admin(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    payments = (
        db.query(Payment)
        .filter(Payment.order_id == order_id)
        .order_by(Payment.id.desc())
        .all()
    )

    return payments