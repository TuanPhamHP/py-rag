# app/api/chat.py
import openai
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession
from typing import List, Dict
import os
from dotenv import load_dotenv
import uuid

from app.services.search import retrieve_context
from utils.normalize import normalize_relevant_docs_scripts
from app.db.postgre_sql.database import get_db, SessionLocal
from app.services.db_service import get_or_create_session, save_message, get_messages_by_session_id, get_list_session

# Load biến môi trường
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Khởi tạo router và client OpenAI
router = APIRouter()
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

# Từ khóa để kích hoạt RAG
RAG_KEYWORDS = ["tài liệu", "nội bộ", "hồ sơ", "báo cáo", "file", "tệp tin", "tìm", "tra cứu", "thông tin", "dữ liệu"]

async def should_use_rag(question: str) -> bool:
    """Kiểm tra xem có nên dùng RAG dựa trên từ khóa trong câu hỏi."""
    return any(keyword in question.lower() for keyword in RAG_KEYWORDS)

def create_base_prompt() -> str:
    """Tạo phần prompt cơ bản."""
    return """
    Bạn là một chatbot AI. Trả lời câu hỏi của người dùng một cách chuyên nghiệp, rõ ràng.
    Nội dung trả lời luôn dùng HTML5, không dùng Markdown.
    - Title dùng thẻ <h1> đến <h6>.
    - Danh sách dùng <ul><li></li></ul>.
    - So sánh tiêu chí dùng bảng <table>.
    """

def generate_prompt(question: str, context: str = "") -> str:
    """Tạo prompt đầy đủ từ câu hỏi và context."""
    base_prompt = create_base_prompt()
    if context:
        base_prompt += f"<p><strong>Dữ liệu nội bộ:</strong> {context}</p><p>Sử dụng dữ liệu này làm nguồn chính nếu liên quan.</p>"
    else:
        base_prompt += "<p>Không có dữ liệu nội bộ. Trả lời dựa trên kiến thức chung.</p>"
    return f"{base_prompt}<p><strong>Câu hỏi:</strong> {question}</p>"

async def stream_response(prompt: str, context_messages: List[Dict]):
    """Tạo stream trả lời từ OpenAI."""
    messages = [*context_messages, {"role": "user", "content": prompt}]
    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        stream=True
    )
    return response

@router.post("/", response_class=StreamingResponse)
async def chat_with_gpt(request: Request, db: DBSession = Depends(get_db)):
    """Xử lý yêu cầu chat, stream trả lời và lưu cả câu hỏi lẫn trả lời vào DB."""
    # Lấy dữ liệu từ request
    data = await request.json()
    list_msg = data.get("listMsg", [])
    user_id = request.headers.get("user_id")
    session_id_str = data.get("session_id")  # Lấy session_id từ body request

    # Validate input
    if not user_id:
        raise HTTPException(status_code=401, detail="user_id header is required")
    if not list_msg or not isinstance(list_msg, list):
        raise HTTPException(status_code=400, detail="listMsg must be a non-empty list")

    # Chuyển session_id từ str sang UUID nếu có, hoặc None nếu không có
    session_id = uuid.UUID(session_id_str) if session_id_str else None

    # Tách câu hỏi hiện tại và context trước đó
    user_question = list_msg[-1]["content"]
    context_messages = list_msg[:-1]

    # Tạo hoặc lấy session từ DB
    session = get_or_create_session(db, user_id, session_id)
    session_id = session.id  # Lưu session_id dưới dạng UUID
    print(f"Session ID: {session_id}")

    # Lưu câu hỏi của user
    save_message(db, session_id, "user", user_question)

    # Quyết định dùng RAG và lấy context nếu cần
    use_rag = await should_use_rag(user_question)
    retrieved_context = ""
    if use_rag:
        retrieved_docs = await retrieve_context(user_question)
        retrieved_context = normalize_relevant_docs_scripts(retrieved_docs)
        print(f"Số tài liệu liên quan: {len(retrieved_context)}")
    else:
        print("Không dùng RAG, trả lời dựa trên kiến thức chung.")

    # Tạo prompt và stream trả lời
    prompt = generate_prompt(user_question, retrieved_context)
    response = await stream_response(prompt, context_messages)

    # Stream và thu thập full_response, lưu với session mới
    async def stream_and_save():
        # Gửi session_id trước tiên dưới dạng JSON
        session_data = f"\"session_id\": \"{str(session_id)}\"\n\n end_session_id\""
        yield session_data

        full_response = ""
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                # Gửi từng chunk dưới dạng plain text
                yield content
        
        # Lưu câu trả lời vào DB
        with SessionLocal() as new_db:
            try:
                save_message(new_db, session_id, "system", full_response)
                print(f"Đã lưu câu trả lời: {full_response[:50]}...")
            except Exception as e:
                print(f"Lỗi khi lưu câu trả lời: {e}")

    return StreamingResponse(stream_and_save(), media_type="text/event-stream")

@router.get("/history")
async def get_chat_history(
    s_id: str,
    page: int = Query(1, alias="page", ge=1),  # Mặc định page = 1, không cho phép nhỏ hơn 1
    limit: int = Query(10, alias="limit", ge=1, le=100),  # Giới hạn số bản ghi (tối đa 100)
    db: DBSession = Depends(get_db)
):
    """API lấy lịch sử tin nhắn theo session_id có phân trang."""
    try:
        session_id = uuid.UUID(s_id)  # Chuyển đổi session_id thành UUID
    except ValueError:
        raise HTTPException(status_code=400, detail="Session ID không hợp lệ")

    messages, total = get_messages_by_session_id(db, session_id, page, limit)
    
    if not messages:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin nhắn cho session_id này")
    
    return {
        "session_id": s_id,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "messages": [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp} for msg in messages]
    }

@router.get("/sessions")
async def get_chat_sessions(
    request: Request,
    page: int = Query(1, alias="page", ge=1), 
    limit: int = Query(10, alias="limit", ge=1, le=100), 
    db: DBSession = Depends(get_db)
):
    """API lấy lịch sử tin nhắn theo session_id có phân trang."""
    user_id = request.headers.get("user_id")
    sessions, total = get_list_session(db, user_id, page, limit)
    
    if not sessions:
        raise HTTPException(status_code=404, detail="Không tìm thấy sessions cho user_id này")
    
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "sessions": sessions
    }