import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import hermesctl


class HermesctlApplyTests(unittest.TestCase):
    @patch("hermesctl.time.sleep")
    @patch("hermesctl.run")
    @patch("hermesctl.require_phrase")
    @patch("hermesctl.require_rendered_tfvars")
    def test_reapply_retries_on_host_capacity_error(self, fake_tfvars, _fake_phrase, fake_run, fake_sleep):
        fake_tfvars.return_value = Path("/tmp/terraform.tfvars.json")
        capacity = subprocess.CompletedProcess(["tofu"], 1, "│ Error: 500-InternalError, Out of host capacity.\n", "")
        success = subprocess.CompletedProcess(["tofu"], 0, "Apply complete!\n", "")
        fake_run.side_effect = [capacity, success]

        hermesctl.cmd_reapply(argparse_namespace())

        self.assertEqual(fake_run.call_count, 2)
        fake_sleep.assert_called_once_with(hermesctl.REAPPLY_RETRY_SECONDS)
        command = fake_run.call_args_list[0].args[0]
        self.assertIn("-auto-approve", command)
        self.assertIn("-no-color", command)
        self.assertEqual(fake_run.call_args_list[0].kwargs["env"]["TF_IN_AUTOMATION"], "1")

    @patch("hermesctl.run")
    @patch("hermesctl.require_phrase")
    @patch("hermesctl.require_rendered_tfvars")
    def test_reapply_exits_on_other_errors(self, fake_tfvars, _fake_phrase, fake_run):
        fake_tfvars.return_value = Path("/tmp/terraform.tfvars.json")
        fake_run.return_value = subprocess.CompletedProcess(["tofu"], 3, "Error: something else\n", "")

        with self.assertRaises(SystemExit) as ctx:
            hermesctl.cmd_reapply(argparse_namespace())

        self.assertEqual(ctx.exception.code, 3)
        fake_run.assert_called_once()

    @patch("hermesctl.run")
    @patch("hermesctl.require_phrase")
    @patch("hermesctl.require_rendered_tfvars")
    def test_apply_does_not_retry(self, fake_tfvars, _fake_phrase, fake_run):
        fake_tfvars.return_value = Path("/tmp/terraform.tfvars.json")
        fake_run.return_value = subprocess.CompletedProcess(["tofu"], 0, "Apply complete!\n", "")

        hermesctl.cmd_apply(argparse_namespace())

        fake_run.assert_called_once()
        _, kwargs = fake_run.call_args
        self.assertTrue(kwargs["stream"])
        self.assertNotIn("stream_capture", kwargs)
        command = fake_run.call_args.args[0]
        self.assertNotIn("-auto-approve", command)


def argparse_namespace(**overrides):
    import argparse

    args = argparse.Namespace(verbose=False)
    for key, value in overrides.items():
        setattr(args, key, value)
    return args


if __name__ == "__main__":
    unittest.main()
