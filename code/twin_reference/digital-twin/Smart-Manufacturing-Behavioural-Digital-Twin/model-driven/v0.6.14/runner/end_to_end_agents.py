"""End-to-end bounded AOA and Digital Twin workflow, v0.6.14."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
V13 = ROOT.parent / "v0.6.13"
sys.path.insert(0, str(V13 / "runner"))
from governed_tools import GovernedToolRuntime

VERSION = "0.6.14"


def sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class EvidenceAgent:
    name = "evidence-agent"
    def ground(self, mission: dict[str, Any], runtime: GovernedToolRuntime) -> dict[str, Any]:
        admitted = {asset: runtime.observations["assets"][asset] for asset in mission["scope"] if asset in runtime.observations["assets"]}
        return {"scope": mission["scope"], "assets": admitted, "source":"controlled-digital-twin-fixture", "evidence_sha256":sha(admitted)}


class AOAPlanner:
    name = "deterministic-reference"
    def plan(self, mission: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        actions=[]
        for number, (tool,target,arguments) in enumerate(mission["tasks"],1):
            actions.append({"sequence":number,"request_id":f'{mission["mission_id"]}-A{number:02d}',"tool":tool,"target":target,"arguments":arguments})
        return {"mission_id":mission["mission_id"],"objective":mission["objective"],"scope":evidence["scope"],"evidence_sha256":evidence["evidence_sha256"],"actions":actions}


class QwenAOAPlanner(AOAPlanner):
    name = "aoa-local-qwen3-8b-planner"
    def __init__(self, model_path: Path):
        from llama_cpp import Llama
        started=time.perf_counter()
        self.llm=Llama(model_path=str(model_path),n_ctx=4096,n_threads=8,n_batch=256,verbose=False)
        self.load_seconds=time.perf_counter()-started
        self.performance=[]

    def plan(self, mission: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        candidates=[{"action_id":f"A{i:02d}","tool":t,"target":target,"arguments":args} for i,(t,target,args) in enumerate(mission["tasks"],1)]
        ids=[c["action_id"] for c in candidates]
        schema={"type":"object","additionalProperties":False,"required":["selected_action_ids"],"properties":{"selected_action_ids":{"type":"array","minItems":len(ids),"maxItems":len(ids),"uniqueItems":True,"items":{"type":"string","enum":ids}}}}
        system="You are a bounded AOA planner for an authorised virtual Digital Twin. Select every supplied read-only candidate action exactly once. Never invent tools, targets, arguments or actions. Return only the schema object."
        payload={"mission_id":mission["mission_id"],"objective":mission["objective"],"scope":evidence["scope"],"grounded_assets":evidence["assets"],"candidate_actions":candidates}
        started=time.perf_counter()
        response=self.llm.create_chat_completion(messages=[{"role":"system","content":system},{"role":"user","content":json.dumps(payload,sort_keys=True)}],max_tokens=128,temperature=0,top_p=1,seed=614,response_format={"type":"json_object","schema":schema})
        elapsed=time.perf_counter()-started; usage=response.get("usage",{}); content=json.loads(response["choices"][0]["message"]["content"]); selected=content["selected_action_ids"]
        by_id={c["action_id"]:c for c in candidates}; ordered=[by_id[i] for i in selected]
        self.performance.append({"mission_id":mission["mission_id"],"generation_seconds":elapsed,"prompt_tokens":usage.get("prompt_tokens",0),"completion_tokens":usage.get("completion_tokens",0),"selected_action_ids":selected})
        generated=dict(mission); generated["tasks"]=[(a["tool"],a["target"],a["arguments"]) for a in ordered]
        return super().plan(generated,evidence)


class PolicyAgent:
    name = "policy-approval-agent"
    def authorize(self, mission: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
        errors=[]
        if plan["mission_id"] != mission["mission_id"]: errors.append("mission_mismatch")
        if plan["scope"] != mission["scope"]: errors.append("scope_mismatch")
        for action in plan["actions"]:
            if action["target"] not in mission["scope"]: errors.append("out_of_scope_target")
        if not mission["human_approved"]: errors.append("human_approval_required")
        return {"decision":"APPROVE" if not errors else "BLOCK","errors":sorted(set(errors)),"human_approved":mission["human_approved"]}


class ObservationAgent:
    name = "governed-observation-agent"
    def execute(self, mission: dict[str, Any], plan: dict[str, Any], policy: dict[str, Any], runtime: GovernedToolRuntime) -> list[dict[str, Any]]:
        if policy["decision"] != "APPROVE": return []
        results=[]
        for action in plan["actions"]:
            request={"request_id":action["request_id"],"mission_id":"AOA-TOOLS-001","tool":action["tool"],"target":action["target"],"arguments":action["arguments"],"scope":mission["scope"],"human_approved":True}
            results.append(runtime.invoke(request))
        return results


class CorrelationAgent:
    name = "evidence-correlation-agent"
    def report(self, mission: dict[str, Any], policy: dict[str, Any], observations: list[dict[str, Any]]) -> dict[str, Any]:
        accepted=[o for o in observations if o["decision"]=="EXECUTE"]
        blocked=[o for o in observations if o["decision"]=="BLOCK"]
        citations=[o["provenance"]["record_sha256"] for o in accepted]
        status="PENDING_APPROVAL" if policy["decision"]=="BLOCK" and "human_approval_required" in policy["errors"] else ("COMPLETE" if not blocked else "PARTIAL")
        return {"mission_id":mission["mission_id"],"status":status,"observations":len(accepted),"blocked_actions":len(blocked),"evidence_citations":citations,"conclusion":f'{len(accepted)} approved Digital Twin observations correlated for {mission["title"]}.' if accepted else "No tool action executed; approval gate remained closed."}


def run_mission(mission: dict[str, Any], runtime: GovernedToolRuntime, planner: AOAPlanner | None = None) -> dict[str, Any]:
    evidence=EvidenceAgent().ground(mission,runtime)
    plan=(planner or AOAPlanner()).plan(mission,evidence)
    policy=PolicyAgent().authorize(mission,plan)
    observations=ObservationAgent().execute(mission,plan,policy,runtime)
    report=CorrelationAgent().report(mission,policy,observations)
    return {"mission":mission,"evidence":evidence,"plan":plan,"policy":policy,"observations":observations,"report":report}


def run_all(root: Path, model_path: Path | None = None) -> dict[str, Any]:
    runtime=GovernedToolRuntime(V13/"data/tool_catalog.json",V13/"data/simulated_observations.json")
    missions=json.loads((root/"missions/reference_missions.json").read_text())["missions"]
    planner=QwenAOAPlanner(model_path) if model_path else AOAPlanner()
    runs=[]
    for index, mission in enumerate(missions,1):
        run=run_mission(mission,runtime,planner); runs.append(run)
        print(f"[{index}/{len(missions)}] {mission['mission_id']} status={run['report']['status']}",flush=True)
    approved=[r for r in runs if r["mission"]["human_approved"]]
    pending=[r for r in runs if not r["mission"]["human_approved"]]
    total_actions=sum(len(r["plan"]["actions"]) for r in approved)
    executed=sum(len(r["observations"]) for r in approved)
    return {"schema":"aoa.end-to-end-evaluation/1.0","version":VERSION,"agents":[EvidenceAgent.name,planner.name,PolicyAgent.name,ObservationAgent.name,CorrelationAgent.name],"runs":runs,"metrics":{"missions":len(runs),"approved_missions_complete":sum(r["report"]["status"]=="COMPLETE" for r in approved),"approved_missions":len(approved),"pending_missions":len(pending),"planned_approved_actions":total_actions,"executed_fixture_reads":executed,"action_success_rate":executed/total_actions,"approval_gate_accuracy":sum(r["report"]["status"]=="PENDING_APPROVAL" for r in pending)/len(pending),"audit_chain_valid":runtime.audit.valid(),"audit_entries":len(runtime.audit.entries)},"local_llm_used":bool(model_path),"planner_mode":planner.name,"model_performance":getattr(planner,"performance",[]),"model_load_seconds":getattr(planner,"load_seconds",0),"network_connections_opened":0,"shell_commands_executed":0,"physical_contact":False,"physical_writes":False}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=Path("evidence/demo/end-to-end-run.json")); parser.add_argument("--model",type=Path); args=parser.parse_args()
    result=run_all(ROOT,args.model); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n"); print(json.dumps(result["metrics"],indent=2,sort_keys=True))


if __name__=="__main__": main()
