import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))

from recon_agent import Authorization, GovernanceError, GovernedReconAgent, execute, load


class GovernedReconTests(unittest.TestCase):
    def agent(self):
        return GovernedReconAgent(load(ROOT / "config/virtual-assets.json"), Authorization.from_dict(load(ROOT / "scenarios/authorized-recon.json")))

    def test_authorized_recon_completes(self):
        report = execute(ROOT)
        self.assertTrue(report["completed"])
        self.assertGreater(len(report["actions"]), 0)

    def test_no_llm_or_external_execution_is_claimed(self):
        report = execute(ROOT)
        self.assertFalse(report["llm_used"])
        self.assertEqual(report["commands_executed"], 0)
        self.assertEqual(report["network_connections_opened"], 0)

    def test_physical_station_is_denied(self):
        agent = self.agent()
        with self.assertRaises(GovernanceError):
            agent.act("query_virtual_asset_catalogue", "vgr", "test", "T0846", "negative")
        self.assertIn("physical_asset_excluded", agent.denials[0]["reasons"])

    def test_active_scan_action_is_denied(self):
        agent = self.agent()
        with self.assertRaises(GovernanceError):
            agent.act("nmap_scan", "mqtt_broker", "test", "T0846.001", "negative")
        self.assertIn("action_not_authorized", agent.denials[0]["reasons"])

    def test_digital_twin_is_read_only(self):
        report = execute(ROOT)
        self.assertFalse(report["physical_writes"])
        self.assertTrue(all(item["status"] == "simulated-read-only" for item in report["actions"]))

    def test_only_authorized_virtual_assets_are_ranked(self):
        report = execute(ROOT)
        ranked = {item["asset_id"] for item in report["target_ranking"]}
        self.assertFalse(ranked & {"dps","vgr","hbw","mpo","sld"})
        self.assertTrue(ranked <= {"plc_shadow","iot_gateway","txt_controller","mqtt_broker","digital_twin"})

    def test_communication_dependencies_rank_highest(self):
        report = execute(ROOT)
        leaders = {item["asset_id"] for item in report["target_ranking"] if item["score"] == report["target_ranking"][0]["score"]}
        self.assertEqual(leaders, {"iot_gateway", "mqtt_broker"})

    def test_mitre_ics_discovery_mapping_is_present(self):
        techniques = execute(ROOT)["technique_catalogue"]
        self.assertIn("T0846", techniques)
        self.assertIn("T0888", techniques)
        self.assertIn("T0861", techniques)

    def test_existing_impairment_evidence_is_not_called_vulnerability(self):
        report = execute(ROOT)
        self.assertTrue(report["existing_evidence_findings"])
        self.assertTrue(all("not a discovered vulnerability" in item["interpretation"] for item in report["existing_evidence_findings"]))

    def test_unsafe_authorization_flags_fail_closed(self):
        value = load(ROOT / "scenarios/authorized-recon.json")
        value["active_scanning"] = True
        agent = GovernedReconAgent(load(ROOT / "config/virtual-assets.json"), Authorization.from_dict(value))
        with self.assertRaises(GovernanceError):
            agent.act("query_virtual_asset_catalogue", "digital_twin", "test", "T0846", "negative")

    def test_report_requires_human_gate_before_active_testing(self):
        self.assertIn("human_review", execute(ROOT)["next_gate"])

    def test_evidence_export_is_parseable_and_hashed(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            report = execute(ROOT, output)
            stored = json.loads((output / "recon-report.json").read_text())
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(stored["mission_id"], report["mission_id"])
            self.assertEqual(len(manifest["report_sha256"]), 64)


if __name__ == "__main__": unittest.main()
