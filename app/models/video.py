from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    filename = Column(String(255), nullable=False)
    filepath = Column(String(255), nullable=False)
    duration = Column(Float, default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Mối quan hệ
    user = relationship("User", back_populates="videos")
    emotion_data = relationship(
        "EmotionData", back_populates="video", cascade="all, delete-orphan"
    )


class EmotionData(Base):
    __tablename__ = "emotion_data"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    timestamp = Column(Float, nullable=False)
    emotion = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    face_coordinates = Column(String, nullable=True)  # JSON dạng string
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Mối quan hệ
    video = relationship("Video", back_populates="emotion_data")


class SessionData(Base):
    __tablename__ = "session_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    session_name = Column(String(255))
    start_time = Column(TIMESTAMP, server_default=func.current_timestamp())
    end_time = Column(TIMESTAMP, nullable=True)
    duration_minutes = Column(Integer, default=0)
    dominant_emotion = Column(String(20))
    focus_score = Column(Float, default=0)
    engagement_score = Column(Float, default=0)
    notes = Column(String, nullable=True)

    # Mối quan hệ
    user = relationship("User", back_populates="sessions")


class EmotionReport(Base):
    __tablename__ = "emotion_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    report_date = Column(TIMESTAMP, nullable=False)
    total_sessions = Column(Integer, default=0)
    total_duration_minutes = Column(Integer, default=0)
    happy_percentage = Column(Float, default=0)
    sad_percentage = Column(Float, default=0)
    angry_percentage = Column(Float, default=0)
    surprised_percentage = Column(Float, default=0)
    neutral_percentage = Column(Float, default=0)
    focused_percentage = Column(Float, default=0)
    average_engagement = Column(Float, default=0)

    # Mối quan hệ
    user = relationship("User", back_populates="reports")
