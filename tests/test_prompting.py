import builtins
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.prompting import require_phrase


class PromptingTests(unittest.TestCase):
    def test_require_phrase_blocks_mismatch(self):
        with patch.object(builtins, "input", return_value="wrong"):
            with self.assertRaises(SystemExit):
                require_phrase("APPLY OCI HERMES")

    def test_require_phrase_accepts_exact_match(self):
        with patch.object(builtins, "input", return_value="APPLY OCI HERMES"):
            require_phrase("APPLY OCI HERMES")


if __name__ == "__main__":
    unittest.main()
