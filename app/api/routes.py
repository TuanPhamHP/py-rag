from fastapi import APIRouter
from app.api.search import router as search_router
from app.api.documents import router as documents_router

router = APIRouter()

router.include_router(search_router, prefix="/search", tags=["search"])
router.include_router(documents_router, prefix="/documents", tags=["documents"])
