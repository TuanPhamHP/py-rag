import chromadb

# Kết nối với ChromaDB và lưu dữ liệu vào thư mục "chromadb_store"
chroma_client = chromadb.PersistentClient(path="./app/db/chromadb_store")

# Tạo collection để lưu vector (tên là "documents")
collection = chroma_client.get_or_create_collection(name="documents")

def add_document(id: str, text: str, metadata: dict = {}):
    """Thêm dữ liệu vào vector database"""
    collection.add(
        ids=[id],
        documents=[text],
        metadatas=[metadata]
    )

def search(query: str, top_k: int = 3):
    """Tìm kiếm dữ liệu dựa trên vector"""
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results
