from app.db.database import collection

# Lấy thông tin tài liệu với id cụ thể
doc_id = "Cv 114_1.pdf-0"  # Thay bằng id bạn muốn
result = collection.get(ids=[doc_id], include=["documents", "metadatas", "embeddings"])

if result["ids"]:
    doc = result["documents"][0]
    meta = result["metadatas"][0]
    print(f"ID: {result['ids'][0]}")
    print(f"Filename: {meta['filename']}")
    print(f"Content: {doc[:500]}...")
    if "embeddings" in result:
        print(f"Embedding: {result['embeddings'][0][:5]}...")  # In một phần embedding
else:
    print(f"Không tìm thấy tài liệu với id: {doc_id}")