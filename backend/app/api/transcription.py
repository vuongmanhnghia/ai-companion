from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.services.transcription_service import TranscriptionService

router = APIRouter()
transcription_service = TranscriptionService()

class TranscriptionSession(BaseModel):
    session_id: str
    language: str = "vi-VN"
    participants: List[str] = []
    start_time: datetime
    end_time: Optional[datetime] = None

class TranscriptionSegment(BaseModel):
    speaker: Optional[str]
    text: str
    confidence: float
    timestamp: datetime
    duration: float

@router.websocket("/live")
async def websocket_transcription(websocket: WebSocket):
    """
    WebSocket endpoint cho real-time transcription
    """
    await websocket.accept()
    session_id = None
    
    try:
        # Nhận cấu hình từ client
        config = await websocket.receive_json()
        language = config.get("language", "vi-VN")
        
        # Bắt đầu session transcription
        session_id = await transcription_service.start_session(language)
        
        await websocket.send_json({
            "type": "session_started",
            "session_id": session_id,
            "language": language,
            "message": "Phiên transcription đã bắt đầu"
        })
        
        while True:
            # Nhận audio data từ client
            data = await websocket.receive_bytes()
            
            # Xử lý audio và trả về transcription
            result = await transcription_service.process_audio_chunk(
                session_id, data
            )
            
            if result and result["text"]:
                await websocket.send_json({
                    "type": "transcription",
                    "text": result["text"],
                    "confidence": result["confidence"],
                    "is_final": result["is_final"],
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Lỗi transcription: {str(e)}"
        })
    finally:
        if session_id:
            await transcription_service.end_session(session_id)

@router.post("/session/start")
async def start_transcription_session(
    language: str = "vi-VN",
    participants: List[str] = []
):
    """
    Bắt đầu phiên transcription mới
    """
    try:
        session_id = await transcription_service.start_session(language, participants)
        return {
            "success": True,
            "session_id": session_id,
            "language": language,
            "participants": participants,
            "start_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo session: {str(e)}")

@router.post("/session/{session_id}/end")
async def end_transcription_session(session_id: str):
    """
    Kết thúc phiên transcription
    """
    try:
        result = await transcription_service.end_session(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "end_time": datetime.now(),
            "total_segments": result["total_segments"],
            "duration": result["duration"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kết thúc session: {str(e)}")

@router.get("/session/{session_id}/transcript")
async def get_session_transcript(session_id: str):
    """
    Lấy bản transcript đầy đủ của phiên
    """
    try:
        transcript = await transcription_service.get_session_transcript(session_id)
        return {
            "session_id": session_id,
            "transcript": transcript["segments"],
            "summary": transcript["summary"],
            "participants": transcript["participants"],
            "duration": transcript["duration"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy transcript: {str(e)}")

@router.get("/sessions")
async def get_transcription_sessions(limit: int = 20):
    """
    Lấy danh sách các phiên transcription
    """
    try:
        sessions = await transcription_service.get_recent_sessions(limit)
        return {
            "total_sessions": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách session: {str(e)}")

@router.delete("/session/{session_id}")
async def delete_transcription_session(session_id: str):
    """
    Xóa phiên transcription
    """
    try:
        result = await transcription_service.delete_session(session_id)
        if result:
            return {"success": True, "message": "Đã xóa phiên transcription"}
        else:
            raise HTTPException(status_code=404, detail="Không tìm thấy session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xóa session: {str(e)}")

@router.post("/session/{session_id}/export")
async def export_transcript(session_id: str, format: str = "txt"):
    """
    Export transcript ra file (txt, docx, pdf)
    """
    try:
        if format not in ["txt", "docx", "pdf"]:
            raise HTTPException(status_code=400, detail="Format không hỗ trợ")
            
        file_path = await transcription_service.export_transcript(session_id, format)
        return {
            "success": True,
            "file_path": file_path,
            "format": format,
            "download_url": f"/api/transcription/download/{session_id}.{format}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi export: {str(e)}") 