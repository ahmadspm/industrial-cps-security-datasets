import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
from end_to_end_agents import EvidenceAgent, AOAPlanner, PolicyAgent, ObservationAgent, CorrelationAgent, run_all, run_mission, V13
sys.path.insert(0,str(V13/"runner"))
from governed_tools import GovernedToolRuntime

class EndToEndTests(unittest.TestCase):
    def setUp(self):
        self.runtime=GovernedToolRuntime(V13/"data/tool_catalog.json",V13/"data/simulated_observations.json")
        self.missions=json.loads((ROOT/"missions/reference_missions.json").read_text())["missions"]
    def test_five_agents_defined(self): self.assertEqual(len(run_all(ROOT)["agents"]),5)
    def test_five_missions_defined(self): self.assertEqual(len(self.missions),5)
    def test_evidence_is_scoped(self): self.assertEqual(set(EvidenceAgent().ground(self.missions[0],self.runtime)["assets"]),set(self.missions[0]["scope"]))
    def test_plan_mission_preserved(self):
        e=EvidenceAgent().ground(self.missions[0],self.runtime); p=AOAPlanner().plan(self.missions[0],e); self.assertEqual(p["mission_id"],self.missions[0]["mission_id"])
    def test_plan_sequence_ordered(self):
        e=EvidenceAgent().ground(self.missions[0],self.runtime); p=AOAPlanner().plan(self.missions[0],e); self.assertEqual([a["sequence"] for a in p["actions"]],list(range(1,len(p["actions"])+1)))
    def test_approved_policy(self):
        m=self.missions[0]; e=EvidenceAgent().ground(m,self.runtime); self.assertEqual(PolicyAgent().authorize(m,AOAPlanner().plan(m,e))["decision"],"APPROVE")
    def test_unapproved_policy_blocked(self):
        m=self.missions[-1]; e=EvidenceAgent().ground(m,self.runtime); self.assertIn("human_approval_required",PolicyAgent().authorize(m,AOAPlanner().plan(m,e))["errors"])
    def test_wrong_mission_blocked(self):
        m=self.missions[0]; e=EvidenceAgent().ground(m,self.runtime); p=AOAPlanner().plan(m,e); p["mission_id"]="WRONG"; self.assertIn("mission_mismatch",PolicyAgent().authorize(m,p)["errors"])
    def test_scope_expansion_blocked(self):
        m=self.missions[0]; e=EvidenceAgent().ground(m,self.runtime); p=AOAPlanner().plan(m,e); p["actions"][0]["target"]="physical_plc"; self.assertIn("out_of_scope_target",PolicyAgent().authorize(m,p)["errors"])
    def test_topology_mission_complete(self): self.assertEqual(run_mission(self.missions[0],self.runtime)["report"]["status"],"COMPLETE")
    def test_opcua_mission_complete(self): self.assertEqual(run_mission(self.missions[1],self.runtime)["report"]["status"],"COMPLETE")
    def test_mqtt_mission_complete(self): self.assertEqual(run_mission(self.missions[2],self.runtime)["report"]["status"],"COMPLETE")
    def test_station_mission_complete(self): self.assertEqual(run_mission(self.missions[3],self.runtime)["report"]["status"],"COMPLETE")
    def test_unapproved_mission_pending(self): self.assertEqual(run_mission(self.missions[4],self.runtime)["report"]["status"],"PENDING_APPROVAL")
    def test_unapproved_executes_nothing(self): self.assertEqual(len(run_mission(self.missions[4],self.runtime)["observations"]),0)
    def test_reports_have_citations(self): self.assertTrue(run_mission(self.missions[0],self.runtime)["report"]["evidence_citations"])
    def test_citations_are_hashes(self): self.assertTrue(all(len(x)==64 for x in run_mission(self.missions[0],self.runtime)["report"]["evidence_citations"]))
    def test_all_approved_actions_execute(self): self.assertEqual(run_all(ROOT)["metrics"]["action_success_rate"],1.0)
    def test_four_approved_complete(self): self.assertEqual(run_all(ROOT)["metrics"]["approved_missions_complete"],4)
    def test_approval_gate_accuracy(self): self.assertEqual(run_all(ROOT)["metrics"]["approval_gate_accuracy"],1.0)
    def test_audit_chain_valid(self): self.assertTrue(run_all(ROOT)["metrics"]["audit_chain_valid"])
    def test_audit_entries_match_actions(self): self.assertEqual(run_all(ROOT)["metrics"]["audit_entries"],16)
    def test_no_network(self): self.assertEqual(run_all(ROOT)["network_connections_opened"],0)
    def test_no_shell(self): self.assertEqual(run_all(ROOT)["shell_commands_executed"],0)
    def test_no_physical_contact(self): self.assertFalse(run_all(ROOT)["physical_contact"])
    def test_no_physical_writes(self): self.assertFalse(run_all(ROOT)["physical_writes"])
    def test_reference_planner_disclosed(self): self.assertEqual(run_all(ROOT)["planner_mode"],"deterministic-reference")
    def test_no_llm_claim(self): self.assertFalse(run_all(ROOT)["local_llm_used"])

if __name__=="__main__": unittest.main()
