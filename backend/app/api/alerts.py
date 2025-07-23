from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.services.alert_service import AlertService

router = APIRouter()
alert_service = AlertService()

class AlertSettings(BaseModel):
    sound_type: str
    enabled: bool
    sensitivity: float
    notification_method: List[str]  # ["visual", "vibration", "email"]

class AlertHistory(BaseModel):
    id: str
    sound_type: str
    confidence: float
    timestamp: datetime
    location: Optional[str] = None

@router.post("/configure")
async def configure_alerts(settings: List[AlertSettings]):
    """
    Cấu hình cài đặt cảnh báo cho các loại âm thanh
    """
    try:
        result = await alert_service.configure_alerts(settings)
        return JSONResponse({
            "success": True,
            "message": "Cấu hình cảnh báo thành công",
            "configured_alerts": len(settings)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi cấu hình: {str(e)}")

@router.get("/settings")
async def get_alert_settings():
    """
    Lấy cài đặt cảnh báo hiện tại
    """
    try:
        settings = await alert_service.get_current_settings()
        return {
            "alert_settings": settings,
            "available_sounds": [
                {
                    "type": "fire_alarm",
                    "name": "Báo cháy",
                    "default_sensitivity": 0.8,
                    "priority": "critical"
                },
                {
                    "type": "doorbell", 
                    "name": "Chuông cửa",
                    "default_sensitivity": 0.7,
                    "priority": "medium"
                },
                {
                    "type": "baby_cry",
                    "name": "Tiếng khóc trẻ em", 
                    "default_sensitivity": 0.8,
                    "priority": "high"
                },
                {
                    "type": "phone_ring",
                    "name": "Chuông điện thoại",
                    "default_sensitivity": 0.6,
                    "priority": "medium"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy cài đặt: {str(e)}")

@router.get("/history")
async def get_alert_history(
    limit: int = 50,
    sound_type: Optional[str] = None
):
    """
    Lấy lịch sử cảnh báo
    """
    try:
        history = await alert_service.get_alert_history(limit, sound_type)
        return {
            "total_alerts": len(history),
            "alerts": history,
            "filter": sound_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy lịch sử: {str(e)}")

@router.post("/test")
async def test_alert_system():
    """
    Test hệ thống cảnh báo
    """
    try:
        result = await alert_service.test_alert_system()
        return {
            "test_result": "success",
            "message": "Hệ thống cảnh báo hoạt động bình thường",
            "tested_components": result["components"],
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi test hệ thống: {str(e)}")

@router.delete("/history/{alert_id}")
async def delete_alert(alert_id: str):
    """
    Xóa một cảnh báo khỏi lịch sử
    """
    try:
        result = await alert_service.delete_alert(alert_id)
        if result:
            return {"success": True, "message": "Đã xóa cảnh báo"}
        else:
            raise HTTPException(status_code=404, detail="Không tìm thấy cảnh báo")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xóa cảnh báo: {str(e)}")

@router.get("/statistics")
async def get_alert_statistics():
    """
    Thống kê cảnh báo theo ngày/tuần/tháng
    """
    try:
        stats = await alert_service.get_alert_statistics()
        return {
            "daily_stats": stats["daily"],
            "weekly_stats": stats["weekly"], 
            "monthly_stats": stats["monthly"],
            "most_common_alerts": stats["common_types"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy thống kê: {str(e)}") 