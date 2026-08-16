from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship
from app.db.base import Base
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "PENDING"          # هنوز درخواست request به زرین‌پال ارسال نشده / در انتظار
    INITIATED = "INITIATED"      # authority گرفته شده، کاربر به درگاه هدایت شده
    SUCCESS = "SUCCESS"          # بازگشت از درگاه با Status=OK، هنوز verify نشده
    VERIFIED = "VERIFIED"        # verify موفق و ref_id دریافت شده (تراکنش نهایی)
    FAILED = "FAILED"            # درخواست یا verify ناموفق (Status=NOK یا خطای verify)
    CANCELLED = "CANCELLED"      # کاربر از پرداخت انصراف داده


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # =========================
    # اطلاعات درخواست پرداخت (Payment Request)
    # =========================

    amount = Column(
        Numeric(12, 2),
        nullable=False,
    )  # باید برابر با payable_amount سفارش در لحظه‌ی ثبت درخواست باشد

    description = Column(
        String,
        nullable=True,
    )

    mobile = Column(
        String,
        nullable=True,
    )

    email = Column(
        String,
        nullable=True,
    )

    callback_url = Column(
        String,
        nullable=False,
    )

    status = Column(
        SQLEnum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING,
        index=True,
    )

    # =========================
    # پاسخ درخواست پرداخت (Authority)
    # =========================

    authority = Column(
        String(36),
        nullable=True,
        unique=True,
        index=True,
    )  # UUID که با حرف A شروع می‌شود؛ تا قبل از ارسال درخواست به زرین‌پال، null است

    request_code = Column(
        Integer,
        nullable=True,
    )  # کد پاسخ زرین‌پال در مرحله‌ی request (data.code)

    request_message = Column(
        Text,
        nullable=True,
    )

    # =========================
    # پاسخ تأیید پرداخت (Verification)
    # =========================

    ref_id = Column(
        String,
        nullable=True,
        index=True,
    )  # شماره تراکنش نهایی؛ فقط بعد از verify موفق مقداردهی می‌شود

    verify_code = Column(
        Integer,
        nullable=True,
    )  # کد پاسخ زرین‌پال در مرحله‌ی verify (100 یا 101 یعنی موفق)

    verify_message = Column(
        Text,
        nullable=True,
    )

    card_pan = Column(
        String,
        nullable=True,
    )  # شماره کارت ماسک‌شده

    card_hash = Column(
        String,
        nullable=True,
    )

    fee_type = Column(
        String,
        nullable=True,
    )

    fee = Column(
        Numeric(12, 2),
        nullable=True,
    )

    # =========================
    # زمان‌بندی
    # =========================

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    verified_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =========================
    # ارتباطات
    # =========================

    order = relationship(
        "Order",
        back_populates="payments",
    )