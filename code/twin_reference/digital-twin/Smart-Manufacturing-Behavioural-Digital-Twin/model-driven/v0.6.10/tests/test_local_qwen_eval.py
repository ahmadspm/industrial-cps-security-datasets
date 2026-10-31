import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"runner"))
from local_qwen_eval import FixtureProvider,run,sha256,validate
class Tests(unittest.TestCase):
 def case(self):return json.loads((ROOT/"evals/cases.json").read_text())["cases"][0]
 def plan(self):return FixtureProvider().propose(self.case())[0]
 def test_fixture_eval(self):self.assertEqual(run(ROOT,provider=FixtureProvider())["metrics"]["pass_rate"],1)
 def test_cloud_false(self):self.assertFalse(run(ROOT,provider=FixtureProvider())["cloud_api_used"])
 def test_key_false(self):self.assertFalse(run(ROOT,provider=FixtureProvider())["api_key_used"])
 def test_scope(self):p=self.plan();p["intents"][0]["target"]="vgr";self.assertIn("intent_1_scope",validate(p,self.case()))
 def test_capability(self):p=self.plan();p["intents"][0]["intent"]="scan";self.assertIn("intent_1_capability",validate(p,self.case()))
 def test_grounding(self):p=self.plan();p["intents"][0]["evidence_refs"]=[];self.assertIn("intent_1_grounding",validate(p,self.case()))
 def test_confidence(self):p=self.plan();p["intents"][0]["confidence"]=2;self.assertIn("intent_1_confidence",validate(p,self.case()))
 def test_mission(self):p=self.plan();p["mission_id"]="x";self.assertIn("mission_mismatch",validate(p,self.case()))
 def test_schema(self):p=self.plan();p["extra"]=1;self.assertIn("closed_schema",validate(p,self.case()))
 def test_no_model(self):
  with self.assertRaises(FileNotFoundError):run(ROOT,Path("missing.gguf"))
 def test_manifest(self):
  m=json.loads((ROOT/"model/MODEL-MANIFEST.json").read_text());self.assertEqual(len(m["sha256"]),64);self.assertFalse(m["model_file_committed"])
 def test_safety(self):r=run(ROOT,provider=FixtureProvider());self.assertEqual(r["tool_calls_executed"],0);self.assertFalse(r["physical_writes"])
 def test_human(self):self.assertEqual(run(ROOT,provider=FixtureProvider())["human_approval"]["status"],"pending")
 def test_export(self):
  with tempfile.TemporaryDirectory() as d:run(ROOT,output=Path(d),provider=FixtureProvider());self.assertEqual(json.loads((Path(d)/"local-qwen-evaluation.json").read_text())["version"],"0.6.10")
if __name__=="__main__":unittest.main()
