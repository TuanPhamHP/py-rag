from fastapi import FastAPI
import uvicorn
from app.api.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hoặc chỉ cho phép "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả phương thức (GET, POST, ...)
    allow_headers=["*"],  # Cho phép tất cả headers
)

# Thêm API endpoints từ router
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
