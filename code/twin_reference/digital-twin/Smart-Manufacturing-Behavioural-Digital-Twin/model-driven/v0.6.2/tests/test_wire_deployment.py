import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class WireDeploymentTests(unittest.TestCase):
    def test_no_host_ports_or_external_network(self):
        text = (ROOT / "compose.yaml").read_text()
        self.assertNotIn("ports:", text)
        self.assertIn("internal: true", text)
        self.assertNotIn("network_mode: host", text)
        self.assertNotIn("privileged: true", text)

    def test_runtime_secrets_are_not_committed(self):
        self.assertFalse((ROOT / ".secrets").exists())
        self.assertIn(".secrets/", (ROOT / ".gitignore").read_text())

    def test_broker_disables_anonymous_clients(self):
        config = (ROOT / "mosquitto/bootstrap/mosquitto.conf").read_text()
        self.assertIn("allow_anonymous false", config)
        self.assertIn("acl_file", config)

    def test_acl_separates_gateway_twin_and_txt(self):
        acl = (ROOT / "mosquitto/bootstrap/acl").read_text()
        self.assertIn("user gateway", acl)
        self.assertIn("user twin", acl)
        self.assertIn("user txt", acl)
        twin = acl.split("user twin",1)[1].split("user txt",1)[0]
        self.assertNotIn("topic write", twin)

    def test_dependencies_are_pinned(self):
        requirements = (ROOT / "services/requirements.txt").read_text()
        self.assertIn("asyncua==2.0.1", requirements)
        self.assertIn("paho-mqtt==2.1.0", requirements)

    def test_vendor_topics_are_present(self):
        source = (ROOT / "services/app/common.py").read_text()
        for topic in ("f/i/state/dsi","f/i/state/vgr","f/i/state/hbw","f/i/state/mpo","f/i/state/sld"):
            self.assertIn(topic, source)

if __name__ == "__main__": unittest.main()
