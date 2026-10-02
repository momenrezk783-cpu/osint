from typing import Tuple, Dict, Any

class ConfidenceGate:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def check(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        confidence = payload.get("confidence", 0.0)
        text = payload.get("text", "")
        if confidence < self.threshold:
            return False, "عذراً، لم أتمكن من فهم طلبك بدقة كافية. سأقوم بتحويلك لممثل خدمة العملاء."
        return True, text
