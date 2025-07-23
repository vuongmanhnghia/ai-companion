import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.core.config import settings

class TranscriptionService:
    def __init__(self):
        self.active_sessions = {}
        self.session_history = []
    
    async def start_session(self, language: str = "vi-VN", participants: List[str] = []) -> str:
        """
        Bắt đầu phiên transcription mới
        """
        try:
            session_id = str(uuid.uuid4())
            
            session = {
                "session_id": session_id,
                "language": language,
                "participants": participants,
                "start_time": datetime.now(),
                "end_time": None,
                "segments": [],
                "status": "active"
            }
            
            self.active_sessions[session_id] = session
            
            return session_id
            
        except Exception as e:
            raise Exception(f"Lỗi tạo session: {str(e)}")
    
    async def process_audio_chunk(self, session_id: str, audio_data: bytes) -> Dict[str, Any]:
        """
        Xử lý chunk âm thanh và trả về transcription
        """
        try:
            if session_id not in self.active_sessions:
                raise Exception("Session không tồn tại")
            
            session = self.active_sessions[session_id]
            
            # Mock transcription processing
            # Trong thực tế, đây sẽ gọi Google Cloud Speech API
            mock_texts = [
                "Xin chào, tôi đang nói tiếng Việt",
                "Hôm nay thời tiết rất đẹp",
                "Bạn có nghe thấy tôi không?",
                "Đây là bản demo transcription",
                "Hệ thống đang hoạt động tốt"
            ]
            
            import random
            text = random.choice(mock_texts)
            confidence = round(random.uniform(0.8, 0.95), 2)
            is_final = random.choice([True, False])
            
            # Tạo segment mới
            segment = {
                "text": text,
                "confidence": confidence,
                "is_final": is_final,
                "timestamp": datetime.now(),
                "speaker": None
            }
            
            # Lưu segment nếu final
            if is_final:
                session["segments"].append(segment)
            
            return {
                "text": text,
                "confidence": confidence,
                "is_final": is_final,
                "session_id": session_id
            }
            
        except Exception as e:
            raise Exception(f"Lỗi xử lý audio chunk: {str(e)}")
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        Kết thúc phiên transcription
        """
        try:
            if session_id not in self.active_sessions:
                raise Exception("Session không tồn tại")
            
            session = self.active_sessions[session_id]
            session["end_time"] = datetime.now()
            session["status"] = "completed"
            
            # Tính duration
            duration = (session["end_time"] - session["start_time"]).total_seconds()
            session["duration"] = duration
            
            # Chuyển session sang history
            self.session_history.append(session)
            del self.active_sessions[session_id]
            
            return {
                "total_segments": len(session["segments"]),
                "duration": duration
            }
            
        except Exception as e:
            raise Exception(f"Lỗi kết thúc session: {str(e)}")
    
    async def get_session_transcript(self, session_id: str) -> Dict[str, Any]:
        """
        Lấy bản transcript đầy đủ của phiên
        """
        try:
            # Tìm session trong active hoặc history
            session = None
            
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
            else:
                for hist_session in self.session_history:
                    if hist_session["session_id"] == session_id:
                        session = hist_session
                        break
            
            if not session:
                raise Exception("Session không tồn tại")
            
            # Convert datetime objects to strings for JSON serialization
            segments = []
            for segment in session["segments"]:
                seg_copy = segment.copy()
                seg_copy["timestamp"] = segment["timestamp"].isoformat()
                segments.append(seg_copy)
            
            # Tạo summary từ các segments
            all_text = " ".join([seg["text"] for seg in session["segments"]])
            summary = all_text[:200] + "..." if len(all_text) > 200 else all_text
            
            return {
                "segments": segments,
                "summary": summary,
                "participants": session["participants"],
                "duration": session.get("duration", 0),
                "language": session["language"]
            }
            
        except Exception as e:
            raise Exception(f"Lỗi lấy transcript: {str(e)}")
    
    async def get_recent_sessions(self, limit: int = 20) -> List[Dict]:
        """
        Lấy danh sách các phiên transcription gần đây
        """
        try:
            # Combine active and history sessions
            all_sessions = list(self.active_sessions.values()) + self.session_history
            
            # Sort by start time (newest first)
            all_sessions.sort(key=lambda x: x["start_time"], reverse=True)
            
            # Convert datetime to string and prepare response
            sessions = []
            for session in all_sessions[:limit]:
                session_copy = {
                    "session_id": session["session_id"],
                    "language": session["language"],
                    "participants": session["participants"],
                    "start_time": session["start_time"].isoformat(),
                    "end_time": session["end_time"].isoformat() if session["end_time"] else None,
                    "status": session["status"],
                    "segment_count": len(session["segments"]),
                    "duration": session.get("duration", 0)
                }
                sessions.append(session_copy)
            
            return sessions
            
        except Exception as e:
            raise Exception(f"Lỗi lấy danh sách session: {str(e)}")
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Xóa phiên transcription
        """
        try:
            # Xóa từ active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                return True
            
            # Xóa từ history
            for i, session in enumerate(self.session_history):
                if session["session_id"] == session_id:
                    del self.session_history[i]
                    return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Lỗi xóa session: {str(e)}")
    
    async def export_transcript(self, session_id: str, format: str = "txt") -> str:
        """
        Export transcript ra file
        """
        try:
            transcript = await self.get_session_transcript(session_id)
            
            # Tạo nội dung file
            content = f"Transcript Session: {session_id}\n"
            content += f"Language: {transcript['language']}\n"
            content += f"Duration: {transcript['duration']} seconds\n"
            content += f"Participants: {', '.join(transcript['participants'])}\n"
            content += "=" * 50 + "\n\n"
            
            for segment in transcript["segments"]:
                content += f"[{segment['timestamp']}] "
                if segment.get('speaker'):
                    content += f"{segment['speaker']}: "
                content += f"{segment['text']} (Confidence: {segment['confidence']})\n"
            
            # Mock file path - trong thực tế sẽ lưu file thật
            file_path = f"/tmp/transcript_{session_id}.{format}"
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Lỗi export transcript: {str(e)}") 