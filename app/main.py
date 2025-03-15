from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from app.database import engine, Base, SessionLocal
from app.routers import auth, videos, reports
from app.config import UPLOAD_FOLDER


# Khởi tạo các bảng trong cơ sở dữ liệu
Base.metadata.create_all(bind=engine)

# Tạo thư mục uploads nếu chưa tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Emotion Detection API",
    description="API đánh giá cảm xúc của người học trực tuyến dựa trên phân tích ảnh mặt người",
    version="1.0.0",
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các nguồn gốc trong môi trường phát triển
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký static folder để phục vụ các file đã tải lên
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# # Đăng ký các router
# app.include_router(auth.router)
# app.include_router(videos.router)
# app.include_router(reports.router)


@app.get("/")
def read_root():
    return {
        "message": "Hệ thống đánh giá cảm xúc của người học trực tuyến dựa trên phân tích ảnh mặt người",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
