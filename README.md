# 🎧 AI Companion - Hỗ trợ người khiếm thính

Hệ thống AI hỗ trợ người khiếm thính với các tính năng:

## ✨ Tính năng chính

- 🎤 **Chuyển đổi Lời nói**: Google Cloud Speech-to-Text với độ chính xác 99%
- 🔊 **Phân loại Âm thanh**: YAMNet với 521 loại âm thanh, độ chính xác 85%
- 🚨 **Cảnh báo Âm thanh**: Phát hiện báo cháy, chuông cửa, tiếng khóc trẻ em
- 💬 **Transcription Realtime**: Chuyển đổi cuộc hội thoại thành văn bản trực tiếp

## 🏗️ Kiến trúc

```
ai-companion/
├── backend/          # FastAPI + Python
├── frontend/         # React.js + Shadcn/ui
├── models/          # AI models storage
└── config/          # Configuration files
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python 3.9+)
- Google Cloud Speech-to-Text API
- TensorFlow (YAMNet)
- WebSocket for real-time communication

**Frontend:**
- React.js 18 + TypeScript
- Shadcn/ui + Tailwind CSS
- Socket.io-client
- Web Audio API

## 🚀 Cài đặt

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📝 Ghi chú

- Ngôn ngữ chính: Tiếng Việt
- Target: Người dùng cá nhân
- Offline mode: Đã thiết kế kiến trúc (chưa triển khai)

## 📄 License

MIT License 