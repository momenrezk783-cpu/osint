from enum import Enum
from typing import Optional

class CallState(Enum):
    INIT = "init"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    FAILED_OVER = "failed_over"
    TERMINATED = "terminated"

class VoiceStateMachine:
    def __init__(self):
        self.state = CallState.INIT

    def transition(self, new_state: CallState):
        self.state = new_state
