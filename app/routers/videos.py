from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import sys

sys.path.append("C:/Users/ha161/CodeTest/TTTTN/app")
from database import get_db
from models.user import User
from models.video import Video, EmotionData
from schemas.video import VideoResponse, EmotionDataResponse, VideoAnalysisResponse
from utils.security import get_current_user
from services.video_service import VideoService

router = APIRouter(prefix="/videos", tags=["videos"])

video_service = VideoService()


@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tải lên video và xử lý nhận diện cảm xúc
    """
    # Kiểm tra định dạng file
    if not file.filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ hỗ trợ các định dạng video: MP4, AVI, MOV, MKV",
        )

    # Lưu video và xử lý nhận diện cảm xúc
    video = await video_service.save_video(file, current_user.id, db)

    return video


@router.get("/", response_model=List[VideoResponse])
def get_user_videos(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Lấy danh sách video của người dùng
    """
    videos = db.query(Video).filter(Video.user_id == current_user.id).all()
    return videos


@router.get("/{video_id}", response_model=VideoResponse)
def get_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy thông tin chi tiết về video
    """
    video = (
        db.query(Video)
        .filter(Video.id == video_id, Video.user_id == current_user.id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video không tồn tại hoặc không thuộc về người dùng này",
        )

    return video


@router.get("/{video_id}/emotions", response_model=List[EmotionDataResponse])
def get_video_emotions(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy dữ liệu cảm xúc từ video
    """
    # Kiểm tra xem video có tồn tại và thuộc về người dùng hiện tại không
    video = (
        db.query(Video)
        .filter(Video.id == video_id, Video.user_id == current_user.id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video không tồn tại hoặc không thuộc về người dùng này",
        )

    # Lấy dữ liệu cảm xúc
    emotions = db.query(EmotionData).filter(EmotionData.video_id == video_id).all()

    return emotions


@router.get("/{video_id}/analysis", response_model=VideoAnalysisResponse)
def analyze_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Phân tích cảm xúc từ video
    """
    # Kiểm tra xem video có tồn tại và thuộc về người dùng hiện tại không
    video = (
        db.query(Video)
        .filter(Video.id == video_id, Video.user_id == current_user.id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video không tồn tại hoặc không thuộc về người dùng này",
        )

    # Phân tích cảm xúc
    analysis = video_service.analyze_video_emotions(video_id, db)

    return analysis
