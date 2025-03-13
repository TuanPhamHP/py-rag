from fastapi import FastAPI, File, UploadFile
import uvicorn
from app.api.routes import router
from app.db.chromadb_store.chromadb_client import add_document, search
import pdfplumber
from docx import Document

app = FastAPI()

# Thêm API endpoints từ router
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "FastAPI + ChromaDB is running!"}

@app.get("/search/")
async def search_doc(query: str):
    """API tìm kiếm trong vector database"""
    results = search(query)
    return results

@app.post("/add_document/")
async def add_doc(id: str, text: str):
    """API thêm dữ liệu vào vector database"""
    add_document(id, text)
    return {"message": "Document added!", "id": id}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Nhận file và xử lý nội dung"""
    content = await file.read()  # Đọc file

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
