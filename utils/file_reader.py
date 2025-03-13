import os
import json
import pandas as pd
import chromadb
from PyPDF2 import PdfReader
from docx import Document
from typing import List
import fitz


# Định nghĩa đường dẫn thư mục lưu file
UPLOAD_DIR = "uploaded_files"
CHROMADB_PATH = "app/db/chromadb_store"

# Khởi tạo client của ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
chroma_collection = chroma_client.get_or_create_collection(name="document_embeddings")

def read_pdf(file_path: str) -> str:
    """Đọc nội dung từ file PDF."""
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text("text") + "\n"

    return text


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
        add_to_chroma_db(document)
        print(f"✅ Đã lưu thành công file: {filename} vào ChromaDB")
    except Exception as e:
        print(f"❌ Lỗi khi xử lý {filename}: {e}")


def load_all_files() -> List[dict]:
    """Tải toàn bộ nội dung các file trong /uploaded_files để xử lý"""
    documents = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        content = read_file(file_path)
        if content:  # Nếu file đọc thành công
            documents.append({"id": filename, "content": content})
    return documents