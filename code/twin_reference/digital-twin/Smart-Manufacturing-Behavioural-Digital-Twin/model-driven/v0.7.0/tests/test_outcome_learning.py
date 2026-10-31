import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"runner"))
from outcome_learning import build_memory,recommend,run
class Tests(unittest.TestCase):
 def records(self): return json.loads((ROOT/"data/evaluated-outcomes.json").read_text())["records"]
 def test_ingest(self): self.assertEqual(run(ROOT)["records_ingested"],3)
 def test_reject(self): self.assertEqual(run(ROOT)["records_rejected"],1)
 def test_human(self): self.assertIn("human_review_required",build_memory(self.records())["rejected"][0]["reasons"])
 def test_physical(self): r=self.records()[0].copy();r["physical_contact"]=True;self.assertEqual(len(build_memory([r])["episodes"]),0)
 def test_invalid(self): r=self.records()[0].copy();r["outcome"]="unknown";self.assertEqual(len(build_memory([r])["episodes"]),0)
 def test_recommend(self): self.assertEqual(run(ROOT)["recommendation"]["recommended_intent"],"correlate_recorded_evidence")
 def test_provenance(self): self.assertTrue(all(x["evidence_ref"] for x in run(ROOT)["memory"]["episodes"]))
 def test_weights(self): self.assertFalse(run(ROOT)["recommendation"]["model_weights_changed"])
 def test_approval(self): self.assertTrue(run(ROOT)["recommendation"]["human_approval_required"])
 def test_hash(self): self.assertEqual(len(run(ROOT)["memory_sha256"]),64)
 def test_nonexecution(self): self.assertEqual(run(ROOT)["tool_calls_executed"],0)
 def test_export(self):
  with tempfile.TemporaryDirectory() as d: run(ROOT,Path(d));self.assertEqual(json.loads((Path(d)/"learning-report.json").read_text())["version"],"0.7.0")
if __name__=="__main__":unittest.main()
