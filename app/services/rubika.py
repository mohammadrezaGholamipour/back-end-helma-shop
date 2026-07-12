# app/services/bale.py

import os
import logging
import requests

logger = logging.getLogger("services.bale")

TOKEN = "BIHFBB0GVVEECGUKWMRKVKGIVLTPXWNAJSIOCJEVWIFJOOSZMULRTJDAZRTZBUOS"
CHAT_ID = "4657728849"

BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"


def send_product(image_path: str, caption: str):
    """ارسال محصول با تصویر و کپشن به کانال یا گروه بله"""
    try:
        if not os.path.exists(image_path):
            logger.error(f"Bale image not found: {image_path}")
            return

        url = f"{BASE_URL}/sendPhoto"

        with open(image_path, "rb") as image:
            response = requests.post(
                url,
                files={
                    "photo": image,
                },
                data={
                    "chat_id": CHAT_ID,
                    "caption": caption,
                    "parse_mode": "HTML",
                },
                timeout=30,
            )

        response.raise_for_status()
        logger.info("Product image sent to Bale successfully.")

    except Exception:
        logger.exception("Failed to send product image to Bale")