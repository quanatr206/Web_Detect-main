import cv2
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import json
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from config import MODEL_PATH, EMOTION_LABELS


class EmotionDetector:
    def __init__(self, model_path=MODEL_PATH):
        # Khởi tạo TensorRT engine
        self.model_path = model_path
        self.logger = trt.Logger(trt.Logger.WARNING)
        self.runtime = trt.Runtime(self.logger)

        # Tải model TensorRT
        with open(self.model_path, "rb") as f:
            self.engine = self.runtime.deserialize_cuda_engine(f.read())

        self.context = self.engine.create_execution_context()

        # Lấy kích thước đầu vào
        self.input_shape = None
        for binding in range(self.engine.num_bindings):
            if self.engine.binding_is_input(binding):
                self.input_shape = self.engine.get_binding_shape(binding)
                break

        if self.input_shape is None:
            raise ValueError("Không tìm thấy input binding trong model TensorRT")

        # Khởi tạo face detector từ OpenCV
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def preprocess_frame(self, frame):
        """
        Tiền xử lý khung hình để chuẩn bị cho việc nhận diện cảm xúc
        """
        # Chuyển sang ảnh xám
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Nhận diện khuôn mặt
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        processed_faces = []
        face_locations = []

        for x, y, w, h in faces:
            # Cắt vùng khuôn mặt
            face_roi = gray[y : y + h, x : x + w]

            # Resize theo kích thước đầu vào của model
            input_height, input_width = self.input_shape[
                2:
            ]  # Dạng [batch_size, channels, height, width]
            resized_face = cv2.resize(face_roi, (input_width, input_height))

            # Chuẩn hóa
            normalized_face = resized_face / 255.0

            # Chuyển về định dạng NCHW [batch, channels, height, width]
            processed_face = np.expand_dims(
                np.expand_dims(normalized_face, axis=0), axis=0
            ).astype(np.float32)

            processed_faces.append(processed_face)
            face_locations.append((x, y, w, h))

        return processed_faces, face_locations

    def detect_emotion(self, frame):
        """
        Nhận diện cảm xúc từ khung hình
        """
        # Tiền xử lý khung hình
        processed_faces, face_locations = self.preprocess_frame(frame)

        results = []

        for i, face in enumerate(processed_faces):
            # Chuẩn bị bộ nhớ đầu vào và đầu ra
            input_memory = cuda.mem_alloc(face.nbytes)
            output = np.empty((1, len(EMOTION_LABELS)), dtype=np.float32)
            output_memory = cuda.mem_alloc(output.nbytes)

            # Sao chép dữ liệu đầu vào vào GPU
            cuda.memcpy_htod(input_memory, face)

            # Thực thi model
            bindings = [int(input_memory), int(output_memory)]
            self.context.execute_v2(bindings)

            # Sao chép dữ liệu đầu ra từ GPU
            cuda.memcpy_dtoh(output, output_memory)

            # Giải phóng bộ nhớ
            input_memory.free()
            output_memory.free()

            # Xử lý kết quả
            emotion_idx = np.argmax(output)
            emotion = EMOTION_LABELS[emotion_idx]
            confidence = float(output[0][emotion_idx])

            # Lưu kết quả
            x, y, w, h = face_locations[i]
            result = {
                "emotion": emotion,
                "confidence": confidence,
                "face_coordinates": {
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                },
            }
            results.append(result)

        return results

    def process_video(self, video_path, interval=1.0):
        """
        Xử lý video và trích xuất cảm xúc theo khoảng thời gian

        Args:
            video_path: Đường dẫn đến file video
            interval: Khoảng thời gian (giây) giữa các lần nhận diện

        Returns:
            List các kết quả nhận diện cảm xúc theo thời gian
        """
        # Mở file video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Không thể mở file video: {video_path}")

        # Lấy thông tin video
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps

        # Tính số frame cần nhảy qua giữa các lần nhận diện
        frames_per_interval = int(fps * interval)

        results = []
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Chỉ xử lý frame theo khoảng thời gian
            if frame_idx % frames_per_interval == 0:
                # Tính thời điểm hiện tại trong video
                current_time = frame_idx / fps

                # Nhận diện cảm xúc
                emotion_results = self.detect_emotion(frame)

                # Thêm thông tin thời gian vào kết quả
                for result in emotion_results:
                    result["timestamp"] = current_time
                    results.extend(emotion_results)

            frame_idx += 1

        cap.release()

        return results, duration
