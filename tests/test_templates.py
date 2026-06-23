import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.config import HermesConfig
from lib.constants import REPO_ROOT
from lib.templates import render_text, template_values


class TemplateTests(unittest.TestCase):
    def test_render_text_replaces_all_placeholders(self):
        rendered = render_text("host={{DUCKDNS_HOSTNAME}} ssh={{SSH_ALLOWED_CIDR}}", {
            "DUCKDNS_HOSTNAME": "quiet-river-47.duckdns.org",
            "SSH_ALLOWED_CIDR": "203.0.113.10/32",
        })

        self.assertEqual(rendered, "host=quiet-river-47.duckdns.org ssh=203.0.113.10/32")

    def test_render_text_rejects_unresolved_placeholders(self):
        with self.assertRaises(ValueError):
            render_text("host={{DUCKDNS_HOSTNAME}} missing={{MISSING}}", {"DUCKDNS_HOSTNAME": "quiet-river-47.duckdns.org"})

    def test_template_values_are_placeholder_free_for_default_config(self):
        config = HermesConfig()
        values = template_values(config, compartment_ocid="compartment-placeholder")

        self.assertEqual(values["REGION"], "us-chicago-1")
        self.assertEqual(values["DUCKDNS_HOSTNAME"], "private-neutral-name.duckdns.org")

    def test_compose_env_template_renders_bridge_values(self):
        config = HermesConfig()
        values = template_values(config, compartment_ocid="compartment-placeholder")
        template = (REPO_ROOT / "deploy/compose/config/hermes.env.tmpl").read_text(encoding="utf-8")

        rendered = render_text(template, values)

        self.assertIn("HERMES_MATRIX_USER_ID=@hermes:private-neutral-name.duckdns.org", rendered)
        self.assertIn("HERMES_TRUSTED_INVITER_IDS=@admin:private-neutral-name.duckdns.org,@primary:private-neutral-name.duckdns.org", rendered)
        self.assertIn("HERMES_OPENAI_ENABLED=false", rendered)
        self.assertNotIn("{{", rendered)


if __name__ == "__main__":
    unittest.main()
