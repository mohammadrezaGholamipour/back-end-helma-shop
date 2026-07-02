# app/services/eitaa.py

import os
import logging
import requests

logger = logging.getLogger("services.eitaa")

TOKEN = "bot479619:aea2edc1-1a66-42a1-ba63-593f9139de2b"
CHAT_ID = "11198574"


def send_product(image_path: str, title: str, caption: str):
    """ارسال محصول به ایتا"""
    try:
        if not os.path.exists(image_path):
            logger.error(f"Eitaa image not found: {image_path}")
            return
        
        url = f"https://eitaayar.ir/api/{TOKEN}/sendFile"
        with open(image_path, "rb") as image:
            response = requests.post(
                url,
                files={"file": image},
                data={
                    "chat_id": CHAT_ID,
                    "title": title,
                    "caption": caption,
                    "pin": True,
                },
                timeout=30,
                verify=False
            )

        response.raise_for_status()
        logger.info("Product sent to Eitaa successfully.")

    except Exception:
        logger.exception("Failed sending to Eitaa")
