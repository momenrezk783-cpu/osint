import asyncio
import pytest
from src.agent.omni_voice_engine import ConfigurationAgnosticCore, OmniVoiceEngine

@pytest.mark.anyio
async def test_configuration_agnostic_core():
    config_dict = {
        "system_prompt": "أنت مساعد طوارئ طبي",
        "domain": "medical",
        "tools": ["clinic_lookup"]
    }
    core = ConfigurationAgnosticCore(config_dict)
    assert core.system_prompt == "أنت مساعد طوارئ طبي"
    assert core.domain == "medical"
    assert core.tools_config == ["clinic_lookup"]

@pytest.mark.anyio
async def test_omni_voice_engine_barge_in():
    core = ConfigurationAgnosticCore({"domain": "medical"})
    engine = OmniVoiceEngine(core)

    # Put dummy audio item in queue
    await engine.audio_playback_queue.put(b"DUMMY_AUDIO")
    engine.acknowledged_transcript = "السلام عليكم"

    await engine.handle_barge_in()

    assert engine.audio_playback_queue.empty()
    assert engine.interrupt_event.is_set()
    assert len(engine.conversation_history) == 2
    assert "السلام عليكم [تمت المقاطعة]" in engine.conversation_history[-1]["content"]

@pytest.mark.anyio
async def test_omni_voice_engine_stream_process():
    core = ConfigurationAgnosticCore({"domain": "medical"})
    engine = OmniVoiceEngine(core)

    async def mock_stream():
        yield {"is_speech_start": True}
        yield {
            "transcript": "أريد حجز موعد في العيادة",
            "anticipate_endpoint_probability": 0.9,
            "is_final": True
        }

    await engine.process_user_stream(mock_stream())

    # Wait for LLM task completion
    if engine.current_llm_task:
        await engine.current_llm_task
    if engine.current_tts_task:
        await engine.current_tts_task

    assert not engine.audio_playback_queue.empty()
    item = await engine.audio_playback_queue.get()
    assert item == b'SPECULATIVE_AUDIO_PAYLOAD'
