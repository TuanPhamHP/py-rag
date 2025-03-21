# Sử dụng image Python 3.11 slim dựa trên Debian
FROM python:3.11-slim

# Đặt biến môi trường để tối ưu Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cài đặt các phụ thuộc hệ thống
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-vie \
    poppler-utils \
    libpq-dev \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy requirements.txt từ thư mục gốc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy main.py từ thư mục gốc
COPY main.py .

# Copy thư mục app/
COPY app/ app/
COPY utils/ utils/
COPY chroma_db/ chroma_db/
COPY db/ db/
COPY routes/ routes/
# Mở port 8000 cho FastAPI
EXPOSE 8000

# Lệnh chạy ứng dụng
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]