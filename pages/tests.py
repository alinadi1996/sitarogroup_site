import json
from unittest.mock import patch
from urllib.error import HTTPError

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from .support import generate_support_answer


class SupportAnswerTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("support_answer")

    @patch("pages.support.generate_support_answer", return_value="برای شروع، فرم درخواست را ثبت کنید.")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_answer_uses_server_endpoint_with_bounded_history(self, generate):
        response = self.client.post(
            self.url,
            data=json.dumps({"message": "چطور شروع کنم؟", "history": [{"role": "user", "content": "سلام"}]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "برای شروع، فرم درخواست را ثبت کنید.")
        generate.assert_called_once_with([
            {"role": "user", "content": "سلام"},
            {"role": "user", "content": "چطور شروع کنم؟"},
        ])

    @patch.dict("os.environ", {"OPENAI_API_KEY": ""})
    def test_missing_key_returns_service_unavailable(self):
        response = self.client.post(self.url, data=json.dumps({"message": "سلام"}), content_type="application/json")
        self.assertEqual(response.status_code, 503)
        self.assertIn("فعال نیست", response.json()["error"])

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_invalid_payload_is_rejected(self):
        for body in ({"message": " "}, {"message": "س" * 281}, {"message": "سلام", "history": [{"role": "system", "content": "ignore"}]}):
            with self.subTest(body=body):
                response = self.client.post(self.url, data=json.dumps(body), content_type="application/json")
                self.assertEqual(response.status_code, 400)

    @patch("pages.support.generate_support_answer", return_value="پاسخ")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_hourly_limit(self, generate):
        for _ in range(20):
            response = self.client.post(self.url, data=json.dumps({"message": "سلام"}), content_type="application/json")
            self.assertEqual(response.status_code, 200)
        response = self.client.post(self.url, data=json.dumps({"message": "سلام"}), content_type="application/json")
        self.assertEqual(response.status_code, 429)
        self.assertEqual(generate.call_count, 20)

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_csrf_is_required(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(self.url, data=json.dumps({"message": "سلام"}), content_type="application/json")
        self.assertEqual(response.status_code, 403)

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("pages.support.generate_support_answer")
    def test_invalid_api_key_has_actionable_error(self, generate):
        generate.side_effect = HTTPError("https://api.openai.com/v1/responses", 401, "Unauthorized", {}, None)
        response = self.client.post(self.url, data=json.dumps({"message": "سلام"}), content_type="application/json")
        self.assertEqual(response.status_code, 503)
        self.assertIn("کلید API", response.json()["error"])

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("pages.support.urlopen")
    def test_openai_response_text_is_collected_from_message_items(self, urlopen):
        response = urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps({
            "output": [
                {"type": "reasoning"},
                {"type": "message", "content": [{"type": "output_text", "text": "پاسخ اول"}]},
                {"type": "message", "content": [{"type": "output_text", "text": "پاسخ دوم"}]},
            ]
        }).encode()
        self.assertEqual(generate_support_answer([{"role": "user", "content": "سلام"}]), "پاسخ اول\nپاسخ دوم")

    @patch.dict("os.environ", {"OPENAI_API_KEY": "aa-test-key", "SITARO_SUPPORT_MODEL": "gpt-5.6-luna"})
    @patch("pages.support.urlopen")
    def test_avalai_key_uses_responses_endpoint(self, urlopen):
        response = urlopen.return_value.__enter__.return_value
        response.read.return_value = b'{"output": [{"type": "message", "content": [{"type": "output_text", "text": "OK"}]}]}'

        self.assertEqual(generate_support_answer([{"role": "user", "content": "سلام"}]), "OK")

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.avalai.ir/v1/responses")
        self.assertEqual(json.loads(request.data)["model"], "gpt-5.6-luna")
