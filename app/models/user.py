from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    system_info = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Mối quan hệ
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship(
        "SessionData", back_populates="user", cascade="all, delete-orphan"
    )
    reports = relationship(
        "EmotionReport", back_populates="user", cascade="all, delete-orphan"
    )
