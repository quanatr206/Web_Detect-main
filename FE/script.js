const participants = [
  { name: "Học Viên 1", emotion: "" },
  { name: "Học Viên 2", emotion: "" },
  { name: "Học Viên 3", emotion: "" },
  { name: "Học Viên 4", emotion: "" },
  { name: "Học Viên 5", emotion: "" },
  { name: "Học Viên 6", emotion: "" },
  { name: "Học Viên 7", emotion: "" },
  { name: "Học Viên 8", emotion: "" },
  { name: "Học Viên 9", emotion: "" },
  { name: "Học Viên 10", emotion: "" },
  { name: "Học Viên 11", emotion: "" },
  { name: "Học Viên 12", emotion: "" },
  { name: "Học Viên 13", emotion: "" },
  { name: "Học Viên 14", emotion: "" },
  { name: "Học Viên 15", emotion: "" },
  { name: "Học Viên 16", emotion: "" },
  { name: "Học Viên 17", emotion: "" },
  { name: "Học Viên 18", emotion: "" },
  { name: "Học Viên 19", emotion: "" },
  { name: "Học Viên 20", emotion: "" },
];

const emotionEmojis = ["😊", "😐", "😞", "😃", "😢", "😲", "😠", "😴"];

const videoGrid = document.getElementById("videoGrid");
const participantsCount = document.getElementById("participantsCount");
const btnEmotion = document.getElementById("btnEmotion");

function updateParticipantsCount() {
  participantsCount.textContent = `${participants.length} người`;
}

function renderParticipants() {
  videoGrid.innerHTML = "";
  participants.forEach((p, index) => {
    const container = document.createElement("div");
    container.classList.add("video-container");

    container.innerHTML = `
        <div class="video-fake"></div>
        <div class="user-info">
          <div class="user-name">${p.name}</div>
          <div class="user-emotion" id="emotion-${index}">${p.emotion}</div>
        </div>
      `;
    videoGrid.appendChild(container);
  });
}

function detectEmotion() {
  participants.forEach((p, index) => {
    const randomEmoji =
      emotionEmojis[Math.floor(Math.random() * emotionEmojis.length)];
    p.emotion = randomEmoji;
  });
  renderParticipants();
}

btnEmotion.addEventListener("click", detectEmotion);

updateParticipantsCount();
renderParticipants();

function updateTime() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, "0");
  const minutes = now.getMinutes().toString().padStart(2, "0");
  document.getElementById("currentTime").textContent = `${hours}:${minutes}`;
}
setInterval(updateTime, 1000);
updateTime();

document.getElementById("btnEndCall").addEventListener("click", () => {
  alert("Bạn đã kết thúc cuộc họp!");
});
