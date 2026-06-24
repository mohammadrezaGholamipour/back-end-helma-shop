FROM python:3.11-slim

WORKDIR /app

# کپی فایل requirements برای نصب پکیج‌ها
COPY requirements.txt .

# ۱. ابتدا pip را آپدیت می‌کنیم
# ۲. سپس با افزایش زمان انتظار (timeout) پکیج‌ها را نصب می‌کنیم
RUN pip install --upgrade pip && \
    pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# کپی کل سورس‌کد پروژه
COPY . .

# اجرا با uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

