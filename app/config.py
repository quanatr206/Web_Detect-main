import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Cấu hình cơ sở dữ liệu
DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root:@localhost/emotion_detection"
)

# Cấu hình bảo mật
SECRET_KEY = os.getenv("SECRET_KEY", "thuc-tap-program")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Cấu hình đường dẫn
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
MODEL_PATH = os.getenv(
    "MODEL_PATH", "C:/Users/ha161/CodeTest/TTTTN/app/model/emotion_model.trt"
)

# Cấu hình TensorRT
EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
