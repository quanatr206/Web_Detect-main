from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta

from ..database import get_db, SessionLocal
from ..models.user import User
from ..models.video import SessionData, EmotionReport
from ..schemas.video import EmotionReportResponse
from ..utils.security import get_current_user

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)


@router.post("/session", status_code=status.HTTP_201_CREATED)
def create_session(
    session_name: str,
    dominant_emotion: str = None,
    focus_score: float = 0,
    engagement_score: float = 0,
    notes: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo một phiên học tập mới
    """
    session = SessionData(
        user_id=current_user.id,
        session_name=session_name,
        dominant_emotion=dominant_emotion,
        focus_score=focus_score,
        engagement_score=engagement_score,
        notes=notes
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {"id": session.id, "message": "Đã tạo phiên học tập mới"}


@router.put("/session/{session_id}/end")
def end_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kết thúc phiên học tập và cập nhật thời lượng
    """
    session = db.query(SessionData).filter(
        SessionData.id == session_id,
        SessionData.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phiên học tập không tồn tại hoặc không thuộc về người dùng này"
        )
    
    if session.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phiên học tập đã kết thúc"
        )
    
    # Cập nhật thời gian kết thúc
    session.end_time = datetime.now()
    
    # Tính thời lượng (phút)
    duration = (session.end_time - session.start_time).total_seconds() / 60
    session.duration_minutes = round(duration)
    
    db.commit()
    db.refresh(session)
    
    return {
        "id": session.id,
        "duration_minutes": session.duration_minutes,
        "message": "Đã kết thúc phiên học tập"
    }


@router.get("/sessions", response_model=List[dict])
def get_user_sessions(
    start_date: date = None,
    end_date: date = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách phiên học tập của người dùng theo khoảng thời gian
    """
    query = db.query(SessionData).filter(SessionData.user_id == current_user.id)
    
    if start_date:
        query = query.filter(SessionData.start_time >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        query = query.filter(SessionData.start_time <= datetime.combine(end_date, datetime.max.time()))
    
    sessions = query.order_by(SessionData.start_time.desc()).all()
    
    result = []
    for session in sessions:
        session_dict = {
            "id": session.id,
            "session_name": session.session_name,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "duration_minutes": session.duration_minutes,
            "dominant_emotion": session.dominant_emotion,
            "focus_score": session.focus_score,
            "engagement_score": session.engagement_score
        }
        result.append(session_dict)
    
    return result


@router.get("/daily", response_model=List[EmotionReportResponse])
def get_daily_reports(
    start_date: date = None,
    end_date: date = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy báo cáo cảm xúc hàng ngày trong khoảng thời gian
    """
    # Nếu không có ngày bắt đầu, mặc định lấy dữ liệu của 7 ngày gần nhất
    if not start_date:
        start_date = date.today() - timedelta(days=6)
    
    # Nếu không có ngày kết thúc, mặc định là ngày hiện tại
    if not end_date:
        end_date = date.today()
    
    reports = db.query(EmotionReport).filter(
        EmotionReport.user_id == current_user.id,
        EmotionReport.report_date >= start_date,
        EmotionReport.report_date <= end_date
    ).order_by(EmotionReport.report_date).all()
    
    return reports


@router.post("/generate-daily-report", status_code=status.HTTP_201_CREATED)
def generate_daily_report(
    report_date: date = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo hoặc cập nhật báo cáo cảm xúc cho một ngày cụ thể
    """
    # Nếu không có ngày báo cáo, mặc định là ngày hiện tại
    if not report_date:
        report_date = date.today()
    
    # Kiểm tra xem báo cáo đã tồn tại chưa
    existing_report = db.query(EmotionReport).filter(
        EmotionReport.user_id == current_user.id,
        EmotionReport.report_date == report_date
    ).first()
    
    # Lấy tất cả các phiên học tập trong ngày
    start_datetime = datetime.combine(report_date, datetime.min.time())
    end_datetime = datetime.combine(report_date, datetime.max.time())
    
    sessions = db.query(SessionData).filter(
        SessionData.user_id == current_user.id,
        SessionData.start_time >= start_datetime,
        SessionData.start_time <= end_datetime,
        SessionData.end_time.isnot(None)  # Chỉ lấy các phiên đã kết thúc
    ).all()
    
    if not sessions:
        if existing_report:
            return {"message": "Báo cáo đã tồn tại và không có phiên học tập mới"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không có phiên học tập nào trong ngày này"
            )
    
    # Tính toán các chỉ số báo cáo
    total_sessions = len(sessions)
    total_duration = sum(session.duration_minutes for session in sessions)
    
    # Tính phần trăm các cảm xúc
    emotion_counts = {"happy": 0, "sad": 0, "angry": 0, "surprise": 0, "neutral": 0}
    focus_scores = []
    engagement_scores = []
    
    for session in sessions:
        # Đếm cảm xúc
        if session.dominant_emotion and session.dominant_emotion in emotion_counts:
            emotion_counts[session.dominant_emotion] += 1
        
        # Thêm điểm tập trung và tương tác
        if session.focus_score is not None:
            focus_scores.append(session.focus_score)
        if session.engagement_score is not None:
            engagement_scores.append(session.engagement_score)
    
    # Tính phần trăm các cảm xúc
    happy_percentage = (emotion_counts["happy"] / total_sessions) * 100 if total_sessions > 0 else 0
    sad_percentage = (emotion_counts["sad"] / total_sessions) * 100 if total_sessions > 0 else 0
    angry_percentage = (emotion_counts["angry"] / total_sessions) * 100 if total_sessions > 0 else 0
    surprised_percentage = (emotion_counts["surprise"] / total_sessions) * 100 if total_sessions > 0 else 0
    neutral_percentage = (emotion_counts["neutral"] / total_sessions) * 100 if total_sessions > 0 else 0
    
    # Tính điểm tập trung và tương tác trung bình
    focused_percentage = sum(focus_scores) / len(focus_scores) if focus_scores else 0
    average_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
    
    # Tạo hoặc cập nhật báo cáo
    if existing_report:
        existing_report.total_sessions = total_sessions
        existing_report.total_duration_minutes = total_duration
        existing_report.happy_percentage = happy_percentage
        existing_report.sad_percentage = sad_percentage
        existing_report.angry_percentage = angry_percentage
        existing_report.surprised_percentage = surprised_percentage
        existing_report.neutral_percentage = neutral_percentage
        existing_report.focused_percentage = focused_percentage
        existing_report.average_engagement = average_engagement
        
        db.commit()
        db.refresh(existing_report)
        report = existing_report
    else:
        new_report = EmotionReport(
            user_id=current_user.id,
            report_date=report_date,
            total_sessions=total_sessions,
            total_duration_minutes=total_duration,
            happy_percentage=happy_percentage,
            sad_percentage=sad_percentage,
            angry_percentage=angry_percentage,
            surprised_percentage=surprised_percentage,
            neutral_percentage=neutral_percentage,
            focused_percentage=focused_percentage,
            average_engagement=average_engagement
        )
        
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        report = new_report
    
    return {
        "id": report.id,
        "report_date": report.report_date,
        "total_sessions": report.total_sessions,
        "total_duration_minutes": report.total_duration_minutes,
        "message": "Đã tạo/cập nhật báo cáo cảm xúc hàng ngày"
    }