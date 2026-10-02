import os
from pydantic import BaseModel

class Settings(BaseModel):
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.85"))
    circuit_breaker_failure_threshold: int = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    circuit_breaker_recovery_timeout: int = int(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "30"))
    azure_speech_region: str = os.getenv("AZURE_SPEECH_REGION", "uaenorth")
    azure_speech_key: str = os.getenv("AZURE_SPEECH_KEY", "")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "")
    azure_storage_connection_string: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")

settings = Settings()
