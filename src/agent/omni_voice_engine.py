import asyncio
import json
import re
from typing import Any, AsyncGenerator, Dict, Optional, Union


class ConfigurationAgnosticCore:
    """
    نواة إعدادات لا أدرية (Omni-Adaptable).
    تسمح بتغيير شخصية وأدوات الوكيل الصوتي عبر ملف JSON خارجي،
    لتطبيق بروتوكولات حماية NeMo Guardrails وتخصيص وكيل لقطاعات مختلفة في وقت التشغيل.
    """
    def __init__(self, config_source: Union[str, Dict[str, Any]]):
        if isinstance(config_source, str):
            with open(config_source, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        elif isinstance(config_source, dict):
            self.config = config_source
        else:
            self.config = {}

        self.system_prompt = self.config.get("system_prompt", "أنت مساعد ذكي.")
        self.tools_config = self.config.get("tools", [])
        self.domain = self.config.get("domain", "general")


class OmniVoiceEngine:
    """
    النواة التشغيلية الفائقة للوكيل الصوتي.
    تُدمج التوازي التكهني، الاسترجاع اللحظي، وإدارة المقاطعة اللحظية المعقدة.
    """
    def __init__(self, config_core: ConfigurationAgnosticCore):
        self.config = config_core
        self.audio_playback_queue: asyncio.Queue = asyncio.Queue()
        self.interrupt_event = asyncio.Event()

        # مهام التوليد المفتوحة للسماح بإلغائها فوراً (Cancellation Tokens)
        self.current_llm_task: Optional[asyncio.Task] = None
        self.current_tts_task: Optional[asyncio.Task] = None

        self.conversation_history = [{"role": "system", "content": self.config.system_prompt}]
        self.sentence_boundary = re.compile(r'(?<=[.!?،؛])\s+')

        # الذاكرة المخبئية للتكهن الصوتي (Speculative Cache)
        self.speculative_cache: Dict[str, Any] = {}
        # مؤشر الاحتفاظ الدلالي
        self.acknowledged_transcript = ""

    async def handle_barge_in(self):
        """
        بروتوكول المقاطعة اللحظية (Absolute Barge-in Protocol):
        يُستدعى فور رصد VAD لخطاب بشري صالح يمتد لأكثر من 300 ملي ثانية لتجاوز الضجيج.
        """
        print("[المقاطعة] رصد مقاطعة من المستخدم. بدء بروتوكول التنظيف الفوري.")
        self.interrupt_event.set()

        # 1. الإفراغ اللحظي لحزم WebRTC لمنع الاستمرار الروبوتي
        while not self.audio_playback_queue.empty():
            try:
                self.audio_playback_queue.get_nowait()
                self.audio_playback_queue.task_done()
            except asyncio.QueueEmpty:
                break

        # 2. إطلاق رموز الإلغاء لمهام التوليد النشطة
        if self.current_llm_task and not self.current_llm_task.done():
            self.current_llm_task.cancel()
        if self.current_tts_task and not self.current_tts_task.done():
            self.current_tts_task.cancel()

        # تحديث الذاكرة بما نُطق فعلياً لحفظ انسجام الحوار
        if self.acknowledged_transcript:
            self.conversation_history.append({"role": "assistant", "content": self.acknowledged_transcript + " [تمت المقاطعة]"})
            self.acknowledged_transcript = ""

    async def _stream_rag_hook(self, partial_transcript: str) -> Optional[str]:
        """
        الاسترجاع الموازي (StreamRAG):
        يُقيّم الاكتمال الدلالي بشكل متكرر؛ إذا تحقق، يطلق بحثاً متوازياً في قواعد البيانات.
        """
        word_count = len(partial_transcript.split())
        # شرط مبسط لتمثيل حاجز الاكتمال الدلالي
        if word_count > 4 and self.config.domain != "general":
            print(f"[StreamRAG] تم تجاوز عتبة الإدراك. بدء استرجاع متزامن لـ: {partial_transcript}...")
            # إخفاء زمن RAG خلف حديث المستخدم
            await asyncio.sleep(0.01)
            return f"<RAG_CONTEXT> بيانات مسترجعة من المستودع المتجهي لـ {partial_transcript} </RAG_CONTEXT>"
        return None

    async def _endpoint_anticipation_executor(self, partial_transcript: str):
        """
        التوليد التكهني (Speculative Execution):
        بناءً على احتمال نهاية الجملة p(h)_t، يُحضر الاستجابة قبل توقف المستخدم عن الكلام.
        """
        print(f"[التكهن-EPA] تم توقع نهاية دور المستخدم. بدء بناء مخبأ استجابة تكهني...")

        # استدعاء وهمي للـ LLM للحصول على بادئة الاستجابة
        speculative_response_text = "حسناً، بناءً على هذه البيانات، "
        # محاكاة تحويل النص إلى صوت تكهني يُحفظ بالذاكرة
        self.speculative_cache['anticipated_audio'] = b'SPECULATIVE_AUDIO_PAYLOAD'
        self.speculative_cache['anticipated_text'] = speculative_response_text

    async def process_user_stream(self, rtc_stt_stream: AsyncGenerator[Dict[str, Any], None]):
        """
        المحرك الموازي لمعالجة التدفقات. يتلقى الأحداث من طبقة النقل ويوزعها بشكل لامركزي.
        """
        current_transcript = ""
        rag_context = ""

        async for event in rtc_stt_stream:
            # معالجة فورية لأحداث المقاطعة
            if event.get("is_speech_start"):
                self.interrupt_event.clear()
                await self.handle_barge_in()
                continue

            partial_transcript = event.get("transcript", "")
            if partial_transcript:
                current_transcript = partial_transcript

                # إطلاق الاسترجاع الديناميكي متزامناً مع تدفق الكلام
                if not rag_context:
                    rag_result = await self._stream_rag_hook(current_transcript)
                    if rag_result:
                        rag_context = rag_result

                # مراقبة توقع نقطة النهاية (Endpoint Anticipation)
                if event.get("anticipate_endpoint_probability", 0.0) > 0.85 and not self.speculative_cache:
                    await self._endpoint_anticipation_executor(current_transcript)

            # تأكيد النهاية الفعلية للمتحدث من الـ VAD
            if event.get("is_final"):
                print(f"[VAD] نهاية مؤكدة للحديث: {current_transcript}")

                # تطبيق المخبأ التكهني فوراً لخفض الكمون إلى 0 ملي ثانية
                if 'anticipated_audio' in self.speculative_cache:
                    print("[الكمون-الصفري] تحرير المخبأ التكهني. زمن الاستجابة الفعلي: 0ms.")
                    await self.audio_playback_queue.put(self.speculative_cache['anticipated_audio'])

                    # تعديل سياق الحوار ليعكس النص الذي أُطلق
                    anticipated_text = self.speculative_cache['anticipated_text']
                    self.acknowledged_transcript = anticipated_text

                    full_prompt = f"{rag_context}\n[استجابة تكهنية مدفوعة مسبقاً: {anticipated_text}]\nالمستخدم: {current_transcript}"
                    self.speculative_cache.clear()
                else:
                    full_prompt = f"{rag_context}\nالمستخدم: {current_transcript}"

                self.conversation_history.append({"role": "user", "content": full_prompt})

                # تفعيل سلسلة التوليد اللاحقة اللامتزامنة
                self.current_llm_task = asyncio.create_task(
                    self.generate_and_stream_tts()
                )

                current_transcript = ""
                rag_context = ""

    async def generate_and_stream_tts(self):
        """
        التوليد النصي وتقطيع الجمل الديناميكي للإرسال الموازي نحو محرك الـ TTS.
        """
        buffer = ""
        try:
            # محاكاة لتيار LLM الوارد
            async for chunk in self._mock_llm_stream():
                if self.interrupt_event.is_set():
                    break

                buffer += chunk
                parts = self.sentence_boundary.split(buffer)

                # متى ما تشكلت جملة مفهومة، تُدفع للـ TTS بينما يستمر توليد الـ LLM في الخلفية
                if len(parts) > 1:
                    sentence_to_synth = parts[0]
                    buffer = " ".join(parts[1:])
                    self.acknowledged_transcript += sentence_to_synth + " "

                    self.current_tts_task = asyncio.create_task(
                        self.synthesize_and_queue(sentence_to_synth)
                    )

            # تفريغ الفضلات المتبقية في المخزن
            if buffer.strip() and not self.interrupt_event.is_set():
                 self.acknowledged_transcript += buffer
                 self.current_tts_task = asyncio.create_task(
                        self.synthesize_and_queue(buffer)
                 )

        except asyncio.CancelledError:
            print("[نواة الذكاء الاصطناعي] تم إجهاض المهمة استجابة لرمز الإلغاء (Barge-in).")

    async def synthesize_and_queue(self, text: str):
        """إرسال المقاطع إلى الـ TTS وإدراج الصوت الناتج في طابور النقل."""
        if self.interrupt_event.is_set():
            return

        print(f"[TTS] ترجمة النص إلى تدفق صوتي: {text}")
        await asyncio.sleep(0.01) # زمن افتراضي لمحرك TTS سريع

        if not self.interrupt_event.is_set():
            # إدراج حزمة البيانات الخام
            await self.audio_playback_queue.put(b"OPUS_ENCODED_AUDIO_CHUNK")

    async def _mock_llm_stream(self) -> AsyncGenerator[str, None]:
        """أداة محاكاة لتوليد تيار نصي بمعدلات متفاوتة."""
        words = ["النتائج ", "تشير ", "بوضوح ", "إلى ", "وجود ", "تطابق ", "مباشر."]
        for word in words:
            await asyncio.sleep(0.01)
            yield word
