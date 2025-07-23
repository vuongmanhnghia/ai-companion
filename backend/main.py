from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from app.api import speech, alerts, transcription  # audio_classifier tạm thời bỏ

# Create FastAPI app
app = FastAPI(
    title="AI Companion - Hỗ trợ người khiếm thính",
    description="Hệ thống AI hỗ trợ người khiếm thính với Speech-to-Text và Audio Classification",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"]
)

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Include API routes
app.include_router(speech.router, prefix="/api/speech", tags=["speech"])
# app.include_router(audio_classifier.router, prefix="/api/audio", tags=["audio"])  # Tạm thời comment
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(transcription.router, prefix="/api/transcription", tags=["transcription"])

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")
    await sio.emit('connected', {'message': 'Kết nối thành công!'}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

@sio.event
async def start_transcription(sid, data):
    """Bắt đầu phiên transcription real-time"""
    print(f"Starting transcription for client {sid}")
    # TODO: Implement real-time transcription logic
    await sio.emit('transcription_started', {'status': 'started'}, room=sid)

@sio.event
async def stop_transcription(sid, data):
    """Dừng phiên transcription"""
    print(f"Stopping transcription for client {sid}")
    await sio.emit('transcription_stopped', {'status': 'stopped'}, room=sid)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Companion API - Hỗ trợ người khiếm thính",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True) 