import os
import uuid
import cv2
import json
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

# from ..models.video import Video, EmotionData
# from ..services.emotion_detector import EmotionDetector
# from ..config import UPLOAD_FOLDER

from ...app.models.video import Video, EmotionData
from app.services.emotion_detector import EmotionDetector
from app.config import UPLOAD_FOLDER


class VideoService:
    def __init__(self):
        # Đảm bảo thư mục upload tồn tại
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        self.emotion_detector = EmotionDetector()

    async def save_video(self, file: UploadFile, user_id: int, db: Session):
        """
        Lưu video đã tải lên, xử lý nhận diện cảm xúc và lưu kết quả vào database
        """
        # Tạo tên tệp duy nhất
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        # Lưu file tải lên
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        try:
            # Xử lý video để nhận diện cảm xúc
            emotion_results, duration = self.emotion_detector.process_video(file_path)

            # Lưu thông tin video vào database
            db_video = Video(
                user_id=user_id,
                filename=unique_filename,
                filepath=file_path,
                duration=duration,
            )
            db.add(db_video)
            db.commit()
            db.refresh(db_video)

            # Lưu kết quả nhận diện cảm xúc vào database
            for result in emotion_results:
                # Chuyển đổi tọa độ khuôn mặt sang chuỗi JSON
                face_coordinates = json.dumps(result["face_coordinates"])

                db_emotion = EmotionData(
                    video_id=db_video.id,
                    timestamp=result["timestamp"],
                    emotion=result["emotion"],
                    confidence=result["confidence"],
                    face_coordinates=face_coordinates,
                )
                db.add(db_emotion)

            db.commit()

            return db_video

        except Exception as e:
            # Nếu có lỗi, xóa file đã tải lên
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500, detail=f"Lỗi khi xử lý video: {str(e)}"
            )

    def analyze_video_emotions(self, video_id: int, db: Session):
        """
        Phân tích thống kê cảm xúc từ video đã xử lý
        """
        # Lấy tất cả dữ liệu cảm xúc của video
        emotion_data = (
            db.query(EmotionData).filter(EmotionData.video_id == video_id).all()
        )

        if not emotion_data:
            raise HTTPException(
                status_code=404, detail="Không tìm thấy dữ liệu cảm xúc cho video này"
            )

        # Đếm số lượng từng loại cảm xúc
        emotion_counts = {}
        for data in emotion_data:
            emotion = data.emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Tính phần trăm cho từng loại cảm xúc
        total_emotions = sum(emotion_counts.values())
        emotion_percentages = {
            emotion: (count / total_emotions) * 100
            for emotion, count in emotion_counts.items()
        }

        # Tính thời gian trung bình cho mỗi cảm xúc
        emotion_times = {}
        for data in emotion_data:
            emotion = data.emotion
            if emotion not in emotion_times:
                emotion_times[emotion] = []
            emotion_times[emotion].append(data.timestamp)

        # Cảm xúc chiếm ưu thế
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]

        # Tính điểm tập trung (focus score) dựa trên các cảm xúc tích cực
        focus_emotions = ["happy", "neutral", "surprise"]
        focus_count = sum(emotion_counts.get(emotion, 0) for emotion in focus_emotions)
        focus_score = (focus_count / total_emotions) * 10  # Thang điểm từ 0-10

        # Tính điểm tương tác (engagement score)
        engagement_score = 10 - (emotion_counts.get("neutral", 0) / total_emotions) * 10

        result = {
            "video_id": video_id,
            "total_emotions_detected": total_emotions,
            "emotion_counts": emotion_counts,
            "emotion_percentages": emotion_percentages,
            "dominant_emotion": dominant_emotion,
            "focus_score": focus_score,
            "engagement_score": engagement_score,
        }

        return result
