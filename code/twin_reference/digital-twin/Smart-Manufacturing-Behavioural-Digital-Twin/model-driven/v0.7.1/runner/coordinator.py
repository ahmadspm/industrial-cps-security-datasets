"""Governed AOA-ASBIO proposal review and human handoff."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def review(proposal,mission):
 reasons=[];decision="APPROVE"
 if proposal.get("author")!="AOA": reasons.append("invalid_proposer");decision="REJECT"
 if proposal.get("reviewer") in {"AOA",proposal.get("author")} : reasons.append("self_approval_forbidden");decision="REJECT"
 if proposal.get("target") not in mission["authorized_assets"]: reasons.append("target_out_of_scope");decision="REJECT"
 if not proposal.get("evidence_refs"): reasons.append("evidence_required");decision="REVISE" if decision=="APPROVE" else decision
 if proposal.get("confidence",0)>0.95: reasons.append("confidence_requires_calibration");decision="REVISE" if decision=="APPROVE" else decision
 if proposal.get("impact_class") in {"process_change","availability","safety"}: reasons.append("consequential_impact");decision="ESCALATE" if decision=="APPROVE" else decision
 return {"reviewer":"ASBIO","decision":decision,"reasons":reasons,"may_execute":False,"human_approval_required":decision in {"APPROVE","ESCALATE"}}
def run(root,output=None):
 data=json.loads((root/"scenarios/coordination.json").read_text());records=[]
 for p in data["proposals"]:
  r=review(p,data["mission"]);records.append({"proposal_id":p["proposal_id"],"proposal_sha256":hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest(),"review":r})
 report={"schema":"aoa-asbio.coordination/1.0","version":"0.7.1","records":records,"counts":{d:sum(x["review"]["decision"]==d for x in records) for d in ["APPROVE","REVISE","REJECT","ESCALATE"]},"shared_memory_write":"append-only-review-records","tool_calls_executed":0,"network_connections_opened":0,"physical_contact":False,"physical_writes":False,"next_gate":"human_review"}
 if output: output.mkdir(parents=True,exist_ok=True);(output/"coordination-report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 return report
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=Path("evidence/demo"));a=ap.parse_args();print(json.dumps(run(Path(__file__).resolve().parents[1],a.output),indent=2))
if __name__=="__main__":main()
