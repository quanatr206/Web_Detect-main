from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class VideoBase(BaseModel):
    filename: str
    filepath: str
    duration: float


class VideoCreate(VideoBase):
    pass


class VideoResponse(VideoBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


class EmotionDataBase(BaseModel):
    timestamp: float
    emotion: str
    confidence: float
    face_coordinates: Dict[str, Any]


class EmotionDataCreate(EmotionDataBase):
    video_id: int


class EmotionDataResponse(EmotionDataBase):
    id: int
    video_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


class VideoAnalysisResponse(BaseModel):
    video_id: int
    total_emotions_detected: int
    emotion_counts: Dict[str, int]
    emotion_percentages: Dict[str, float]
    dominant_emotion: str
    focus_score: float
    engagement_score: float


class EmotionReportCreate(BaseModel):
    user_id: int
    report_date: datetime
    total_sessions: int
    total_duration_minutes: int
    happy_percentage: float
    sad_percentage: float
    angry_percentage: float
    surprised_percentage: float
    neutral_percentage: float
    focused_percentage: float
    average_engagement: float


class EmotionReportResponse(EmotionReportCreate):
    id: int
    
    class Config:
        orm_mode = True