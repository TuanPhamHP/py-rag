
# PY RAG

Yêu cầu hệ thống (Unbutu):

PYTHON: 3.11

OCR - Tesseract

## DATABASE
```bash
ChromaDB: ^0.6.0
PostgreSQL
```

## Run Locally
Cài dependencies

```bash
  pip install -r requirements.txt
```

Giả lập môi trường (Optional)

```bash
  python3 -m venv venv
  source venv/bin/activate
```

Chạy file main

```bash
  python main.py
```


Khởi tạo DB

```bash
  python -m app.db.chat_history
```

## Commands
Các command nhanh để test Local (CRUD):

```bash
  app/commands
```