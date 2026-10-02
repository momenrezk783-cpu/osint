from typing import Dict, Any
from src.agent.inbound_handler import InboundHandler
from src.agent.outbound_handler import OutboundHandler

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Any] = {}

    def create_session(self, call_type: str, caller_id: str):
        if call_type == "outbound":
            session = OutboundHandler(caller_id=caller_id)
        else:
            session = InboundHandler(caller_id=caller_id)
        self.sessions[caller_id] = session
        return session

    def get_session(self, caller_id: str):
        return self.sessions.get(caller_id)
