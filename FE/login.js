document
  .getElementById("loginForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    // Lấy thông tin từ form
    const studentName = document.getElementById("studentName").value.trim();
    const classCode = document.getElementById("classCode").value.trim();

    // Kiểm tra dữ liệu hợp lệ
    if (studentName === "" || classCode === "") {
      alert("Vui lòng nhập đầy đủ thông tin!");
      return;
    }

    // Lưu thông tin vào localStorage (để chuyển sang trang học)
    localStorage.setItem("studentName", studentName);
    localStorage.setItem("classCode", classCode);

    // Chuyển sang giao diện lớp học
    window.location.href = "student.html";
  });
