# app/db/database.py
import chromadb
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# ChromaDB setup (giả định từ code hiện tại của bạn)
chroma_client = chromadb.Client()
chroma_collection = chroma_client.create_collection("rag_collection")  # Ví dụ, tùy theo code của bạn

# PostgreSQL setup
DATABASE_URL = "postgresql://chatbot_user:your_password@localhost:5432/chatbot_db"
pg_engine = create_engine(DATABASE_URL)
PgSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)

Base = declarative_base()

# Model cho bảng sessions
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="session")

# Model cho bảng messages
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" hoặc "system"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")

# Tạo bảng trong PostgreSQL
Base.metadata.create_all(bind=pg_engine)

# Hàm để lấy session database cho PostgreSQL
def get_pg_db():
    db = PgSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Hàm để lấy ChromaDB collection (giả định từ code của bạn)
def get_chroma_collection():
    return chroma_collection