import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.core.config import settings

class AlertService:
    def __init__(self):
        self.alert_settings = {}
        self.alert_history = []
        self._load_default_settings()
    
    def _load_default_settings(self):
        """Tải cài đặt mặc định cho các loại cảnh báo"""
        self.alert_settings = {
            "fire_alarm": {
                "enabled": True,
                "sensitivity": 0.8,
                "notification_method": ["visual", "vibration"],
                "priority": "critical"
            },
            "doorbell": {
                "enabled": True,
                "sensitivity": 0.7,
                "notification_method": ["visual"],
                "priority": "medium"
            },
            "baby_cry": {
                "enabled": True,
                "sensitivity": 0.8,
                "notification_method": ["visual", "vibration"],
                "priority": "high"
            },
            "phone_ring": {
                "enabled": True,
                "sensitivity": 0.6,
                "notification_method": ["visual"],
                "priority": "medium"
            }
        }
    
    async def configure_alerts(self, settings: List[Dict]) -> Dict[str, Any]:
        """
        Cấu hình cài đặt cảnh báo
        """
        try:
            for setting in settings:
                sound_type = setting.get("sound_type")
                if sound_type in self.alert_settings:
                    self.alert_settings[sound_type].update({
                        "enabled": setting.get("enabled", True),
                        "sensitivity": setting.get("sensitivity", 0.7),
                        "notification_method": setting.get("notification_method", ["visual"])
                    })
            
            return {"success": True, "updated_settings": len(settings)}
            
        except Exception as e:
            raise Exception(f"Lỗi cấu hình cảnh báo: {str(e)}")
    
    async def get_current_settings(self) -> Dict[str, Any]:
        """
        Lấy cài đặt cảnh báo hiện tại
        """
        return self.alert_settings
    
    async def trigger_alert(self, sound_type: str, confidence: float, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Kích hoạt cảnh báo cho âm thanh được phát hiện
        """
        try:
            if sound_type not in self.alert_settings:
                return {"triggered": False, "reason": "Unknown sound type"}
            
            setting = self.alert_settings[sound_type]
            
            if not setting["enabled"]:
                return {"triggered": False, "reason": "Alert disabled"}
            
            if confidence < setting["sensitivity"]:
                return {"triggered": False, "reason": "Below sensitivity threshold"}
            
            # Tạo alert record
            alert_record = {
                "id": f"alert_{len(self.alert_history) + 1}",
                "sound_type": sound_type,
                "confidence": confidence,
                "timestamp": datetime.now(),
                "location": location,
                "priority": setting["priority"],
                "notification_method": setting["notification_method"]
            }
            
            # Lưu vào lịch sử
            self.alert_history.append(alert_record)
            
            return {
                "triggered": True,
                "alert_id": alert_record["id"],
                "priority": setting["priority"],
                "notification_method": setting["notification_method"]
            }
            
        except Exception as e:
            raise Exception(f"Lỗi kích hoạt cảnh báo: {str(e)}")
    
    async def get_alert_history(self, limit: int = 50, sound_type: Optional[str] = None) -> List[Dict]:
        """
        Lấy lịch sử cảnh báo
        """
        try:
            history = self.alert_history.copy()
            
            # Filter by sound type if specified
            if sound_type:
                history = [alert for alert in history if alert["sound_type"] == sound_type]
            
            # Sort by timestamp (newest first)
            history.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Convert datetime to string for JSON serialization
            for alert in history[:limit]:
                alert["timestamp"] = alert["timestamp"].isoformat()
            
            return history[:limit]
            
        except Exception as e:
            raise Exception(f"Lỗi lấy lịch sử cảnh báo: {str(e)}")
    
    async def delete_alert(self, alert_id: str) -> bool:
        """
        Xóa một cảnh báo khỏi lịch sử
        """
        try:
            for i, alert in enumerate(self.alert_history):
                if alert["id"] == alert_id:
                    del self.alert_history[i]
                    return True
            return False
            
        except Exception as e:
            raise Exception(f"Lỗi xóa cảnh báo: {str(e)}")
    
    async def test_alert_system(self) -> Dict[str, Any]:
        """
        Test hệ thống cảnh báo
        """
        try:
            tested_components = []
            
            # Test each alert type
            for sound_type in self.alert_settings.keys():
                test_result = await self.trigger_alert(sound_type, 0.9, "Test Location")
                tested_components.append({
                    "component": sound_type,
                    "status": "success" if test_result["triggered"] else "failed",
                    "details": test_result
                })
            
            return {
                "components": tested_components,
                "overall_status": "success",
                "test_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Lỗi test hệ thống: {str(e)}")
    
    async def get_alert_statistics(self) -> Dict[str, Any]:
        """
        Thống kê cảnh báo theo thời gian
        """
        try:
            now = datetime.now()
            
            # Daily stats (last 7 days)
            daily_stats = {}
            for i in range(7):
                date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
                daily_stats[date] = len([
                    alert for alert in self.alert_history
                    if alert["timestamp"].strftime("%Y-%m-%d") == date
                ])
            
            # Weekly stats (last 4 weeks)
            weekly_stats = {}
            for i in range(4):
                week_start = now - timedelta(weeks=i)
                week_key = f"Week {i+1}"
                weekly_stats[week_key] = len([
                    alert for alert in self.alert_history
                    if alert["timestamp"] >= week_start - timedelta(days=7) and
                       alert["timestamp"] < week_start
                ])
            
            # Monthly stats (last 6 months)
            monthly_stats = {}
            for i in range(6):
                month = (now - timedelta(days=30*i)).strftime("%Y-%m")
                monthly_stats[month] = len([
                    alert for alert in self.alert_history
                    if alert["timestamp"].strftime("%Y-%m") == month
                ])
            
            # Most common alert types
            sound_counts = {}
            for alert in self.alert_history:
                sound_type = alert["sound_type"]
                sound_counts[sound_type] = sound_counts.get(sound_type, 0) + 1
            
            common_types = sorted(sound_counts.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "daily": daily_stats,
                "weekly": weekly_stats,
                "monthly": monthly_stats,
                "common_types": common_types[:5]  # Top 5
            }
            
        except Exception as e:
            raise Exception(f"Lỗi lấy thống kê: {str(e)}") 