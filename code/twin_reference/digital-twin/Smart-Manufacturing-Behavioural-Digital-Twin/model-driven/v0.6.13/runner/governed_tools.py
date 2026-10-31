"""Governed, fixture-only Digital Twin observation tools for AOA v0.6.13."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VERSION = "0.6.13"
MISSION_ID = "AOA-TOOLS-001"


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class Decision:
    status: str
    reason: str


class AuditChain:
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        previous = self.entries[-1]["entry_hash"] if self.entries else "GENESIS"
        entry = {"sequence": len(self.entries) + 1, "previous_hash": previous, **event}
        entry["entry_hash"] = digest(entry)
        self.entries.append(entry)
        return entry

    def valid(self) -> bool:
        previous = "GENESIS"
        for number, entry in enumerate(self.entries, 1):
            candidate = {k: v for k, v in entry.items() if k != "entry_hash"}
            if entry["sequence"] != number or entry["previous_hash"] != previous:
                return False
            if digest(candidate) != entry["entry_hash"]:
                return False
            previous = entry["entry_hash"]
        return True


class GovernedToolRuntime:
    """Executes only deterministic reads from a controlled fixture."""

    def __init__(self, catalog_path: Path, observations_path: Path):
        catalog = json.loads(catalog_path.read_text())
        self.catalog = {tool["name"]: tool for tool in catalog["tools"]}
        self.observations = json.loads(observations_path.read_text())
        self.catalog_hash = digest(catalog)
        self.observations_hash = digest(self.observations)
        self.audit = AuditChain()

    def authorize(self, request: dict[str, Any]) -> Decision:
        required = {"request_id", "mission_id", "tool", "target", "arguments", "scope", "human_approved"}
        if set(request) != required:
            return Decision("BLOCK", "closed_request_schema")
        if request["mission_id"] != MISSION_ID:
            return Decision("BLOCK", "mission_mismatch")
        if request["human_approved"] is not True:
            return Decision("BLOCK", "human_approval_required")
        tool = self.catalog.get(request["tool"])
        if not tool:
            return Decision("BLOCK", "tool_not_allowlisted")
        if tool["read_only"] is not True:
            return Decision("BLOCK", "tool_not_read_only")
        if request["target"] not in request["scope"]:
            return Decision("BLOCK", "target_out_of_scope")
        if request["target"] not in tool["allowed_targets"]:
            return Decision("BLOCK", "target_not_allowed_for_tool")
        arguments = request["arguments"]
        if not isinstance(arguments, dict) or set(arguments) != {tool["required_argument"]}:
            return Decision("BLOCK", "invalid_arguments")
        if tool["required_argument"] == "asset" and arguments["asset"] != request["target"]:
            return Decision("BLOCK", "argument_target_mismatch")
        return Decision("EXECUTE", "authorized_fixture_read")

    def _observe(self, request: dict[str, Any]) -> Any:
        tool, arg = request["tool"], next(iter(request["arguments"].values()))
        section = {
            "asset_inventory": "assets", "service_catalog": "services",
            "opcua_metadata": "opcua", "mqtt_contract": "mqtt",
            "passive_flow_evidence": "flows", "configuration_evidence": "configurations",
        }[tool]
        if arg not in self.observations[section]:
            raise KeyError("fixture_record_not_found")
        return self.observations[section][arg]

    def invoke(self, request: dict[str, Any]) -> dict[str, Any]:
        decision = self.authorize(request)
        result: dict[str, Any] = {
            "request_id": request.get("request_id", "unknown"),
            "decision": decision.status, "reason": decision.reason,
            "tool": request.get("tool"), "target": request.get("target"),
            "network_connections_opened": 0, "physical_contact": False,
            "physical_writes": False, "shell_commands_executed": 0,
        }
        if decision.status == "EXECUTE":
            try:
                observation = self._observe(request)
            except KeyError:
                result.update(decision="BLOCK", reason="fixture_record_not_found")
            else:
                provenance = {
                    "snapshot_id": self.observations["snapshot_id"],
                    "source": self.observations["source"],
                    "observations_sha256": self.observations_hash,
                    "record_sha256": digest(observation),
                }
                result.update(observation=observation, provenance=provenance)
        self.audit.append({"request_hash": digest(request), "result_hash": digest(result), "decision": result["decision"]})
        return result


def build_request(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": case["id"], "mission_id": MISSION_ID, "tool": case["tool"],
        "target": case["target"], "arguments": case["arguments"],
        "scope": case["scope"], "human_approved": case["approved"],
    }


def evaluate(root: Path) -> dict[str, Any]:
    runtime = GovernedToolRuntime(root / "data/tool_catalog.json", root / "data/simulated_observations.json")
    cases = json.loads((root / "evals/tool_cases.json").read_text())["cases"]
    rows = []
    for case in cases:
        result = runtime.invoke(build_request(case))
        rows.append({
            "case_id": case["id"], "expected": case["expect"], "actual": result["decision"],
            "passed": result["decision"] == case["expect"], "adversarial": case.get("adversarial", False),
            "reason": result["reason"], "provenance_complete": result["decision"] != "EXECUTE" or
                set(result.get("provenance", {})) == {"snapshot_id", "source", "observations_sha256", "record_sha256"},
            "result": result,
        })
    allowed = [r for r in rows if r["expected"] == "EXECUTE"]
    blocked = [r for r in rows if r["expected"] == "BLOCK"]
    adversarial = [r for r in rows if r["adversarial"]]
    return {
        "schema": "aoa.governed-tool-evaluation/1.0", "version": VERSION,
        "mission_id": MISSION_ID, "runtime": "fixture-only-read-runtime",
        "catalog_sha256": runtime.catalog_hash, "observations_sha256": runtime.observations_hash,
        "cases": rows,
        "metrics": {
            "cases": len(rows), "passed": sum(r["passed"] for r in rows),
            "decision_accuracy": sum(r["passed"] for r in rows) / len(rows),
            "authorized_execution_rate": sum(r["passed"] for r in allowed) / len(allowed),
            "blocked_request_rate": sum(r["passed"] for r in blocked) / len(blocked),
            "adversarial_block_rate": sum(r["actual"] == "BLOCK" for r in adversarial) / len(adversarial),
            "provenance_completeness": sum(r["provenance_complete"] for r in rows) / len(rows),
            "audit_chain_valid": runtime.audit.valid(), "audit_entries": len(runtime.audit.entries),
        },
        "audit_chain": runtime.audit.entries,
        "network_connections_opened": 0, "shell_commands_executed": 0,
        "physical_contact": False, "physical_writes": False,
        "human_approval_enforced": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("evidence/demo/governed-tool-evaluation.json"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = evaluate(root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["metrics"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
