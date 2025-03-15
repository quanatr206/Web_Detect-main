const express = require('express');
const app = express();
const port = 3000;

// Cấu hình để Express có thể phục vụ các file tĩnh từ thư mục "public"
app.use(express.static('public'));

// API đơn giản trả về thông tin máy người dùng
app.get('/api/userinfo', (req, res) => {
    res.json({
        userAgent: req.headers['user-agent'],
        platform: process.platform
    });
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
