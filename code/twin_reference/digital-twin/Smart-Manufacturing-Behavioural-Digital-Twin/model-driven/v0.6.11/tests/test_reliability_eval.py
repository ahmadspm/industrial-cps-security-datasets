import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
from reliability_eval import (FixtureProvider, evaluate_case, metrics, plan_schema,
                              run, validate)


class BrokenThenRepairProvider(FixtureProvider):
    def propose(self, case, attempt=0, prior=None, errors=None):
        plan, perf = super().propose(case, attempt, prior, errors)
        if attempt == 0:
            plan["intents"][0]["target"] = "physical_plc"
        return plan, perf


class AlwaysBrokenProvider(FixtureProvider):
    def propose(self, case, attempt=0, prior=None, errors=None):
        return {"mission_id": "wrong", "intents": []}, {"generation_seconds": 0, "prompt_tokens": 0, "completion_tokens": 0, "tokens_per_second": 0}


class ReliabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ROOT / "evals/cases.json").read_text())["cases"]
        cls.case = cls.cases[0]

    def plan(self):
        return FixtureProvider().propose(self.case)[0]

    def test_benchmark_has_30_cases(self): self.assertEqual(len(self.cases), 30)
    def test_benchmark_has_six_adversarial_cases(self): self.assertEqual(sum(c.get("adversarial", False) for c in self.cases), 6)
    def test_benchmark_covers_five_categories(self): self.assertEqual({c["category"] for c in self.cases}, {"topology", "protocol", "station", "evidence", "adversarial"})
    def test_schema_is_closed(self): self.assertFalse(plan_schema(self.case)["additionalProperties"])
    def test_schema_constrains_mission(self): self.assertEqual(plan_schema(self.case)["properties"]["mission_id"]["const"], self.case["mission_id"])
    def test_schema_constrains_targets(self): self.assertEqual(plan_schema(self.case)["properties"]["intents"]["items"]["properties"]["target"]["enum"], self.case["authorized_assets"])
    def test_valid_fixture(self): self.assertEqual(validate(self.plan(), self.case), [])
    def test_scope_escape_rejected(self):
        plan = self.plan(); plan["intents"][0]["target"] = "physical_plc"
        self.assertIn("intent_1_scope", validate(plan, self.case))
    def test_unknown_evidence_rejected(self):
        plan = self.plan(); plan["intents"][0]["evidence_refs"] = ["invented.json"]
        self.assertIn("intent_1_grounding", validate(plan, self.case))
    def test_unknown_capability_rejected(self):
        plan = self.plan(); plan["intents"][0]["intent"] = "scan_network"
        self.assertIn("intent_1_capability", validate(plan, self.case))
    def test_extra_property_rejected(self):
        plan = self.plan(); plan["command"] = "nmap"
        self.assertIn("closed_schema", validate(plan, self.case))
    def test_bool_confidence_rejected(self):
        plan = self.plan(); plan["intents"][0]["confidence"] = True
        self.assertIn("intent_1_confidence", validate(plan, self.case))
    def test_short_rationale_rejected(self):
        plan = self.plan(); plan["intents"][0]["rationale"] = "short"
        self.assertIn("intent_1_rationale", validate(plan, self.case))
    def test_repair_is_bounded_and_recorded(self):
        row = evaluate_case(BrokenThenRepairProvider(), self.case, 1)
        self.assertTrue(row["accepted"]); self.assertTrue(row["repaired"]); self.assertEqual(row["attempt_count"], 2)
    def test_failure_remains_fail_closed(self):
        row = evaluate_case(AlwaysBrokenProvider(), self.case, 1)
        self.assertFalse(row["accepted"]); self.assertIsNone(row["plan"]); self.assertEqual(row["attempt_count"], 2)
    def test_zero_repairs_means_one_attempt(self): self.assertEqual(evaluate_case(AlwaysBrokenProvider(), self.case, 0)["attempt_count"], 1)
    def test_fixture_benchmark_passes(self): self.assertEqual(run(ROOT, provider=FixtureProvider())["metrics"]["policy_acceptance_rate"], 1)
    def test_safety_counters(self):
        report = run(ROOT, provider=FixtureProvider())
        self.assertEqual(report["tool_calls_executed"], 0); self.assertFalse(report["physical_writes"]); self.assertFalse(report["cloud_api_used"])
    def test_human_approval_pending(self): self.assertEqual(run(ROOT, provider=FixtureProvider())["human_approval"]["status"], "pending")
    def test_evidence_export(self):
        with tempfile.TemporaryDirectory() as directory:
            run(ROOT, output=Path(directory), provider=FixtureProvider())
            report = json.loads((Path(directory) / "qwen-reliability-evaluation.json").read_text())
            self.assertEqual(report["version"], "0.6.11")
    def test_missing_model_fails(self):
        with self.assertRaises(FileNotFoundError): run(ROOT, Path("missing.gguf"))
    def test_metrics_include_percentiles(self): self.assertIn("p95_generation_seconds", metrics([evaluate_case(FixtureProvider(), self.case)]))


if __name__ == "__main__":
    unittest.main()
