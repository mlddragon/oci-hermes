import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.runner import _filter_captured_output, run, set_verbose


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        set_verbose(False)

    def test_stream_mode_does_not_capture_interactive_command_output(self):
        completed = subprocess.CompletedProcess(["fake"], 0, "ok\n", "")

        with patch("lib.runner._run_streamed", return_value=completed) as fake_stream:
            result = run(["fake"], stream=True)

        self.assertIs(result, completed)
        fake_stream.assert_called_once()

    def test_stream_capture_returns_combined_output(self):
        completed = subprocess.CompletedProcess(["fake"], 1, "failed\n", "")

        with patch("lib.runner._run_streamed", return_value=completed) as fake_stream:
            result = run(["fake"], stream=True, stream_capture=True, check=False)

        self.assertEqual(result.stdout, "failed\n")
        fake_stream.assert_called_once_with(["fake"], None, verbose=False, capture=True, env=None)

    def test_filter_captured_output_hides_traceback_but_keeps_error_line(self):
        text = (
            "Traceback (most recent call last):\n"
            '  File "tool.py", line 1, in <module>\n'
            "    boom()\n"
            "RuntimeError: boom\n"
            "normal output\n"
        )

        filtered = _filter_captured_output(text, verbose=False)

        self.assertNotIn("Traceback", filtered)
        self.assertNotIn('File "tool.py"', filtered)
        self.assertIn("RuntimeError: boom\n", filtered)
        self.assertIn("normal output\n", filtered)

    def test_filter_captured_output_shows_traceback_when_verbose(self):
        text = "Traceback (most recent call last):\n  File \"tool.py\", line 1\nValueError: nope\n"

        filtered = _filter_captured_output(text, verbose=True)

        self.assertEqual(filtered, text)

    def test_filter_captured_output_hides_debug_lines(self):
        text = "INFO: starting\nDEBUG: secret detail\nINFO: done\n"

        filtered = _filter_captured_output(text, verbose=False)

        self.assertIn("INFO: starting\n", filtered)
        self.assertNotIn("DEBUG: secret detail\n", filtered)
        self.assertIn("INFO: done\n", filtered)


if __name__ == "__main__":
    unittest.main()
