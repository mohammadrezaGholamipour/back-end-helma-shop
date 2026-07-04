import requests
import logging
import os

logger = logging.getLogger("services.telegram")

TOKEN = "8914407408:AAHXGtmK_RJIFl2Mg8oZh6mCk94ZU4LevMA"
CHAT_ID = "-1003966574296"

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
                    "parse_mode": "HTML" 
                },
                proxies=PROXIES,
                verify=False,
                timeout=30,
            )
        response.raise_for_status()
        logger.info("Product image sent to Telegram successfully.")
    except Exception:
        logger.exception("Failed to send product image to Telegram")
