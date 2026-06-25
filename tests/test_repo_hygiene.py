import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_repo_hygiene import forbidden_tracked_paths, is_forbidden_tracked_path


class RepoHygieneTests(unittest.TestCase):
    def test_tracked_template_paths_are_allowed(self):
        allowed = [
            "infra/oci/templates/terraform-vars.json.tmpl",
            "deploy/compose/config/hermes.env.tmpl",
            "deploy/caddy/templates/Caddyfile.tmpl",
        ]

        self.assertEqual(forbidden_tracked_paths(allowed), [])

    def test_generated_artifact_paths_are_forbidden(self):
        forbidden = [
            ".hermes/rendered/terraform.tfvars.json",
            "infra/oci/terraform.tfvars",
            "infra/oci/plan.tfplan",
            "secrets/duckdns.env",
            "matrix-data/store.db",
        ]

        self.assertEqual(forbidden_tracked_paths(forbidden), forbidden)

    def test_legacy_broad_tfvars_pattern_false_positive_is_fixed(self):
        legacy_pattern = re.compile(r".*\.tfvars(\.json)?")
        path = "infra/oci/templates/terraform.tfvars.json.tmpl"

        self.assertIsNotNone(legacy_pattern.search(path))
        self.assertFalse(is_forbidden_tracked_path(path))

    def test_current_repo_has_no_forbidden_tracked_paths(self):
        tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()

        self.assertEqual(forbidden_tracked_paths(tracked), [])


if __name__ == "__main__":
    unittest.main()
