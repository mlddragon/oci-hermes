import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.redaction import redact_mapping, redact_text


class RedactionTests(unittest.TestCase):
    def test_redacts_common_deployment_identifiers(self):
        openai_key = "sk-" + "a" * 20
        text = "ip 198.51.100.20 token 11111111-2222-3333-4444-555555555555 " + openai_key

        redacted = redact_text(text)

        self.assertNotIn("198.51.100.20", redacted)
        self.assertNotIn(openai_key, redacted)
        self.assertIn("[REDACTED_IP]", redacted)
        self.assertIn("[REDACTED_OPENAI_KEY]", redacted)

    def test_redacts_secret_like_mapping_keys(self):
        redacted = redact_mapping({"duckdns_token": "value", "nested": {"api_key": "value"}})

        self.assertEqual(redacted["duckdns_token"], "[REDACTED]")
        self.assertEqual(redacted["nested"]["api_key"], "[REDACTED]")


if __name__ == "__main__":
    unittest.main()
