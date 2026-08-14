from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.payment import Payment, PaymentStatus
from app.models.order import Order, OrderStatus
from fastapi.responses import RedirectResponse
from app.core.security import get_current_user
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from decimal import Decimal
from typing import Optional
import httpx



router = APIRouter(
    prefix="/helma-shop-api/v1/payment",
    tags=["Payment"],
)


# =========================================================
# ZARINPAL CONFIG
# =========================================================

ZARINPAL_REQUEST_URL = "https://api.zarinpal.com/pg/v4/payment/request.json"

ZARINPAL_VERIFY_URL = "https://api.zarinpal.com/pg/v4/payment/verify.json"

ZARINPAL_START_PAY_URL = "https://www.zarinpal.com/pg/StartPay/"


# =========================================================
# CREATE PAYMENT
# =========================================================


@router.post(
    "/zarinpal/{order_id}",
)
async def create_zarinpal_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # =====================================================
    # GET ORDER
    # =====================================================

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

    # =====================================================
    # CHECK ORDER STATUS
    # =====================================================

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "order",
                "message": "این سفارش قابل پرداخت نیست",
            },
        )

    # =====================================================
    # CHECK AMOUNT
    # =====================================================

    if order.payable_amount is None:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "amount",
                "message": "مبلغ قابل پرداخت مشخص نیست",
            },
        )

    if order.payable_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "amount",
                "message": "مبلغ پرداخت باید بیشتر از صفر باشد",
            },
        )

    # =====================================================
    # CHECK EXISTING SUCCESSFUL PAYMENT
    # =====================================================

    successful_payment = (
        db.query(Payment)
        .filter(
            Payment.order_id == order.id,
            Payment.status == PaymentStatus.SUCCESS,
        )
        .first()
    )

    if successful_payment:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "payment",
                "message": "این سفارش قبلاً پرداخت شده است",
            },
        )

    # =====================================================
    # AMOUNT
    # =====================================================

    # اگر قیمت‌های دیتابیس شما تومان هستند،
    # زرین‌پال مبلغ را به ریال دریافت می‌کند.
    #
    # مثال:
    #
    # 100000 تومان
    # ↓
    # 1000000 ریال

    amount = int(Decimal(order.payable_amount) * 10)

    # =====================================================
    # CREATE PAYMENT RECORD
    # =====================================================

    payment = Payment(
        order_id=order.id,
        amount=order.payable_amount,
        status=PaymentStatus.PENDING,
        gateway="zarinpal",
    )

    db.add(payment)
    db.flush()

    # =====================================================
    # ZARINPAL REQUEST
    # =====================================================

    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": amount,
        "description": f"پرداخت سفارش #{order.id}",
        "callback_url": settings.ZARINPAL_CALLBACK_URL,
        "metadata": {
            "mobile": current_user.mobile,
        },
    }

    try:

        async with httpx.AsyncClient(
            timeout=30.0,
        ) as client:

            response = await client.post(
                ZARINPAL_REQUEST_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                },
            )

    except httpx.RequestError:

        db.rollback()

        raise HTTPException(
            status_code=503,
            detail={
                "field": "gateway",
                "message": "ارتباط با درگاه پرداخت برقرار نشد",
            },
        )

    # =====================================================
    # HTTP ERROR
    # =====================================================

    if response.status_code != 200:

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail={
                "field": "gateway",
                "message": "درگاه پرداخت پاسخ معتبر ارسال نکرد",
            },
        )

    # =====================================================
    # PARSE RESPONSE
    # =====================================================

    try:
        result = response.json()

    except ValueError:

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail={
                "field": "gateway",
                "message": "پاسخ درگاه پرداخت نامعتبر است",
            },
        )

    # =====================================================
    # ZARINPAL ERROR
    # =====================================================

    errors = result.get("errors")

    if errors:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail={
                "field": "gateway",
                "message": errors.get(
                    "message",
                    "خطا در ایجاد تراکنش",
                ),
                "code": errors.get("code"),
            },
        )

    # =====================================================
    # GET DATA
    # =====================================================

    data = result.get("data")

    if not data:

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail={
                "field": "gateway",
                "message": "اطلاعات تراکنش از درگاه دریافت نشد",
            },
        )

    # =====================================================
    # CHECK REQUEST CODE
    # =====================================================

    if data.get("code") != 100:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail={
                "field": "gateway",
                "message": data.get(
                    "message",
                    "خطا در ایجاد تراکنش",
                ),
                "code": data.get("code"),
            },
        )

    # =====================================================
    # AUTHORITY
    # =====================================================

    authority = data.get("authority")

    if not authority:

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail={
                "field": "gateway",
                "message": "شناسه تراکنش از درگاه دریافت نشد",
            },
        )

    # =====================================================
    # SAVE AUTHORITY
    # =====================================================

    payment.authority = authority

    db.commit()
    db.refresh(payment)

    # =====================================================
    # PAYMENT URL
    # =====================================================

    payment_url = f"{ZARINPAL_START_PAY_URL}{authority}"

    return {
        "payment_id": payment.id,
        "order_id": order.id,
        "authority": authority,
        "payment_url": payment_url,
    }


# =========================================================
# ZARINPAL CALLBACK
# =========================================================


@router.get(
    "/zarinpal/callback",
)
async def zarinpal_callback(
    Authority: str = Query(...),
    Status: str = Query(...),
    db: Session = Depends(get_db),
):
    # =====================================================
    # FIND PAYMENT
    # =====================================================

    payment = (
        db.query(Payment)
        .filter(
            Payment.authority == Authority,
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail={
                "field": "payment",
                "message": "تراکنش مورد نظر یافت نشد",
            },
        )

    # =====================================================
    # GET ORDER
    # =====================================================

    order = (
        db.query(Order)
        .filter(
            Order.id == payment.order_id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail={
                "field": "order",
                "message": "سفارش مربوط به تراکنش یافت نشد",
            },
        )

    # =====================================================
    # ALREADY SUCCESSFUL
    # =====================================================

    if payment.status == PaymentStatus.SUCCESS:

        return RedirectResponse(
            url=(
                f"{settings.FRONTEND_URL}"
                f"/payment/result"
                f"?status=success"
                f"&order_id={order.id}"
                f"&ref_id={payment.ref_id}"
            )
        )

    # =====================================================
    # USER CANCELLED / FAILED
    # =====================================================

    if Status.upper() != "OK":

        payment.status = PaymentStatus.FAILED

        db.commit()

        return RedirectResponse(
            url=(
                f"{settings.FRONTEND_URL}"
                f"/payment/result"
                f"?status=failed"
                f"&order_id={order.id}"
            )
        )

    # =====================================================
    # CHECK PAYMENT AMOUNT
    # =====================================================

    amount = int(Decimal(payment.amount) * 10)

    # =====================================================
    # VERIFY
    # =====================================================

    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "authority": Authority,
        "amount": amount,
    }

    try:

        async with httpx.AsyncClient(
            timeout=30.0,
        ) as client:

            response = await client.post(
                ZARINPAL_VERIFY_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                },
            )

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail={
                "field": "gateway",
                "message": "ارتباط با درگاه برای تایید پرداخت برقرار نشد",
            },
        )

    # =====================================================
    # HTTP ERROR
    # =====================================================

    if response.status_code != 200:

        raise HTTPException(
            status_code=502,
            detail={
                "field": "gateway",
                "message": "پاسخ نامعتبر از درگاه دریافت شد",
            },
        )

    # =====================================================
    # PARSE RESPONSE
    # =====================================================

    try:
        result = response.json()

    except ValueError:

        raise HTTPException(
            status_code=502,
            detail={
                "field": "gateway",
                "message": "پاسخ Verify درگاه نامعتبر است",
            },
        )

    # =====================================================
    # VERIFY ERROR
    # =====================================================

    errors = result.get("errors")

    if errors:

        payment.status = PaymentStatus.FAILED

        db.commit()

        return RedirectResponse(
            url=(
                f"{settings.FRONTEND_URL}"
                f"/payment/result"
                f"?status=failed"
                f"&order_id={order.id}"
            )
        )

    # =====================================================
    # VERIFY DATA
    # =====================================================

    data = result.get("data") or {}

    code = data.get("code")

    # =====================================================
    # SUCCESS
    # =====================================================

    if code == 100:

        ref_id = data.get("ref_id")

        payment.status = PaymentStatus.SUCCESS
        payment.ref_id = str(ref_id) if ref_id is not None else None

        order.status = OrderStatus.PROCESSING

        db.commit()

        return RedirectResponse(
            url=(
                f"{settings.FRONTEND_URL}"
                f"/payment/result"
                f"?status=success"
                f"&order_id={order.id}"
                f"&ref_id={payment.ref_id}"
            )
        )

    # =====================================================
    # ALREADY VERIFIED
    # =====================================================

    if code == 101:

        payment.status = PaymentStatus.SUCCESS

        ref_id = data.get("ref_id")

        if ref_id is not None:
            payment.ref_id = str(ref_id)

        order.status = OrderStatus.PROCESSING

        db.commit()

        return RedirectResponse(
            url=(
                f"{settings.FRONTEND_URL}"
                f"/payment/result"
                f"?status=success"
                f"&order_id={order.id}"
                f"&ref_id={payment.ref_id or ''}"
            )
        )

    # =====================================================
    # PAYMENT FAILED
    # =====================================================

    payment.status = PaymentStatus.FAILED

    db.commit()

    return RedirectResponse(
        url=(
            f"{settings.FRONTEND_URL}"
            f"/payment/result"
            f"?status=failed"
            f"&order_id={order.id}"
        )
    )


# =========================================================
# GET PAYMENT STATUS
# =========================================================


@router.get(
    "/{payment_id}",
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .join(Order)
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

    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "status": payment.status,
        "gateway": payment.gateway,
        "authority": payment.authority,
        "ref_id": payment.ref_id,
    }
