from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse
from app.db.chromadb_store.chromadb_client import add_document
import pdfplumber
from docx import Document
import os

router = APIRouter()

@router.post("/add_document/")
async def add_doc(id: str, text: str):
    """API thêm dữ liệu vào vector database"""
    add_document(id, text)
    return {"message": "Document added!", "id": id}


@router.get("/download")
async def download_file(file_path: str):
    """Tải file từ server"""
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=os.path.basename(file_path), media_type='application/octet-stream')
    return {"error": "File not found"}

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Nhận file và xử lý nội dung"""
    content = await file.read()

    # Xử lý nội dung dựa trên loại file
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(content)
    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(content)
    else:
        return {"error": "File format not supported"}

    # Lưu vào ChromaDB
    add_document(file.filename, text)

    return {"message": "File uploaded and indexed!", "filename": file.filename}

def extract_text_from_pdf(content: bytes) -> str:
    """Trích xuất text từ PDF"""
    with pdfplumber.open(content) as pdf:
        return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def extract_text_from_docx(content: bytes) -> str:
    """Trích xuất text từ DOCX"""
    doc = Document(content)
    return "\n".join([para.text for para in doc.paragraphs])
