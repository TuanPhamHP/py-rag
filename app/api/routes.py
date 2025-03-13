from fastapi import APIRouter
from app.services.vector_store import process_and_store, search_query

router = APIRouter()

@router.post("/upload/")
async def upload_file(text: str):
    message = process_and_store(text)
    return {"message": message}

@router.get("/search/")
async def search(query: str):
    results = search_query(query)
    return {"query": query, "results": results}
