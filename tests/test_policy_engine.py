import unittest
from src.core.policy_engine import OutputGateway, PolicyViolation

class TestPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.kb = {
            "rental_dispute": ["دائرة الأراضي والأملاك", "مركز فض المنازعات الإيجارية"]
        }
        self.gateway = OutputGateway(knowledge_base=self.kb)

    def test_legal_advice_violation(self):
        context = {"official_data": {}}
        allowed, msg, violation = self.gateway.validate(
            "حسب القانون يجب عليك إخلاء العقار فوراً.",
            "rental_dispute",
            context
        )
        self.assertFalse(allowed)
        self.assertEqual(violation, PolicyViolation.LEGAL_ADVICE)

    def test_promise_violation(self):
        context = {"official_data": {}}
        allowed, msg, violation = self.gateway.validate(
            "أكيد سيتم قبول طلبكم وإعادة التأمين.",
            "rental_dispute",
            context
        )
        self.assertFalse(allowed)
        self.assertEqual(violation, PolicyViolation.PROMISE)

    def test_unverified_number(self):
        context = {"official_data": {"reference": "1234"}}
        allowed, msg, violation = self.gateway.validate(
            "رقم المعاملة هو 99999.",
            "rental_dispute",
            context
        )
        self.assertFalse(allowed)
        self.assertEqual(violation, PolicyViolation.NUMBER_HALLUCINATION)

    def test_valid_response(self):
        context = {"official_data": {"fee": "5000"}}
        allowed, msg, violation = self.gateway.validate(
            "رسوم تقديم الطلب لدى مركز فض المنازعات الإيجارية هي 5000 درهم.",
            "rental_dispute",
            context
        )
        self.assertTrue(allowed)
        self.assertIsNone(violation)

if __name__ == '__main__':
    unittest.main()
