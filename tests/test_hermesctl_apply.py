import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import hermesctl
from lib.config import HermesConfig


CHICAGO_ADS = [
    "TEST:US-CHICAGO-1-AD-1",
    "TEST:US-CHICAGO-1-AD-2",
    "TEST:US-CHICAGO-1-AD-3",
]


def write_tfvars(directory: Path, availability_domain: str = "") -> Path:
    path = directory / "terraform.tfvars.json"
    path.write_text(
        json.dumps({"availability_domain": availability_domain, "ocpus": 2, "memory_gb": 12}, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


class AvailabilityDomainRotationTests(unittest.TestCase):
    def test_rotate_starts_at_named_ad_and_wraps(self):
        rotated = hermesctl.rotate_availability_domains(CHICAGO_ADS, CHICAGO_ADS[1])
        self.assertEqual(rotated, [CHICAGO_ADS[1], CHICAGO_ADS[2], CHICAGO_ADS[0]])

    def test_rotate_unknown_start_keeps_oci_order(self):
        self.assertEqual(hermesctl.rotate_availability_domains(CHICAGO_ADS, ""), CHICAGO_ADS)


class HermesctlApplyTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.tfvars = write_tfvars(Path(self.tempdir.name))

    def tearDown(self):
        self.tempdir.cleanup()

    @patch("hermesctl.persist_availability_domain")
    @patch("hermesctl.availability_domains_for_apply", return_value=CHICAGO_ADS)
    @patch("hermesctl.time.sleep")
    @patch("hermesctl.run")
    @patch("hermesctl.require_phrase")
    def test_reapply_rotates_ads_before_sleeping(
        self, _fake_phrase, fake_run, fake_sleep, _fake_ads, fake_persist
    ):
        capacity = subprocess.CompletedProcess(["tofu"], 1, "Error: Out of host capacity.\n", "")
        success = subprocess.CompletedProcess(["tofu"], 0, "Apply complete!\n", "")
        fake_run.side_effect = [capacity, capacity, success]

        with patch("hermesctl.require_rendered_tfvars", return_value=self.tfvars):
            hermesctl.cmd_reapply(argparse_namespace())

        self.assertEqual(fake_run.call_count, 3)
        fake_sleep.assert_not_called()
        fake_persist.assert_called_once_with(CHICAGO_ADS[2])
        self.assertEqual(hermesctl.read_tfvars_availability_domain(self.tfvars), CHICAGO_ADS[2])

    @patch("hermesctl.persist_availability_domain")
    @patch("hermesctl.availability_domains_for_apply", return_value=CHICAGO_ADS)
    @patch("hermesctl.time.sleep")
    @patch("hermesctl.run")
    @patch("hermesctl.require_phrase")
    def test_reapply_sleeps_after_full_ad_cycle(
        self, _fake_phrase, fake_run, fake_sleep, _fake_ads, fake_persist
    ):
        capacity = subprocess.CompletedProcess(["tofu"], 1, "Error: Out of host capacity.\n", "")
        success = subprocess.CompletedProcess(["tofu"], 0, "Apply complete!\n", "")
        fake_run.side_effect = [capacity, capacity, capacity, success]

        with patch("hermesctl.require_rendered_tfvars", return_value=self.tfvars):
            hermesctl.cmd_reapply(argparse_namespace())

        self.assertEqual(fake_run.call_count, 4)
        fake_sleep.assert_called_once_with(hermesctl.REAPPLY_RETRY_SECONDS)
        fake_persist.assert_called_once_with(CHICAGO_ADS[0])

    @patch("hermesctl.availability_domains_for_apply", return_value=CHICAGO_ADS)
    @patch("hermesctl.run")
    @patch("hermesctl.require_phrase")
    def test_reapply_exits_on_other_errors(self, _fake_phrase, fake_run, _fake_ads):
        fake_run.return_value = subprocess.CompletedProcess(["tofu"], 3, "Error: something else\n", "")

        with patch("hermesctl.require_rendered_tfvars", return_value=self.tfvars):
            with self.assertRaises(SystemExit) as ctx:
                hermesctl.cmd_reapply(argparse_namespace())

        self.assertEqual(ctx.exception.code, 3)
        fake_run.assert_called_once()

    @patch("hermesctl.run")
    @patch("hermesctl.require_phrase")
    @patch("hermesctl.require_rendered_tfvars")
    def test_apply_does_not_retry(self, fake_tfvars, _fake_phrase, fake_run):
        fake_tfvars.return_value = self.tfvars
        fake_run.return_value = subprocess.CompletedProcess(["tofu"], 0, "Apply complete!\n", "")

        hermesctl.cmd_apply(argparse_namespace())

        fake_run.assert_called_once()
        _, kwargs = fake_run.call_args
        self.assertTrue(kwargs["stream"])
        self.assertNotIn("stream_capture", kwargs)
        command = fake_run.call_args.args[0]
        self.assertNotIn("-auto-approve", command)


class PersistAvailabilityDomainTests(unittest.TestCase):
    @patch("hermesctl.save_config")
    @patch("hermesctl.load_or_exit")
    def test_persist_writes_successful_ad(self, fake_load, fake_save):
        config = HermesConfig(availability_domain="")
        fake_load.return_value = config
        hermesctl.persist_availability_domain(CHICAGO_ADS[1])
        fake_save.assert_called_once()
        self.assertEqual(config.availability_domain, CHICAGO_ADS[1])


def argparse_namespace(**overrides):
    import argparse

    args = argparse.Namespace(verbose=False)
    for key, value in overrides.items():
        setattr(args, key, value)
    return args


if __name__ == "__main__":
    unittest.main()
