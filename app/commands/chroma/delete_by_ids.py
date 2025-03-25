from app.db.database import collection

def delete_specific_docs(doc_ids):
    """Xóa các tài liệu cụ thể trong ChromaDB dựa trên danh sách ids."""
    try:
        # Xóa các ids được chỉ định
        collection.delete(ids=doc_ids)
        print(f"✅ Đã xóa thành công {len(doc_ids)} tài liệu: {doc_ids}")
    except Exception as e:
        print(f"❌ Lỗi khi xóa tài liệu: {e}")

if __name__ == "__main__":
    # Danh sách ids cần xóa
    ids_to_delete = ["Cv 114_1.pdf-0", "Cv 114_1.pdf-1"]
    delete_specific_docs(ids_to_delete)