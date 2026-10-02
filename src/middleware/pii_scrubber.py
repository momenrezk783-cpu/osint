import re
from typing import Tuple, List, Dict
from dataclasses import dataclass

@dataclass
class ScrubResult:
    clean_text: str
    redacted_entities: list[dict]
    original_hash: str  # للتتبع فقط بدون محتوى

class PIIScrubber:
    """
    يعمل محلياً على خادم Edge داخل الإمارات.
    لا يرسل أي بيانات حساسة للسحابة.
    """

    PATTERNS = {
        "emirates_id": r"\b(?:784-?\d{4}-?\d{7}-?\d{1})\b",
        "phone": r"(?<!\w)(?:\+971|0)?(?:50|52|54|55|56|58)\d{7}\b",
        "passport": r"\b[A-Z]{1,2}\d{6,9}\b",
        "iban": r"\bAE\d{2}\d{3}\d{16}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    }

    def __init__(self):
        self.compiled_patterns = {
            entity_type: re.compile(pattern, re.IGNORECASE)
            for entity_type, pattern in self.PATTERNS.items()
        }

    def scrub(self, text: str) -> ScrubResult:
        redacted = []
        clean = text

        for entity_type, compiled_pattern in self.compiled_patterns.items():
            def repl(match):
                original = match.group()
                redacted.append({
                    "type": entity_type,
                    "start": match.start(),
                    "end": match.end(),
                    "hash": hash(original)
                })
                return f"[{entity_type.upper()}_REDACTED]"

            clean = compiled_pattern.sub(repl, clean)

        return ScrubResult(
            clean_text=clean,
            redacted_entities=redacted,
            original_hash=str(hash(text))
        )
