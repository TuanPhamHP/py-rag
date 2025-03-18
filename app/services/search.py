import chromadb
from app.db.chromadb_store.chromadb_client import generate_embedding  # Import hàm đã có

# Khởi tạo ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db") 
collection = chroma_client.get_or_create_collection(name="documents")

def search_documents(query: str, top_k: int = 5):
    """Tìm kiếm văn bản gần nhất trong ChromaDB"""
    query_embedding = generate_embedding(query)  # Dùng hàm có sẵn

    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=top_k
    )

    return results
