FROM python:3.11-slim

WORKDIR /app

# ابتدا فقط requirements را کپی کن تا لایه پکیج‌ها کش شود
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# سپس بقیه کد را کپی کن
COPY . .

# به جای CMD معمولی، بهتر است از یک اسکریپت entrypoint استفاده کنی
# تا مطمئن شوی دیتابیس قبل از بالا آمدن وب‌سرویس، مایگریت شده است.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
