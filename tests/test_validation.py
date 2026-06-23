import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.config import HermesConfig
from lib.validation import ConfigError, validate_duckdns_hostname, validate_ssh_cidr


class ValidationTests(unittest.TestCase):
    def test_rejects_service_revealing_duckdns_label(self):
        with self.assertRaises(ConfigError):
            validate_duckdns_hostname("my-matrix-box.duckdns.org")

    def test_normalizes_safe_duckdns_hostname(self):
        self.assertEqual(validate_duckdns_hostname("quiet-river-47"), "quiet-river-47.duckdns.org")

    def test_rejects_world_open_ssh_by_default(self):
        with self.assertRaises(ConfigError):
            validate_ssh_cidr("0.0.0.0/0")

    def test_accepts_default_config(self):
        config = HermesConfig()
        config.validate()
        self.assertEqual(config.region, "us-chicago-1")


if __name__ == "__main__":
    unittest.main()
