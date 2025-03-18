import chromadb
import os

CHROMA_DB_PATH = os.path.abspath("./app/db/chromadb_store")

def clear_chromadb():
    """Xóa toàn bộ collections trong ChromaDB."""
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    collection_names = chroma_client.list_collections()  # Chỉ trả về danh sách tên
    if not collection_names:
        print("✅ ChromaDB đã sạch, không có collection nào.")
        return
    
    for name in collection_names:
        print(f"🗑 Đang xóa collection: {name}")
        chroma_client.delete_collection(name=name)  # Xóa bằng tên

    print("✅ Đã xóa toàn bộ dữ liệu trong ChromaDB.")
    
    # Kiểm tra lại danh sách collections sau khi xóa
    collection_names_after = [col.name for col in chroma_client.list_collections()]
    print("📂 Collections sau khi xóa:", collection_names_after)

if __name__ == "__main__":
    clear_chromadb()
