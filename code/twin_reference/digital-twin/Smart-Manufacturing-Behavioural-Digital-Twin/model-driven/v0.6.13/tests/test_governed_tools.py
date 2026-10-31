import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
from governed_tools import AuditChain, GovernedToolRuntime, MISSION_ID, build_request, digest, evaluate


class GovernedToolTests(unittest.TestCase):
    def setUp(self):
        self.runtime = GovernedToolRuntime(ROOT / "data/tool_catalog.json", ROOT / "data/simulated_observations.json")
        self.cases = json.loads((ROOT / "evals/tool_cases.json").read_text())["cases"]

    def request(self, case_id): return build_request(next(c for c in self.cases if c["id"] == case_id))
    def test_catalog_has_six_tools(self): self.assertEqual(len(self.runtime.catalog), 6)
    def test_all_tools_read_only(self): self.assertTrue(all(t["read_only"] for t in self.runtime.catalog.values()))
    def test_dataset_has_30_cases(self): self.assertEqual(len(self.cases), 30)
    def test_dataset_has_18_allowed(self): self.assertEqual(sum(c["expect"] == "EXECUTE" for c in self.cases), 18)
    def test_dataset_has_12_blocked(self): self.assertEqual(sum(c["expect"] == "BLOCK" for c in self.cases), 12)
    def test_asset_inventory_allowed(self): self.assertEqual(self.runtime.invoke(self.request("t01"))["decision"], "EXECUTE")
    def test_service_catalog_allowed(self): self.assertEqual(self.runtime.invoke(self.request("t05"))["decision"], "EXECUTE")
    def test_opcua_metadata_allowed(self): self.assertEqual(self.runtime.invoke(self.request("t08"))["decision"], "EXECUTE")
    def test_mqtt_contract_allowed(self): self.assertEqual(self.runtime.invoke(self.request("t10"))["decision"], "EXECUTE")
    def test_passive_flow_allowed(self): self.assertEqual(self.runtime.invoke(self.request("t13"))["decision"], "EXECUTE")
    def test_configuration_allowed(self): self.assertEqual(self.runtime.invoke(self.request("t16"))["decision"], "EXECUTE")
    def test_nmap_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t19"))["reason"], "tool_not_allowlisted")
    def test_shell_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t20"))["decision"], "BLOCK")
    def test_metasploit_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t21"))["decision"], "BLOCK")
    def test_mqtt_publish_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t22"))["decision"], "BLOCK")
    def test_opcua_write_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t23"))["decision"], "BLOCK")
    def test_physical_target_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t24"))["decision"], "BLOCK")
    def test_approval_required(self): self.assertEqual(self.runtime.invoke(self.request("t25"))["reason"], "human_approval_required")
    def test_missing_argument_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t26"))["reason"], "invalid_arguments")
    def test_mismatched_argument_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t27"))["reason"], "argument_target_mismatch")
    def test_extra_argument_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t28"))["reason"], "invalid_arguments")
    def test_unknown_fixture_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t29"))["reason"], "fixture_record_not_found")
    def test_out_of_scope_blocked(self): self.assertEqual(self.runtime.invoke(self.request("t30"))["reason"], "target_out_of_scope")
    def test_wrong_mission_blocked(self):
        request = self.request("t01"); request["mission_id"] = "OTHER"
        self.assertEqual(self.runtime.invoke(request)["reason"], "mission_mismatch")
    def test_closed_schema(self):
        request = self.request("t01"); request["extra"] = True
        self.assertEqual(self.runtime.invoke(request)["reason"], "closed_request_schema")
    def test_provenance_hashes_present(self):
        result = self.runtime.invoke(self.request("t01"))
        self.assertEqual(len(result["provenance"]["record_sha256"]), 64)
    def test_no_network_connections(self): self.assertEqual(self.runtime.invoke(self.request("t01"))["network_connections_opened"], 0)
    def test_no_shell_commands(self): self.assertEqual(self.runtime.invoke(self.request("t01"))["shell_commands_executed"], 0)
    def test_no_physical_contact(self): self.assertFalse(self.runtime.invoke(self.request("t01"))["physical_contact"])
    def test_no_physical_writes(self): self.assertFalse(self.runtime.invoke(self.request("t01"))["physical_writes"])
    def test_audit_chain_valid(self):
        self.runtime.invoke(self.request("t01")); self.runtime.invoke(self.request("t19"))
        self.assertTrue(self.runtime.audit.valid())
    def test_audit_chain_detects_tampering(self):
        self.runtime.invoke(self.request("t01")); self.runtime.audit.entries[0]["decision"] = "BLOCK"
        self.assertFalse(self.runtime.audit.valid())
    def test_digest_deterministic(self): self.assertEqual(digest({"a":1}), digest({"a":1}))
    def test_full_evaluation_passes(self): self.assertEqual(evaluate(ROOT)["metrics"]["decision_accuracy"], 1.0)
    def test_adversarial_block_rate(self): self.assertEqual(evaluate(ROOT)["metrics"]["adversarial_block_rate"], 1.0)
    def test_full_audit_has_30_entries(self): self.assertEqual(evaluate(ROOT)["metrics"]["audit_entries"], 30)


if __name__ == "__main__": unittest.main()
