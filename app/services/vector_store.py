from utils.file_reader import load_all_files
from dotenv import load_dotenv
import tiktoken
from app.db.chromadb_store.chromadb_client import generate_embedding 
from app.db.database import collection 
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

def split_text(text, model="text-embedding-3-large", chunk_size=4000, chunk_overlap=400):
    enc = tiktoken.encoding_for_model(model)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=lambda x: len(enc.encode(x))
    )
    chunks = splitter.split_text(text)
    return chunks

def save_documents_to_chroma():
    """Đọc toàn bộ file và lưu vào ChromaDB"""
    documents = load_all_files()
    if not documents:
        print("❌ Không có tài liệu nào để xử lý.")
        return

    ids, processed_contents, processed_metadata,embeddings = [], [], [], []
    for doc in documents:
        chunks = split_text(doc["content"])  # Chia nhỏ nội dung
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['id']}-{i}"  # Định danh duy nhất từng đoạn
            ids.append(chunk_id)
            processed_contents.append(chunk)
            processed_metadata.append({"filename": doc["id"], "chunk_index": i, "file_path": doc["file_path"]})
            embedding = generate_embedding(chunk)
            embeddings.append(embedding)

    # Kiểm tra số lượng phần tử trước khi thêm vào ChromaDB
    if not (len(ids) == len(processed_contents) == len(processed_metadata)== len(embeddings)):
        print(f"❌ Số lượng phần tử không khớp: ids={len(ids)}, documents={len(processed_contents)}, metadatas={len(processed_metadata)}")
        return

    try:
        collection.add(
            ids=ids, 
            documents=processed_contents, 
            metadatas=processed_metadata,
            embeddings=embeddings 
        )
        print(f"✅ Đã lưu {len(processed_contents)} đoạn văn bản vào ChromaDB.")
    except Exception as e:
        print(f"❌ Lỗi khi lưu vào ChromaDB: {e}")

if __name__ == "__main__":
    save_documents_to_chroma()


# def process_and_store():
#     """Đọc toàn bộ file, chia nhỏ văn bản và lưu vào ChromaDB"""
#     documents = load_all_files()
#     if not documents:
#         print("❌ Không có tài liệu nào để xử lý.")
#         return

#     ids, processed_contents, processed_metadata = [], [], []

#     for doc in documents:
#         chunks = split_text(doc["content"])  # Chia nhỏ nội dung
#         for i, chunk in enumerate(chunks):
#             chunk_id = f"{doc['id']}-{i}"  # Định danh duy nhất từng đoạn
#             ids.append(chunk_id)
#             processed_contents.append(chunk)
#             processed_metadata.append({"filename": doc["id"], "chunk_index": i})

#     # Kiểm tra số lượng phần tử trước khi thêm vào ChromaDB
#     if not (len(ids) == len(processed_contents) == len(processed_metadata)):
#         print(f"❌ Số lượng phần tử không khớp: ids={len(ids)}, documents={len(processed_contents)}, metadatas={len(processed_metadata)}")
#         return

#     try:
#         collection.add(ids=ids, documents=processed_contents, metadatas=processed_metadata)
#         print(f"✅ Đã lưu {len(processed_contents)} đoạn văn bản vào ChromaDB.")
#     except Exception as e:
#         print(f"❌ Lỗi khi lưu vào ChromaDB: {e}")


# if __name__ == "__main__":
#     save_documents_to_chroma()
