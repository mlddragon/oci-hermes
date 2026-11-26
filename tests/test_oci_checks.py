import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.oci_checks import list_availability_domains


class ListAvailabilityDomainTests(unittest.TestCase):
    @patch("lib.oci_checks.run")
    def test_parses_ad_names_in_order(self, fake_run):
        payload = {
            "data": [
                {"name": "TEST:US-CHICAGO-1-AD-1"},
                {"name": "TEST:US-CHICAGO-1-AD-2"},
                {"name": "TEST:US-CHICAGO-1-AD-3"},
            ]
        }
        fake_run.return_value = subprocess.CompletedProcess(
            ["oci"], 0, json.dumps(payload), ""
        )

        names = list_availability_domains("ocid1.compartment.oc1..example")

        self.assertEqual(
            names,
            [
                "TEST:US-CHICAGO-1-AD-1",
                "TEST:US-CHICAGO-1-AD-2",
                "TEST:US-CHICAGO-1-AD-3",
            ],
        )
        fake_run.assert_called_once()
        self.assertNotIn("ocid1.compartment.oc1..example", json.dumps(names))


if __name__ == "__main__":
    unittest.main()
