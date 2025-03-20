from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import bcrypt
from app.auth.jwt_auth import create_access_token

DATABASE_URL = "sqlite:///app/db/chat_history.db"
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    auth_type = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    sessions = relationship("ChatSession", back_populates="user")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.session_id"))
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    session = relationship("ChatSession", back_populates="messages")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def add_user(user_id: str, username: str, auth_type: str, password: str = None):
    db = next(get_db())
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password else None
    user = User(user_id=user_id, username=username, auth_type=auth_type, password_hash=password_hash)
    db.add(user)
    try:
        db.commit()
    except:
        db.rollback()
    db.refresh(user)
    return user

async def verify_user(user_id: str, password: str = None) -> dict:
    """Xác minh người dùng và trả về token."""
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found"}
    
    if password and user.password_hash:
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
            return {"success": False, "message": "Invalid password"}
    elif password and not user.password_hash:
        return {"success": False, "message": "Password not set for this user"}
    
    access_token = create_access_token(data={"sub": user.user_id})
    return {"success": True, "access_token": access_token, "user_id": user.user_id}

async def create_session(user_id: str, title: str = "New Chat") -> int:
    db = next(get_db())
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session.session_id

async def add_message(session_id: int, role: str, content: str):
    db = next(get_db())
    message = Message(session_id=session_id, role=role, content=content)
    db.add(message)
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    session.updated_at = datetime.now()
    db.commit()

async def get_user_sessions(user_id: str) -> list:
    db = next(get_db())
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()).all()
    return [{"session_id": s.session_id, "title": s.title, "created_at": s.created_at.isoformat(), "updated_at": s.updated_at.isoformat()} for s in sessions]

async def get_session_messages(session_id: int) -> list:
    db = next(get_db())
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp.asc()).all()
    return [{"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()} for m in messages]

if __name__ == "__main__":
    init_db()