from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from app.services.speech_service import SpeechService
from app.core.config import settings

router = APIRouter()
speech_service = SpeechService()

@router.post("/upload")
async def speech_to_text_upload(
    file: UploadFile = File(...),
    language: str = "vi-VN"
):
    """
    Upload file âm thanh và chuyển đổi thành văn bản
    """
    try:
        # Kiểm tra định dạng file
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File phải là định dạng âm thanh")
        
        # Lưu file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Chuyển đổi speech to text
            result = await speech_service.transcribe_audio_file(tmp_file_path, language)
            
            return JSONResponse({
                "success": True,
                "transcription": result["transcription"],
                "confidence": result["confidence"],
                "language": language,
                "filename": file.filename
            })
            
        finally:
            # Xóa file tạm thời
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """
    Lấy danh sách ngôn ngữ được hỗ trợ
    """
    return {
        "supported_languages": [
            {"code": "vi-VN", "name": "Tiếng Việt", "default": True},
            {"code": "en-US", "name": "English", "default": False}
        ]
    }

@router.get("/status")
async def get_speech_service_status():
    """
    Kiểm tra trạng thái dịch vụ Speech-to-Text
    """
    try:
        status = await speech_service.check_service_status()
        return {
            "service": "Google Cloud Speech-to-Text",
            "status": "active" if status else "inactive",
            "accuracy": "99%"
        }
    except Exception as e:
        return {
            "service": "Google Cloud Speech-to-Text", 
            "status": "error",
            "error": str(e)
        } 