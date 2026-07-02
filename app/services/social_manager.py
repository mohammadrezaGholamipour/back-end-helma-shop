# app/services/social_manager.py

from .telegram import send_product as telegram_send
from .eitaa import send_product as eitaa_send
# from .bale import send_product as bale_send
# from .rubika import send_product as rubika_send


def notify_new_product(image_path: str | None, name: str, price: int, volume: int):

    # کپشن مخصوص تلگرام (HTML)
    telegram_caption = (
        f"📦 <b>محصول:</b> {name}\n\n"
        f"💰 <b>قیمت:</b> {price:,} تومان\n\n"
        f"⚖️ <b>وزن:</b> {volume} گرم"
    )

    # کپشن مخصوص ایتا (بدون HTML + با فاصله + با Zero Width)
    eitaa_caption = (
        f"📦 محصول: {name}\n"
        f"\n"
        f"💰 قیمت: {price:,} تومان\n"
        f"\n"
        f"⚖️ وزن: {volume} گرم\n"
        f"\u200F"  # کاراکتر نامرئی برای جلوگیری از قاطی شدن با متادیتا
    )

    if image_path:
        local_image_path = image_path.lstrip("/")

        # ارسال تلگرام
        telegram_send(local_image_path, telegram_caption)

        # ارسال ایتا
        eitaa_send(local_image_path, name, eitaa_caption)

        # ارسال بله و روبیکا (بدون HTML)
        # bale_send(local_image_path, eitaa_caption)
        # rubika_send(local_image_path, eitaa_caption)
