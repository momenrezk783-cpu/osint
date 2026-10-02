import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestMainSecurity(unittest.TestCase):
    @patch("src.main.session_mgr.create_session")
    def test_process_call_text_exception_does_not_leak_details(self, mock_create_session):
        # Setup the mock to raise an exception with sensitive details
        mock_create_session.side_effect = Exception("Sensitive internal detail")

        # Make a request to the endpoint that uses this
        response = client.post(
            "/call/process-text",
            json={
                "caller_id": "test_caller",
                "call_type": "inbound",
                "text": "Hello",
                "intent": "rental_dispute"
            }
        )

        # Check that we get a 500 status code
        self.assertEqual(response.status_code, 500)

        # Check that the sensitive detail is NOT in the response
        response_json = response.json()
        self.assertNotIn("Sensitive internal detail", str(response_json))

        # Check that the response has a generic detail
        self.assertEqual(response_json["detail"], "Internal Server Error")

if __name__ == "__main__":
    unittest.main()
