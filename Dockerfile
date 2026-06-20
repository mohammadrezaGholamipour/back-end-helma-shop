FROM python:3.11-slim

WORKDIR /app

# کپی فایل نیازها (مطمئن شوید در پوشه backend یک فایل requirements.txt دارید)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کل سورس‌کد
COPY . .

# اجرا با uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
