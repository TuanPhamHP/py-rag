# utils/file_reader.py
import os
import json
import pandas as pd
import chromadb
from PyPDF2 import PdfReader
from docx import Document
from typing import List
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import pdfplumber
import subprocess

# Định nghĩa đường dẫn thư mục lưu file
UPLOAD_DIR = "uploaded_files"
CHROMADB_PATH = "app/db/chromadb_store"

# Khởi tạo client của ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
chroma_collection = chroma_client.get_or_create_collection(name="document_embeddings")

# Cấu hình đường dẫn tới Tesseract (nếu cần thiết)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # lấy từ which tesseract (Linux/Ubuntu) hoặc where tesseract (Windows)

def has_font_error(text):
    error_patterns = ["Cao Léc", "NGIIIA", "V[T", "xA", "HQI", "BO "]  # Thêm mẫu lỗi từ VNI
    return any(pattern in text for pattern in error_patterns)

def check_pdf_fonts(file_path: str):
    try:
        doc = fitz.open(file_path)
        fonts = set()
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            font_info = page.get_fonts()
            for font in font_info:
                fonts.add(font[2])  # Tên font
        print(f"Fonts in {file_path}: {fonts}")
        return fonts
    except Exception as e:
        print(f"Failed to check fonts for {file_path}: {e}")
        return set()

def read_pdf(file_path: str) -> str:
    """Đọc nội dung từ file PDF, ưu tiên OCR cho font Type1 có lỗi."""
    check_pdf_fonts(file_path)
    text = ""

    # Kiểm tra font để quyết định dùng OCR hay không
    fonts = check_pdf_fonts(file_path)
    use_ocr = any("Type1" in font for font in fonts)  # Dùng OCR nếu có font Type1

    # Phương án 1: Dùng pdftotext (nhanh, nhưng không tốt với font Type1 lỗi)
    if not use_ocr:
        try:
            result = subprocess.run(['pdftotext', '-layout', '-enc', 'Latin1', file_path, '-'], 
                                  capture_output=True, text=True)
            text = result.stdout
            if text.strip() and not has_font_error(text):
                return text.strip()
            elif text.strip():
                print(f"pdftotext extracted text with font errors for {file_path}, switching to OCR")
        except Exception as e:
            print(f"pdftotext failed for {file_path}: {e}")

    # Phương án 2: Dùng OCR với pytesseract (triệt để cho font Type1)
    try:
        doc = fitz.open(file_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)  # Tăng DPI để cải thiện chất lượng
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img, lang="vie", config='--psm 6')
            text += page_text + "\n"
        if text.strip():
            return text.strip()
        print(f"OCR extracted empty text for {file_path}, trying fallback")
    except Exception as e:
        print(f"OCR failed for {file_path}: {e}")

    # Phương án 3: Dùng pdfplumber (fallback)
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip() and not has_font_error(text):
            return text.strip()
    except Exception as e:
        print(f"pdfplumber failed for {file_path}: {e}")

    # Phương án 4: Dùng fitz (text extraction, fallback cuối)
    try:
        doc = fitz.open(file_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            if page_text:
                text += page_text + "\n"
        if text.strip() and not has_font_error(text):
            return text.strip()
    except Exception as e:
        print(f"fitz text extraction failed for {file_path}: {e}")

    return "Error: Could not extract text" if not text.strip() else text.strip()

def read_docx(file_path: str) -> str:
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

def read_json(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return json.dumps(data, indent=2)

def read_csv(file_path: str) -> str:
    df = pd.read_csv(file_path)
    return df.to_csv(index=False)

def read_file(file_path: str) -> str:
    """Xử lý đọc file từ thư mục uploaded_files."""
    ext = file_path.split(".")[-1].lower()
    if ext == "pdf":
        return read_pdf(file_path)
    elif ext == "docx":
        return read_docx(file_path)
    elif ext == "json":
        return read_json(file_path)
    elif ext == "csv":
        return read_csv(file_path)
    else:
        raise ValueError("Unsupported file type")

def add_to_chromadb(documents: List[dict]):
    """Lưu tài liệu đã đọc vào ChromaDB."""
    collection = chroma_client.get_or_create_collection("documents")
    for doc in documents:
        chroma_client.insert(doc["id"], doc["content"], metadata=doc.get("metadata", {}))

def process_and_store_file(filename: str):
    """Đọc file, trích xuất dữ liệu và lưu vào ChromaDB."""
    file_path = f"{UPLOAD_DIR}/{filename}"
    try:
        text = read_file(file_path)
        document = [{
            "id": filename,
            "content": text,
            "metadata": {"filename": filename}
        }]
        add_to_chromadb(document)
        print(f"✅ Đã lưu thành công file: {filename} vào ChromaDB")
    except Exception as e:
        print(f"❌ Lỗi khi xử lý {filename}: {e}")

def load_all_files() -> List[dict]:
    """Tải toàn bộ nội dung các file trong /uploaded_files để xử lý."""
    documents = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            content = read_file(file_path)
            if content and "Error" not in content:
                documents.append({
                    "id": filename,
                    "content": content,
                    "file_path": file_path
                })
            else:
                print(f"Skipped {filename}: Failed to extract content")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    return documents

if __name__ == "__main__":
    file_path = "uploaded_files/Cv 114_1.pdf"
    content = read_pdf(file_path)
    print(f"Content preview: {content[:500]}...")