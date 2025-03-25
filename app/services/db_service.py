# app/services/db_service.py
from sqlalchemy.orm import Session
from app.db.postgre_sql.database import Session as SessionModel, Message
import uuid

def get_session_by_id(db: Session, session_id: uuid.UUID) -> SessionModel:
    """Lấy session theo session_id, trả về None nếu không tồn tại."""
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()

def create_new_session(db: Session, user_id: str) -> SessionModel:
    """Tạo một session mới."""
    session = SessionModel(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def save_message(db: Session, session_id: uuid.UUID, role: str, content: str):
    """Lưu tin nhắn vào session."""
    message = Message(session_id=session_id, role=role, content=content)
    db.add(message)


    
    db.commit()
    db.refresh(message)

def get_or_create_session(db: Session, user_id: str, session_id: uuid.UUID | None) -> SessionModel:
    """Lấy hoặc tạo session dựa trên session_id."""
    if session_id is not None:
        session = get_session_by_id(db, session_id)
        if not session:
            raise ValueError(f"Session với ID {session_id} không tồn tại.")
        return session
    else:
        return create_new_session(db, user_id)
    

def get_messages_by_session_id(db: Session, session_id: uuid.UUID, page: int, limit: int):
    """Lấy danh sách tin nhắn theo session_id có phân trang."""
    offset = (page - 1) * limit  # Tính vị trí bắt đầu
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.timestamp.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_messages = db.query(Message).filter(Message.session_id == session_id).count()
    
    return messages, total_messages


def get_list_session(db: Session, user_id: str, page: int, limit: int):
    """Lấy danh sách tin nhắn theo session_id có phân trang."""
    offset = (page - 1) * limit  # Tính vị trí bắt đầu
    sessions = (
        db.query(SessionModel)
        .filter(SessionModel.user_id == user_id)
        .order_by(SessionModel.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    for session in sessions:
        first_message = (
            db.query(Message)
            .filter(Message.session_id == session.id, Message.role == 'user')
            .order_by(Message.timestamp.desc())
            .first()
        )
        session.first_message = first_message

    total_sessions = db.query(SessionModel).filter(SessionModel.user_id == user_id).count()
    
    return sessions, total_sessions