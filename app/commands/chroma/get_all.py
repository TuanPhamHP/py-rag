from app.db.chromadb_store.chromadb_client import chroma_client

# Lấy danh sách collections (trả về list[str])
collections = chroma_client.list_collections()

print("📂 Collections hiện có:", collections)

for col_name in collections:
    collection = chroma_client.get_collection(col_name)
    docs = collection.get(include=["embeddings", "metadatas"])
    count = len(docs["ids"])
    print(f"📄 Số dữ liệu trong Collection '{col_name}':", count)
    # print(f"📄 Dữ liệu trong Collection '{col_name}':", docs)



