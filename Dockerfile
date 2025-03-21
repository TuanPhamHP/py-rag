# Sử dụng image Python 3.11 slim dựa trên Debian
FROM python:3.11-slim

# Đặt biến môi trường để tối ưu Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cài đặt các phụ thuộc hệ thống
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \       # Cho pdf2image
    libpq-dev \           # Cho psycopg2
    gcc \                 # Compiler cho một số thư viện
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy và cài đặt requirements
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code backend
COPY app/ .

# Mở port 8000 cho FastAPI
EXPOSE 8000

# Lệnh chạy ứng dụng
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]