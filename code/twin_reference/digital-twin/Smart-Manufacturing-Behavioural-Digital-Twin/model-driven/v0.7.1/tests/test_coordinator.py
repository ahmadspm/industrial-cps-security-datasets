import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"runner"))
from coordinator import review,run
M={"authorized_assets":["digital_twin","mqtt_broker"]}
P={"proposal_id":"x","author":"AOA","reviewer":"ASBIO","target":"digital_twin","evidence_refs":["e"],"confidence":.8,"impact_class":"observation"}
class Tests(unittest.TestCase):
 def test_approve(self): self.assertEqual(review(P,M)["decision"],"APPROVE")
 def test_self(self): p=P.copy();p["reviewer"]="AOA";self.assertEqual(review(p,M)["decision"],"REJECT")
 def test_scope(self): p=P.copy();p["target"]="vgr";self.assertEqual(review(p,M)["decision"],"REJECT")
 def test_ground(self): p=P.copy();p["evidence_refs"]=[];self.assertEqual(review(p,M)["decision"],"REVISE")
 def test_conf(self): p=P.copy();p["confidence"]=.99;self.assertEqual(review(p,M)["decision"],"REVISE")
 def test_impact(self): p=P.copy();p["impact_class"]="safety";self.assertEqual(review(p,M)["decision"],"ESCALATE")
 def test_noexecute(self): self.assertFalse(review(P,M)["may_execute"])
 def test_human(self): self.assertTrue(review(P,M)["human_approval_required"])
 def test_matrix(self): self.assertEqual(run(ROOT)["counts"],{"APPROVE":1,"REVISE":1,"REJECT":1,"ESCALATE":1})
 def test_hash(self): self.assertEqual(len(run(ROOT)["records"][0]["proposal_sha256"]),64)
 def test_safety(self): self.assertEqual(run(ROOT)["tool_calls_executed"],0)
 def test_export(self):
  with tempfile.TemporaryDirectory() as d: run(ROOT,Path(d));self.assertEqual(json.loads((Path(d)/"coordination-report.json").read_text())["version"],"0.7.1")
if __name__=="__main__":unittest.main()
