import os
import asyncio
import httpx

class ElevenLabsStaticService:
    """
    خدمة التوليد الصوتي الثابت وحفظ الملفات للاسترجاع السريع دون تأخير (Zero Latency).
    """
    def __init__(self, api_key: str, voice_id: str, model_id: str = "eleven_multilingual_v2"):
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.base_url = "https://api.elevenlabs.io/v1"

    async def generate_audio(self, text: str, output_path: str) -> str:
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            def _save_file():
                dir_name = os.path.dirname(output_path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(response.content)
            await asyncio.to_thread(_save_file)
            return output_path
