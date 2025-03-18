from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.db.database import collection
from app.db.chromadb_store.chromadb_client import generate_embedding
from app.schemas.search import SearchQuery
from app.services.search import search_documents

router = APIRouter()


@router.get("/")
async def search(q: str = Query(..., min_length=1)):
    try:
        query_embedding = generate_embedding(q)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "metadatas"]
        )

        documents_list = results.get("documents", [[]])[0]  # Danh sách tài liệu
        metadatas_list = results.get("metadatas", [[]])[0]  # Danh sách metadata
        formatted_results = []
        for doc, meta in zip(documents_list, metadatas_list):
            formatted_results.append({
                "document": doc,
                "metadata": meta,
                "file_path": meta.get("file_path", "N/A")  # Thêm đường dẫn file
            })

        return JSONResponse(content=formatted_results)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/")
async def search(query_data: SearchQuery):
    results = search_documents(query_data.query, query_data.top_k)
    return {"matches": results}
