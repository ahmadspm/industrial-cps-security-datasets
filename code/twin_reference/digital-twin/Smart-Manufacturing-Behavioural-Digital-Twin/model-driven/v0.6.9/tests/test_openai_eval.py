import copy,json,os,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"runner"))
from openai_eval import MockStructuredProvider,OpenAIResponsesProvider,run,validate
class Tests(unittest.TestCase):
 def case(self): return json.loads((ROOT/"evals/cases.json").read_text())["cases"][0]
 def plan(self): return MockStructuredProvider().propose(self.case())
 def test_reference(self): self.assertEqual(run(ROOT)["metrics"]["schema_pass_rate"],1)
 def test_disclosure(self): self.assertFalse(run(ROOT)["live_openai_used"])
 def test_adapter(self): self.assertTrue(run(ROOT)["openai_adapter_implemented"])
 def test_no_key(self):
  with self.assertRaises(RuntimeError): OpenAIResponsesProvider(api_key="").propose(self.case())
 def test_scope(self): p=self.plan();p["intents"][0]["target"]="vgr";self.assertIn("intent_1_scope",validate(p,self.case()))
 def test_capability(self): p=self.plan();p["intents"][0]["intent"]="scan";self.assertIn("intent_1_capability",validate(p,self.case()))
 def test_grounding(self): p=self.plan();p["intents"][0]["evidence_refs"]=[];self.assertIn("intent_1_grounding",validate(p,self.case()))
 def test_confidence(self): p=self.plan();p["intents"][0]["confidence"]=2;self.assertIn("intent_1_confidence",validate(p,self.case()))
 def test_mission(self): p=self.plan();p["mission_id"]="other";self.assertIn("mission_mismatch",validate(p,self.case()))
 def test_schema(self): p=self.plan();p["extra"]=1;self.assertIn("closed_schema",validate(p,self.case()))
 def test_nonexecution(self): self.assertEqual(run(ROOT)["tool_calls_executed"],0)
 def test_export(self):
  with tempfile.TemporaryDirectory() as d: run(ROOT,Path(d));self.assertEqual(json.loads((Path(d)/"evaluation-report.json").read_text())["version"],"0.6.9")
if __name__=="__main__":unittest.main()
