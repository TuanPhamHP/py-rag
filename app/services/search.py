
from app.db.database import collection
from app.db.chromadb_store.chromadb_client import generate_embedding  # Import hàm đã có
from typing import List
from pydantic import BaseModel
from rank_bm25 import BM25Okapi
from underthesea import word_tokenize

class RelevantDoc(BaseModel):
    filename: str
    file_path: str
    content: str


# def split_into_chunks(document: str, chunk_size: int = 250) -> list:
#     """Chia nội dung tài liệu thành đoạn nhỏ (chunks)"""
#     words = document.split()
#     return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

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
    try:
        # Tách tên file (nếu có) từ query
        filename_query = None
        if "file nội bộ:" in query.lower():
            filename_query = query.lower().split("file nội bộ:")[-1].strip()

        query_embedding = generate_embedding(query)
        if filename_query:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"filename": {"$contains": filename_query}},  # Lọc theo filename
                include=["documents", "metadatas", "distances"]
            )
        else:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=15,
                include=["documents", "metadatas", "distances"]  # Thêm distances
            )

        documents_list = results.get("documents", [[]])[0]
        metadatas_list = results.get("metadatas", [[]])[0]
        distances_list = results.get("distances", [[]])[0]  # Khoảng cách semantic

        if not documents_list:
            return []

        all_chunks = [
            {
                "content": doc,
                "filename": meta.get("filename", "Unnamed"),
                "file_path": meta.get("file_path", "N/A"),
                "distance": distance
            }
            for doc, meta, distance in zip(documents_list, metadatas_list, distances_list)
        ]

       # Rerank bằng BM25 nếu không lọc theo filename
        if not filename_query:
            tokenized_chunks = [word_tokenize(chunk["content"], format="text").split() for chunk in all_chunks]
            bm25 = BM25Okapi(tokenized_chunks)
            tokenized_query = word_tokenize(query, format="text").split()
            bm25_scores = bm25.get_scores(tokenized_query)
            best_chunks = sorted(
                zip(all_chunks, bm25_scores),
                key=lambda x: (1 - x[0]["distance"]) * 0.7 + x[1] * 0.3,
                reverse=True
            )[:top_k]
        else:
            best_chunks = [(chunk, 0) for chunk in all_chunks[:top_k]]  # Giữ nguyên nếu lọc filename

        relevant_docs = [
            RelevantDoc(
                filename=chunk["filename"],
                file_path=chunk["file_path"],
                content=chunk["content"]
            )
            for chunk, _ in best_chunks
        ]
        print(best_chunks)
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
