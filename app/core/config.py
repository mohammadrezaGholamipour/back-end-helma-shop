from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ZARINPAL_MERCHANT_ID: str
    ZARINPAL_SANDBOX: bool = False
    ZARINPAL_CALLBACK_URL: str   # مثلاً https://api.example.com/helma-shop-api/v1/payment/callback
    FRONTEND_PAYMENT_RESULT_URL: str  # صفحه‌ی نتیجه در فرانت، مثلاً https://example.com/payment-result
    class Config:
        env_file = ".env"  # مسیر فایل محیطی


# ایجاد شیء settings برای استفاده در کل پروژه
settings = Settings()


