from __future__ import annotations

import unittest

from aoa_v0.models import ActionProposal
from aoa_v0.policy import PolicyGate
from aoa_v0.workflow import AoAWorkflow, build_default_mission


class AoAV0Tests(unittest.TestCase):
    def test_full_baseline_mission_completes_with_grounded_evidence(self):
        workflow = AoAWorkflow()
        state = workflow.run(build_default_mission())
        evaluation = workflow.evaluate(state)
        self.assertEqual(state["status"], "completed")
        self.assertEqual(evaluation["host_recall"], 1.0)
        self.assertEqual(evaluation["service_precision"], 1.0)
        self.assertEqual(evaluation["evidence_coverage"], 1.0)
        self.assertFalse(state["report"]["physical_factory_contact"])

    def test_baseline_does_not_claim_llm_use(self):
        state = AoAWorkflow().run(build_default_mission())
        self.assertEqual(
            state["provider_disclosure"],
            "Deterministic baseline; no LLM call was made",
        )

    def test_out_of_scope_target_fails_closed(self):
        proposal = ActionProposal(
            action_id="A-X",
            objective="test",
            hypothesis="test",
            tool="safe_service_discovery",
            arguments={"target": "198.18.2.8"},
            expected_information="none",
            confidence=0.5,
        )
        decision = PolicyGate().evaluate(build_default_mission(), proposal)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "target_out_of_scope")

    def test_action_budget_stops_workflow(self):
        workflow = AoAWorkflow()
        state = workflow.run(build_default_mission(max_actions=2), thread_id="budget-test")
        self.assertEqual(len(state["observations"]), 2)
        self.assertEqual(state["status"], "completed")


if __name__ == "__main__":
    unittest.main()
