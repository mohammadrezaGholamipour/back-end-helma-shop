import requests
import logging
import os

logger = logging.getLogger("eitaa")

EITAA_TOKEN = "bot479619:aea2edc1-1a66-42a1-ba63-593f9139de2b"
CHAT_ID = "11198574"

BASE_URL = f"https://eitaayar.ir/api/{EITAA_TOKEN}"


def send_product(
    image_path: str,
    title: str,
    caption: str,
):
    """
    ارسال محصول به کانال ایتا
    """

    try:

        url = f"{BASE_URL}/sendFile"

        with open(image_path, "rb") as image:

            response = requests.post(
                url,
                files={
                    "file": image
                },
                data={
                    "chat_id": CHAT_ID,
                    "title": title,
                    "caption": caption,
                    "pin": True,
                },
                timeout=30,
                verify=False,
            )

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):
            logger.error("Eitaa Error : %s", result)
            return

        logger.info("Product sent to eitaa successfully.")

    except Exception:
        logger.exception("Sending product to Eitaa failed")