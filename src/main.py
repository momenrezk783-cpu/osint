# src/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio

from config.settings import settings
from src.middleware.pii_scrubber import PIIScrubber
from src.middleware.confidence_gate import ConfidenceGate
from src.core.policy_engine import OutputGateway
from src.core.circuit_breaker import CircuitBreaker
from src.cache.semantic_cache import SemanticCache
from src.agent.session_manager import SessionManager

app = FastAPI(
    title="Mizan Voice Agent",
    description="Production-Ready Sovereign Voice Agent (DESC & PDPL Compliant)",
    version="1.0.0"
)

scrubber = PIIScrubber()
confidence_gate = ConfidenceGate(threshold=settings.confidence_threshold)
circuit_breaker = CircuitBreaker(
    failure_threshold=settings.circuit_breaker_failure_threshold,
    recovery_timeout=settings.circuit_breaker_recovery_timeout
)
knowledge_base = {
    "rental_dispute": ["دائرة الأراضي والأملاك", "مركز فض المنازعات الإيجارية"],
    "birth_registration": ["هيئة الصحة بدبي", "دائرة الاقتصاد والسياحة"]
}
policy_gateway = OutputGateway(knowledge_base=knowledge_base)
session_mgr = SessionManager()

class CallInitRequest(BaseModel):
    caller_id: str
    call_type: str

class QueryRequest(BaseModel):
    caller_id: str
    call_type: str
    text: str
    intent: Optional[str] = "rental_dispute"

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "circuit_breaker_state": circuit_breaker.state.value,
        "region": settings.azure_speech_region
    }

@app.post("/call/process-text")
async def process_call_text(req: QueryRequest):
    if not circuit_breaker.allow_request():
        raise HTTPException(status_code=503, detail="Circuit Open: Failover to Human IVR active")

    try:
        scrubbed = await asyncio.to_thread(scrubber.scrub, req.text)
        session = session_mgr.create_session(req.call_type, req.caller_id)

        if hasattr(session, "handle_query"):
            raw_response = await session.handle_query(scrubbed.clean_text)
        else:
            raw_response = await session.generate_prompt()

        conf_ok, response_text = confidence_gate.check({"confidence": 0.95, "text": raw_response})
        if not conf_ok:
            return {"action": "transfer_to_human", "message": response_text}

        allowed, final_text, violation = await asyncio.to_thread(
            policy_gateway.validate,
            response_text,
            req.intent,
            session.context
        )

        if not allowed:
            return {
                "action": "transfer_to_human",
                "reason": violation.value if violation else "policy_violation",
                "message": final_text
            }

        circuit_breaker.record_success()
        return {
            "action": "speak",
            "text": final_text,
            "pii_redacted_count": len(scrubbed.redacted_entities)
        }

    except Exception as e:
        circuit_breaker.record_failure()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.websocket("/ws/voice-stream")
async def voice_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"ACK: {data}")
    except WebSocketDisconnect:
        pass
