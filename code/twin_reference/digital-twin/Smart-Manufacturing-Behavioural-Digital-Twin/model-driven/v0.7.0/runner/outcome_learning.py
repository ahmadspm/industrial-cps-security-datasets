"""Governed episodic learning from human-evaluated virtual experiments."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def load(p): return json.loads(p.read_text())
def build_memory(records):
 accepted=[];rejected=[]
 for r in records:
  reasons=[]
  if not r.get("human_reviewed"): reasons.append("human_review_required")
  if r.get("physical_contact") or r.get("physical_writes"): reasons.append("physical_effect_excluded")
  if r.get("outcome") not in {"effective","ineffective","blocked_by_policy"}: reasons.append("invalid_outcome")
  item={"episode_id":r.get("episode_id"),"reasons":reasons}
  if reasons: rejected.append(item);continue
  accepted.append({"episode_id":r["episode_id"],"features":r["features"],"intent":r["intent"],"outcome":r["outcome"],"reward":float(r["reward"]),"evidence_ref":r["evidence_ref"]})
 return {"schema":"aoa.episodic-memory/1.0","episodes":accepted,"rejected":rejected}
def recommend(memory,context):
 scored=[]
 for e in memory["episodes"]:
  overlap=len(set(e["features"])&set(context["features"]))
  score=overlap*2+e["reward"]
  scored.append({"episode_id":e["episode_id"],"intent":e["intent"],"score":score,"evidence_ref":e["evidence_ref"],"outcome":e["outcome"]})
 scored.sort(key=lambda x:(-x["score"],x["episode_id"]))
 return {"recommended_intent":scored[0]["intent"] if scored else "prepare_recon_summary","supporting_episodes":scored[:3],"model_weights_changed":False,"human_approval_required":True}
def run(root,output=None):
 data=load(root/"data/evaluated-outcomes.json");memory=build_memory(data["records"]);rec=recommend(memory,data["query"])
 report={"version":"0.7.0","learning_method":"governed-episodic-retrieval","memory":memory,"recommendation":rec,"records_ingested":len(memory["episodes"]),"records_rejected":len(memory["rejected"]),"tool_calls_executed":0,"physical_contact":False,"physical_writes":False,"memory_sha256":hashlib.sha256(json.dumps(memory,sort_keys=True).encode()).hexdigest()}
 if output: output.mkdir(parents=True,exist_ok=True);(output/"learning-report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 return report
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=Path("evidence/demo"));a=ap.parse_args();print(json.dumps(run(Path(__file__).resolve().parents[1],a.output),indent=2))
if __name__=="__main__":main()
