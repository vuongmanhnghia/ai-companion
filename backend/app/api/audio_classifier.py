from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from app.services.audio_classifier_service import AudioClassifierService

router = APIRouter()
audio_classifier = AudioClassifierService()

@router.post("/classify")
async def classify_audio(
    file: UploadFile = File(...),
    top_k: int = 5
):
    """
    Phân loại âm thanh sử dụng YAMNet
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
            # Phân loại âm thanh
            result = await audio_classifier.classify_audio_file(tmp_file_path, top_k)
            
            return JSONResponse({
                "success": True,
                "classifications": result["classifications"],
                "top_prediction": result["top_prediction"],
                "filename": file.filename,
                "model": "YAMNet"
            })
            
        finally:
            # Xóa file tạm thời
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi phân loại âm thanh: {str(e)}")

@router.get("/sound-classes")
async def get_sound_classes():
    """
    Lấy danh sách các loại âm thanh YAMNet có thể nhận diện
    """
    try:
        classes = await audio_classifier.get_available_classes()
        return {
            "total_classes": len(classes),
            "classes": classes[:50],  # Trả về 50 class đầu tiên
            "model": "YAMNet",
            "accuracy": "85%"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách: {str(e)}")

@router.get("/critical-sounds")
async def get_critical_sounds():
    """
    Lấy danh sách các âm thanh quan trọng cần cảnh báo
    """
    return {
        "critical_sounds": [
            {
                "id": "fire_alarm",
                "name": "Báo cháy",
                "description": "Tiếng báo cháy, khói",
                "priority": "high",
                "yamnet_classes": ["Smoke detector, smoke alarm", "Fire alarm"]
            },
            {
                "id": "doorbell",
                "name": "Chuông cửa",
                "description": "Tiếng chuông cửa, gõ cửa",
                "priority": "medium",
                "yamnet_classes": ["Doorbell", "Knock"]
            },
            {
                "id": "baby_cry",
                "name": "Tiếng khóc trẻ em",
                "description": "Tiếng khóc của trẻ em, trẻ sơ sinh",
                "priority": "high",
                "yamnet_classes": ["Baby cry, infant cry", "Child speech, kid speaking"]
            },
            {
                "id": "phone_ring",
                "name": "Chuông điện thoại",
                "description": "Tiếng chuông điện thoại",
                "priority": "medium",
                "yamnet_classes": ["Telephone bell ringing", "Ringtone"]
            }
        ]
    }

@router.get("/status")
async def get_classifier_status():
    """
    Kiểm tra trạng thái dịch vụ Audio Classification
    """
    try:
        status = await audio_classifier.check_model_status()
        return {
            "service": "YAMNet Audio Classifier",
            "status": "active" if status else "inactive",
            "model_loaded": status,
            "total_classes": 521,
            "accuracy": "85%"
        }
    except Exception as e:
        return {
            "service": "YAMNet Audio Classifier",
            "status": "error",
            "error": str(e)
        } 