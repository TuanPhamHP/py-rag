import chromadb
import openai
import os
import re
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
# Kết nối với ChromaDB và lưu dữ liệu vào thư mục "chromadb_store"
chroma_client = chromadb.PersistentClient(path="./app/db/chromadb_store")

# Tạo collection để lưu vector (tên là "documents")
collection = chroma_client.get_or_create_collection(name="documents")
RAG_KEYWORDS = ["tài liệu", "nội bộ", "hồ sơ", "báo cáo", "file", "tệp tin"]

def remove_words(text, rag_words):
    pattern = r'\b(' + '|'.join(map(re.escape, rag_words)) + r')\b'
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return ' '.join(cleaned_text.split()) 

def generate_embedding(text: str):
    ip = remove_words(text, RAG_KEYWORDS)
    response = openai.embeddings.create(
        model="text-embedding-ada-002",  # Mô hình OpenAI tạo embedding
        input=ip
    )
    return response.data[0].embedding

def add_document(id: str, text: str, metadata: dict = {}):
    """Thêm dữ liệu vào vector database"""
    embedding = generate_embedding(text)
    collection.add(
        ids=[id],
        documents=[text],
        metadatas=[metadata],
        embeddings=[embedding]
    )

def search(query: str, top_k: int = 15):
    """Tìm kiếm dữ liệu dựa trên vector"""
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results
