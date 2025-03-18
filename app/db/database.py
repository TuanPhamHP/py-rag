
import os
import chromadb
# from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

CHROMA_DB_PATH = os.path.abspath("./app/db/chromadb_store")
COLLECTION_NAME = "documents"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Khởi tạo ChromaDB Client
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)

# Xuất biến để dùng ở nơi khác
__all__ = ["collection"]