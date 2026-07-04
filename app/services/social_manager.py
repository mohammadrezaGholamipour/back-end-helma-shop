from .telegram import send_product as telegram_send
from .eitaa import send_product as eitaa_send
from .bale import send_product as bale_send


def notify_new_product(image_path: str | None, name: str, price: int, volume: int):

    telegram_caption = (
        f"📦 <b>محصول:</b> {name}\n\n"
        f"💰 <b>قیمت:</b> {price:,} تومان\n\n"
        f"⚖️ <b>وزن:</b> {volume} گرم"
    )
    
    bale_caption = (
        f"📦 محصول: {name}\n\n"
        f"💰 قیمت: {price:,} تومان\n\n"
        f"⚖️ وزن: {volume} گرم"
    )

    eitaa_caption = (
        f"📦 محصول: {name}\n"
        f"\n"
        f"💰 قیمت: {price:,} تومان\n"
        f"\n"
        f"⚖️ وزن: {volume} گرم\n"
        f"\u200F"  
    )

    if image_path:
        local_image_path = image_path.lstrip("/")

        telegram_send(local_image_path, telegram_caption)

        eitaa_send(local_image_path, name, eitaa_caption)

        bale_send(local_image_path, bale_caption)

