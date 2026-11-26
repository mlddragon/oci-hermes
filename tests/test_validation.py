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
        self.assertEqual(config.ocpus, 2)
        self.assertEqual(config.memory_gb, 12)
        self.assertEqual(config.model, "hf.co/Qwen/Qwen3-4B-GGUF:Q4_K_M")

    def test_rejects_oversized_always_free_shape(self):
        config = HermesConfig(ocpus=4, memory_gb=24)
        with self.assertRaises(ConfigError):
            config.validate()

    def test_rejects_non_default_local_model(self):
        config = HermesConfig(model="hf.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF:Q4_K_M")
        with self.assertRaises(ConfigError):
            config.validate()


if __name__ == "__main__":
    unittest.main()
