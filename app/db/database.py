import chromadb

# Tạo PersistentClient để lưu dữ liệu vào thư mục "chroma_db"
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")
