import unittest
from src.middleware.pii_scrubber import PIIScrubber

class TestPIIScrubber(unittest.TestCase):
    def setUp(self):
        self.scrubber = PIIScrubber()

    def test_scrub_no_pii(self):
        text = "Hello world, this is a normal sentence."
        result = self.scrubber.scrub(text)
        self.assertEqual(result.clean_text, text)
        self.assertEqual(len(result.redacted_entities), 0)

    def test_scrub_emirates_id(self):
        text = "My Emirates ID is 784-1234-1234567-1."
        result = self.scrubber.scrub(text)
        self.assertEqual(result.clean_text, "My Emirates ID is [EMIRATES_ID_REDACTED].")
        self.assertEqual(len(result.redacted_entities), 1)
        self.assertEqual(result.redacted_entities[0]["type"], "emirates_id")

        text2 = "My Emirates ID is 784123412345671."
        result2 = self.scrubber.scrub(text2)
        self.assertEqual(result2.clean_text, "My Emirates ID is [EMIRATES_ID_REDACTED].")

    def test_scrub_phone(self):
        text = "Call me at +971501234567 or 0541234567."
        result = self.scrubber.scrub(text)
        self.assertEqual(result.clean_text, "Call me at [PHONE_REDACTED] or [PHONE_REDACTED].")
        self.assertEqual(len(result.redacted_entities), 2)
        self.assertEqual(result.redacted_entities[0]["type"], "phone")

    def test_scrub_passport(self):
        text = "My passport is AB1234567."
        result = self.scrubber.scrub(text)
        self.assertEqual(result.clean_text, "My passport is [PASSPORT_REDACTED].")
        self.assertEqual(len(result.redacted_entities), 1)

    def test_scrub_iban(self):
        text = "Transfer to AE123451234567890123456."
        result = self.scrubber.scrub(text)
        self.assertEqual(result.clean_text, "Transfer to [IBAN_REDACTED].")
        self.assertEqual(len(result.redacted_entities), 1)

    def test_scrub_email(self):
        text = "Email me at test.user@example.com."
        result = self.scrubber.scrub(text)
        self.assertEqual(result.clean_text, "Email me at [EMAIL_REDACTED].")
        self.assertEqual(len(result.redacted_entities), 1)

    def test_multiple_pii(self):
        text = "Email test@test.com, ID 784-1234-1234567-1, phone 0501234567."
        result = self.scrubber.scrub(text)
        self.assertEqual(result.clean_text, "Email [EMAIL_REDACTED], ID [EMIRATES_ID_REDACTED], phone [PHONE_REDACTED].")
        self.assertEqual(len(result.redacted_entities), 3)

if __name__ == '__main__':
    unittest.main()
