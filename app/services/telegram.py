# app/services/telegram.py

import os
import logging
import requests

logger = logging.getLogger("services.telegram")

TOKEN = "8729934548:AAGuSUorsGRXrPayBu3dIstoRDyF1rMzBJE"
CHAT_ID = "-1001673435498"

PROXIES = {
    "http": "http://relay:8085",
    "https": "http://relay:8085",
}


def send_product(image_path: str, caption: str):
    """ارسال محصول با تصویر و کپشن به کانال یا گروه تلگرام"""
    try:
        if not os.path.exists(image_path):
            logger.error(f"Telegram image not found: {image_path}")
            return

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        
        with open(image_path, "rb") as image:
            response = requests.post(
                url,
                files={"photo": image},
                data={
                    "chat_id": CHAT_ID,
                    "caption": caption,
                    "parse_mode": "HTML"  # در صورت تمایل به استفاده از تگ‌های HTML در کپشن
                },
                proxies=PROXIES,
                verify=False,
                timeout=30,
            )
        response.raise_for_status()
        logger.info("Product image sent to Telegram successfully.")
    except Exception:
        logger.exception("Failed to send product image to Telegram")
