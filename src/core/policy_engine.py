# policy_engine.py
from enum import Enum
from typing import Tuple, Optional
import re

class PolicyViolation(Enum):
    LEGAL_ADVICE = "legal_advice"
    PROMISE = "promise"
    NUMBER_HALLUCINATION = "number_hallucination"
    OUT_OF_SCOPE = "out_of_scope"
    UNAUTHORIZED_ACTION = "unauthorized_action"

class OutputGateway:
    """
    يعمل كـ Gatekeeper قبل أي TTS.
    يرفض أي نص يحتوي على استشارة قانونية أو وعود أو أرقام غير موجودة في Knowledge Base.
    """

    FORBIDDEN_PATTERNS = [
        (r"(يجب عليك|أنصحك|الأفضل أن|من حقك|قانوناً|حسب القانون)", PolicyViolation.LEGAL_ADVICE),
        (r"(سأوافق|سيتم الموافقة|مضمون|أكيد سيتم|وعد)", PolicyViolation.PROMISE),
        (r"(رقم المعاملة|المرجع|المبلغ|الغرامة).*?\d{4,}", PolicyViolation.NUMBER_HALLUCINATION),
    ]

    ALLOWED_SOURCES = {
        "rental_dispute": ["دائرة الأراضي والأملاك", "مركز فض المنازعات الإيجارية"],
        "birth_registration": ["هيئة الصحة بدبي", "دائرة الاقتصاد والسياحة"],
    }

    def __init__(self, knowledge_base: dict):
        self.kb = knowledge_base  # مصادر رسمية فقط (RAG documents)
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), violation)
            for pattern, violation in self.FORBIDDEN_PATTERNS
        ]
        self.number_pattern = re.compile(r"\d{4,}")

    def validate(self, response_text: str, intent: str, context: dict) -> Tuple[bool, Optional[str], Optional[PolicyViolation]]:
        # 1. فحص الأنماط المحظورة
        for compiled_pattern, violation in self.compiled_patterns:
            if compiled_pattern.search(response_text):
                return False, "عذراً، لا أستطيع تقديم هذا النوع من المعلومات. يرجى التواصل مع الموظف المختص.", violation

        # 2. التأكد أن أي رقم مذكور موجود في السياق الرسمي فقط
        numbers = self.number_pattern.findall(response_text)
        if numbers:
            official_data_str = str(context.get("official_data", {}))
            for num in numbers:
                if num not in official_data_str:
                    return False, "لا يمكنني تأكيد هذا الرقم. سأحولك إلى موظف.", PolicyViolation.NUMBER_HALLUCINATION

        # 3. التأكد من أن المحتوى مستمد من RAG فقط
        if intent not in self.ALLOWED_SOURCES:
            return False, "هذا الاستفسار خارج نطاق خدمتي. سأحولك الآن.", PolicyViolation.OUT_OF_SCOPE

        return True, response_text, None
