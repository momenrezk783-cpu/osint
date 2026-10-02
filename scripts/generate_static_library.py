import asyncio
import os
from config.settings import settings
from src.integrations.elevenlabs_static import ElevenLabsStaticService

STATIC_PHRASES = {
    "greeting.mp3": "مرحباً بكم في مركز الاتصال لحكومة دبي، كيف يمكنني مساعدتكم؟",
    "hold.mp3": "يرجى الانتظار لحظات ريثما نقوم بمراجعة البيانات.",
    "escalate.mp3": "سأقوم الآن بتحويل مكالمتكم إلى الموظف المختص لمزيد من الدعم."
}

async def main():
    service = ElevenLabsStaticService(
        api_key=settings.elevenlabs_api_key,
        voice_id=settings.elevenlabs_voice_id
    )
    for filename, phrase in STATIC_PHRASES.items():
        out_path = os.path.join("assets", filename)
        print(f"Generating static audio: {filename}...")
        await service.generate_audio(phrase, out_path)

if __name__ == "__main__":
    asyncio.run(main())
