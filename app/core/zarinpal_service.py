import httpx
from app.core.config import settings


def _base_domain() -> str:
    # برای تست از sandbox و برای پروداکشن از payment استفاده کن
    return "sandbox.zarinpal.com" if settings.ZARINPAL_SANDBOX else "payment.zarinpal.com"


def request_payment(
    amount: int,
    description: str,
    callback_url: str,
    mobile: str | None = None,
    email: str | None = None,
) -> dict:
    """
    ارسال درخواست ایجاد تراکنش به زرین‌پال.
    amount باید به تومان و به صورت عدد صحیح ارسال شود.
    """
    url = f"https://{_base_domain()}/pg/v4/payment/request.json"

    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": int(amount),
        "description": description,
        "callback_url": callback_url,
        "currency": "IRT",
    }

    metadata = {}
    if mobile:
        metadata["mobile"] = mobile
    if email:
        metadata["email"] = email
    if metadata:
        payload["metadata"] = metadata

    response = httpx.post(url, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def verify_payment(amount: int, authority: str) -> dict:
    """
    تأیید نهایی تراکنش بعد از بازگشت کاربر از درگاه.
    amount باید دقیقاً همان مقداری باشد که در مرحله‌ی request ارسال شده.
    """
    url = f"https://{_base_domain()}/pg/v4/payment/verify.json"

    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": int(amount),
        "authority": authority,
        "currency": "IRT",
    }

    response = httpx.post(url, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def get_startpay_url(authority: str) -> str:
    return f"https://{_base_domain()}/pg/StartPay/{authority}"