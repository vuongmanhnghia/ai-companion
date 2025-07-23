import asyncio
import io
import os
from typing import Dict, Any, Optional
from google.cloud import speech
import librosa
import soundfile as sf
from app.core.config import settings

class SpeechService:
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Khởi tạo Google Cloud Speech client"""
        try:
            # Kiểm tra nếu có credentials
            if settings.google_credentials_path and os.path.exists(settings.google_credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.google_credentials_path
                self.client = speech.SpeechClient()
                print("✅ Google Cloud Speech client initialized successfully")
            else:
                print("⚠️ Google Cloud credentials not found - using mock mode")
                self.client = None
        except Exception as e:
            print(f"❌ Error initializing Speech client: {e}")
            self.client = None
    
    async def transcribe_audio_file(self, file_path: str, language: str = "vi-VN") -> Dict[str, Any]:
        """
        Chuyển đổi file âm thanh thành văn bản
        """
        try:
            # Đọc và xử lý file âm thanh
            audio_data, sample_rate = librosa.load(file_path, sr=16000)
            
            # Nếu có Google Cloud client, sử dụng API thật
            if self.client:
                # Convert audio to bytes
                audio_bytes = (audio_data * 32767).astype('int16').tobytes()
                
                # Configure recognition
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code=language,
                    enable_automatic_punctuation=True,
                    model='latest_long'
                )
                
                audio = speech.RecognitionAudio(content=audio_bytes)
                
                # Perform recognition
                response = self.client.recognize(config=config, audio=audio)
                
                if response.results:
                    # Get the first result
                    result = response.results[0]
                    transcript = result.alternatives[0].transcript
                    confidence = result.alternatives[0].confidence
                    
                    return {
                        "transcription": transcript,
                        "confidence": confidence,
                        "language": language,
                        "duration": len(audio_data) / sample_rate,
                        "source": "google_cloud"
                    }
                else:
                    return {
                        "transcription": "Không thể nhận diện được âm thanh",
                        "confidence": 0.0,
                        "language": language,
                        "duration": len(audio_data) / sample_rate,
                        "source": "google_cloud"
                    }
            
            # Fallback to mock response
            else:
                if language == "vi-VN":
                    mock_transcription = "⚠️ DEMO MODE: Xin chào, đây là bản demo chuyển đổi giọng nói tiếng Việt thành văn bản."
                else:
                    mock_transcription = "⚠️ DEMO MODE: Hello, this is a demo speech-to-text conversion."
                
                return {
                    "transcription": mock_transcription,
                    "confidence": 0.95,
                    "language": language,
                    "duration": len(audio_data) / sample_rate,
                    "source": "mock"
                }
            
        except Exception as e:
            raise Exception(f"Lỗi transcribe audio: {str(e)}")
    
    async def transcribe_audio_stream(self, audio_chunk: bytes, language: str = "vi-VN") -> Dict[str, Any]:
        """
        Chuyển đổi real-time audio stream thành văn bản
        """
        try:
            if self.client:
                # TODO: Implement streaming recognition
                # config = speech.RecognitionConfig(...)
                # streaming_config = speech.StreamingRecognitionConfig(...)
                # requests = [speech.StreamingRecognizeRequest(audio_content=audio_chunk)]
                # responses = self.client.streaming_recognize(streaming_config, requests)
                
                return {
                    "text": "🔄 Đang xử lý streaming...",
                    "confidence": 0.8,
                    "is_final": False,
                    "language": language,
                    "source": "google_cloud_streaming"
                }
            else:
                # Mock streaming transcription
                return {
                    "text": "⚠️ DEMO: Đang nghe...",
                    "confidence": 0.8,
                    "is_final": False,
                    "language": language,
                    "source": "mock"
                }
        except Exception as e:
            raise Exception(f"Lỗi stream transcription: {str(e)}")
    
    async def check_service_status(self) -> bool:
        """
        Kiểm tra trạng thái dịch vụ Google Cloud Speech
        """
        try:
            if self.client:
                # Test with a simple recognition request
                return True
            else:
                return False
        except Exception as e:
            print(f"Service check error: {e}")
            return False
    
    def get_supported_languages(self) -> list:
        """
        Lấy danh sách ngôn ngữ được hỗ trợ
        """
        return [
            {"code": "vi-VN", "name": "Tiếng Việt"},
            {"code": "en-US", "name": "English (US)"},
            {"code": "en-GB", "name": "English (UK)"},
            {"code": "ja-JP", "name": "Japanese"},
            {"code": "ko-KR", "name": "Korean"}
        ] 