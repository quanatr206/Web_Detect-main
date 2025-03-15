document.addEventListener("DOMContentLoaded", function () {
  const studentVideo = document.getElementById("studentVideo");
  const emotionOverlay = document.getElementById("emotionOverlay");
  const btnEmotion = document.getElementById("btnEmotion");
  const btnEndCall = document.getElementById("btnEndCall");

  // Nhận diện cảm xúc giả lập bằng emoji
  const emotions = ["😊", "😐", "😞", "😃", "😢", "😲", "😠", "😴"];

  btnEmotion.addEventListener("click", () => {
    const randomEmotion = emotions[Math.floor(Math.random() * emotions.length)];
    emotionOverlay.textContent = randomEmotion;
  });

  // Mở camera
  navigator.mediaDevices
    .getUserMedia({ video: true, audio: false })
    .then((stream) => {
      studentVideo.srcObject = stream;
    })
    .catch((error) => {
      console.error("Lỗi mở camera: ", error);
    });

  // Hiển thị thời gian thực
  function updateTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, "0");
    const minutes = now.getMinutes().toString().padStart(2, "0");
    document.getElementById("currentTime").textContent = `${hours}:${minutes}`;
  }
  setInterval(updateTime, 1000);
  updateTime();

  // Sự kiện rời khỏi lớp
  btnEndCall.addEventListener("click", () => {
    alert("Bạn đã rời khỏi lớp học!");
    window.location.href = "https://www.google.com"; // Điều hướng về trang khác
  });
});
