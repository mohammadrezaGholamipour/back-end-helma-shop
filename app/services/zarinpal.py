from app.core.config import settings
import httpx


class ZarinPalService:

    REQUEST_URL = (
        "https://api.zarinpal.com/pg/v4/payment/request.json"
    )

    VERIFY_URL = (
        "https://api.zarinpal.com/pg/v4/payment/verify.json"
    )

    START_PAY_URL = (
        "https://www.zarinpal.com/pg/StartPay/"
    )

    async def request_payment(
        self,
        amount: int,
        description: str,
        callback_url: str,
    ):
        payload = {
            "merchant_id": 'f42f8c24-adc9-4b09-84a3-901b0236719e',
            "amount": amount,
            "description": description,
            "callback_url": callback_url,
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.post(
                self.REQUEST_URL,
                json=payload,
            )

        response.raise_for_status()

        result = response.json()

        data = result.get("data")

        if not data:
            errors = result.get("errors") or {}

            raise Exception(
                errors.get(
                    "message",
                    "خطا در ایجاد درخواست پرداخت",
                )
            )

        if data.get("code") != 100:
            raise Exception(
                data.get(
                    "message",
                    "خطا در ایجاد درخواست پرداخت",
                )
            )

        authority = data["authority"]

        return {
            "authority": authority,
            "payment_url": (
                f"{self.START_PAY_URL}{authority}"
            ),
        }

    async def verify_payment(
        self,
        authority: str,
        amount: int,
    ):
        payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "authority": authority,
            "amount": amount,
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.post(
                self.VERIFY_URL,
                json=payload,
            )

        response.raise_for_status()

        return response.json()