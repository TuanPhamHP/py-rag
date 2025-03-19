
from app.db.database import collection
from app.db.chromadb_store.chromadb_client import generate_embedding  # Import hàm đã có
from typing import List
from pydantic import BaseModel
from rank_bm25 import BM25Okapi
import os

class RelevantDoc(BaseModel):
    filename: str
    file_path: str
    content: str


def split_into_chunks(document: str, chunk_size: int = 250) -> list:
    """Chia nội dung tài liệu thành đoạn nhỏ (chunks)"""
    words = document.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def rank_passages(passages: List[str], query: str, top_k: int = 3) -> List[str]:
    """Xếp hạng các đoạn văn bản theo độ liên quan với query"""
    tokenized_passages = [p.split() for p in passages]  # Tokenize từng đoạn
    bm25 = BM25Okapi(tokenized_passages)  # Tạo index BM25
    query_tokens = query.split()  # Tokenize câu hỏi
    scores = bm25.get_scores(query_tokens)  # Tính điểm BM25

    # Sắp xếp theo điểm số và lấy top_k đoạn có điểm cao nhất
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [passages[i] for i in top_indices]

async def retrieve_context(query: str, top_k: int = 3) -> List[RelevantDoc]:
    """Truy vấn ChromaDB bằng embedding để lấy top_k tài liệu liên quan"""
    try:
        query_embedding = generate_embedding(query)  # Sinh embedding cho câu hỏi
        results = collection.query(
            query_embeddings=[query_embedding], 
            n_results=top_k, 
            include=["documents", "metadatas"]
        )

        documents_list = results.get("documents", [[]])[0]  # Lấy danh sách tài liệu
        metadatas_list = results.get("metadatas", [[]])[0]  # Lấy metadata

        if not documents_list:
            return []
        
        # Chia nhỏ từng tài liệu thành đoạn nhỏ (chunks)
        all_chunks = []
        for doc, meta in zip(documents_list, metadatas_list):
            chunks = split_into_chunks(doc)  # Cắt nhỏ tài liệu
            for chunk in chunks:
                all_chunks.append({
                    "chunk": chunk,
                    "filename": meta.get("filename", "Unnamed"),
                    "file_path": meta.get("file_path", "N/A")
                })

        # 🔥 Dùng BM25 - sliding windows
        tokenized_chunks = [chunk["chunk"].split() for chunk in all_chunks]
        bm25 = BM25Okapi(tokenized_chunks)
        tokenized_query = query.split()
        scores = bm25.get_scores(tokenized_query)

        # Lấy top_k đoạn phù hợp nhất
        best_chunks = sorted(zip(all_chunks, scores), key=lambda x: x[1], reverse=True)[:top_k]

        # Chuẩn hóa kết quả thành danh sách `RelevantDoc`
        relevant_docs = [
            RelevantDoc(
                filename=chunk["filename"],
                file_path=chunk["file_path"],
                content=chunk["chunk"]
            )
            for chunk, _ in best_chunks
        ]

        return relevant_docs
    except Exception as e:
        print(f"Error in retrieve_context: {e}")
        return []

def search_documents(query: str, top_k: int = 15):
    """Tìm kiếm văn bản gần nhất trong ChromaDB"""
    query_embedding = generate_embedding(query)  # Dùng hàm có sẵn

    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=top_k
    )

    return results
