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
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # lấy từ which tesseract(Linux|Unbutu) hoặc where teseract(Windows)

def read_pdf(file_path: str) -> str:
    """Đọc nội dung từ file PDF, xử lý lỗi font."""
    text = ""
    
    # Phương án 1: Dùng pdfplumber
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"pdfplumber failed for {file_path}: {e}")

    # Nếu pdfplumber không đọc được hoặc đọc sai, thử fitz
    if not text.strip():
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text("text")
                if page_text:
                    text += page_text + "\n"
                # Nếu không có văn bản, dùng OCR
                if not page_text.strip():
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text += pytesseract.image_to_string(img, lang="vie") + "\n"  # Chỉ định ngôn ngữ tiếng Việt
        except Exception as e:
            print(f"fitz failed for {file_path}: {e}")

    # Nếu vẫn không ổn, dùng pdftotext
    if not text.strip() or "Cao Léc" in text:  # Kiểm tra lỗi font điển hình
        try:
            result = subprocess.run(['pdftotext', '-layout', file_path, '-'], capture_output=True, text=True)
            text = result.stdout
        except Exception as e:
            print(f"pdftotext failed for {file_path}: {e}")

    return text.strip() if text else "Error: Could not extract text"
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
    """
    Xử lý đọc file từ thư mục uploaded_files
    """
    ext = file_path.split(".")[-1].lower()
    if file_path.endswith(".pdf"):
        return read_pdf(file_path)
    elif file_path.endswith(".docx"):
        return read_docx(file_path)
    elif file_path.endswith(".json"):
        return read_json(file_path)
    elif file_path.endswith(".csv"):
        return read_csv(file_path)
    # elif ext == ".doc":
    #     print(f"📄 Chuyển đổi file .doc → .docx: {file_path}")
    #     docx_path = convert_doc_to_docx(file_path)  # Chuyển sang docx
    #     return read_docx(docx_path)  # Đọc file mới
    else:
        raise ValueError("Unsupported file type")


def add_to_chromadb(documents: List[dict]):
    """Lưu tài liệu đã đọc vào ChromaDB."""
    collection = chroma_client.get_or_create_collection("documents")
    for doc in documents:
        chroma_client.insert(doc["id"], doc["content"], metadata=doc.get("metadata", {}))


def process_and_store_file(filename: str):
    """
    Đọc file, trích xuất dữ liệu và lưu vào ChromaDB.
    """
    file_path = f"{UPLOAD_DIR}/{filename}"
    try:
        text = read_file(file_path)
        # Tạo Document object để lưu vào ChromaDB
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
    """Tải toàn bộ nội dung các file trong /uploaded_files để xử lý"""
    documents = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        # content = read_file(file_path)
        # if content:  # Nếu file đọc thành công
        #     documents.append({
        #         "id": filename, 
        #         "content": content,
        #         "file_path": file_path
        #         })
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
