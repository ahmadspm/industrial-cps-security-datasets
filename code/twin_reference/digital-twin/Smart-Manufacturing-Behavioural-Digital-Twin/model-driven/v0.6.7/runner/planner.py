"""LLM-ready, fail-closed planning boundary for governed virtual reconnaissance."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Protocol


ALLOWED_INTENTS = {
    "inspect_asset_metadata",
    "inspect_protocol_contract",
    "correlate_recorded_evidence",
    "compare_declared_dependencies",
    "prepare_recon_summary",
}
PROHIBITED_TERMS = re.compile(
    r"\b(nmap|masscan|metasploit|msfconsole|exploit|shell|socket|connect|write|upload|download|"
    r"credential|password|physical|scan|probe)\b",
    re.IGNORECASE,
)
INJECTION_MARKERS = re.compile(
    r"(ignore (all |any )?(previous|prior|system) instructions|system prompt|developer message|"
    r"override (the )?(policy|mission)|you are now|execute this command)",
    re.IGNORECASE,
)


class PlanningError(ValueError):
    pass


class PlannerProvider(Protocol):
    name: str

    def propose(self, context: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class ToolIntent:
    step: int
    intent: str
    target: str
    evidence_refs: tuple[str, ...]
    rationale: str
    expected_output: str
    confidence: float
    execution: str = "not-executed"


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sanitize_evidence(value: Any, path: str = "$") -> tuple[Any, list[dict[str, str]]]:
    """Quarantine instruction-like strings while preserving their provenance."""
    quarantined: list[dict[str, str]] = []
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            result[key], findings = sanitize_evidence(child, f"{path}.{key}")
            quarantined.extend(findings)
        return result, quarantined
    if isinstance(value, list):
        result = []
        for index, child in enumerate(value):
            clean, findings = sanitize_evidence(child, f"{path}[{index}]")
            result.append(clean)
            quarantined.extend(findings)
        return result, quarantined
    if isinstance(value, str) and INJECTION_MARKERS.search(value):
        quarantined.append({"path": path, "sha256": hashlib.sha256(value.encode()).hexdigest(), "reason": "instruction_like_evidence"})
        return "[QUARANTINED_INSTRUCTION_LIKE_CONTENT]", quarantined
    return value, quarantined


class DeterministicPlanner:
    name = "deterministic-fallback"

    def propose(self, context: dict[str, Any]) -> dict[str, Any]:
        mission = context["mission"]
        recon = context["evidence"]
        ranked = [item["asset_id"] for item in recon.get("target_ranking", [])]
        preferred = [target for target in ranked if target in mission["authorized_assets"]]
        primary = preferred[0] if preferred else "digital_twin"
        proposals = [
            ("inspect_asset_metadata", primary, ("recon-report.json#/target_ranking",), "Confirm declared virtual role and zone", "metadata comparison"),
            ("inspect_protocol_contract", "digital_twin", ("recon-report.json#/technique_catalogue",), "Review approved topic and logical-node contracts", "contract inventory"),
            ("correlate_recorded_evidence", "digital_twin", ("recon-report.json#/existing_evidence_findings",), "Correlate existing simulation findings without live capture", "evidence correlation"),
            ("compare_declared_dependencies", primary, ("recon-report.json#/target_ranking",), "Explain dependency-based priority without asserting vulnerability", "dependency rationale"),
            ("prepare_recon_summary", "digital_twin", ("recon-report.json#/actions",), "Prepare evidence-backed findings for human review", "review packet"),
        ]
        return {
            "schema": "aoa.plan-proposal/1.0",
            "mission_id": mission["mission_id"],
            "intents": [asdict(ToolIntent(index, *proposal, confidence=0.90)) for index, proposal in enumerate(proposals, 1)],
        }


class PolicyValidator:
    def __init__(self, mission: dict[str, Any]) -> None:
        self.mission = mission

    def validate(self, proposal: dict[str, Any]) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []
        required = {"schema", "mission_id", "intents"}
        if set(proposal) != required:
            errors.append({"path": "$", "code": "schema_keys", "detail": "proposal must contain exactly schema, mission_id and intents"})
        if proposal.get("schema") != "aoa.plan-proposal/1.0":
            errors.append({"path": "$.schema", "code": "schema_version"})
        if proposal.get("mission_id") != self.mission["mission_id"]:
            errors.append({"path": "$.mission_id", "code": "mission_mismatch"})
        intents = proposal.get("intents")
        if not isinstance(intents, list) or not 1 <= len(intents) <= 8:
            errors.append({"path": "$.intents", "code": "intent_count"})
            return errors
        for index, intent in enumerate(intents):
            prefix = f"$.intents[{index}]"
            required_intent = {"step", "intent", "target", "evidence_refs", "rationale", "expected_output", "confidence", "execution"}
            if not isinstance(intent, dict) or set(intent) != required_intent:
                errors.append({"path": prefix, "code": "intent_schema"})
                continue
            if intent["step"] != index + 1:
                errors.append({"path": prefix + ".step", "code": "step_order"})
            if intent["intent"] not in ALLOWED_INTENTS:
                errors.append({"path": prefix + ".intent", "code": "intent_not_allowed"})
            if intent["target"] not in self.mission["authorized_assets"]:
                errors.append({"path": prefix + ".target", "code": "target_out_of_scope"})
            if intent["execution"] != "not-executed":
                errors.append({"path": prefix + ".execution", "code": "execution_forbidden"})
            if not isinstance(intent["evidence_refs"], (list, tuple)) or not intent["evidence_refs"]:
                errors.append({"path": prefix + ".evidence_refs", "code": "evidence_required"})
            if not isinstance(intent["confidence"], (int, float)) or not 0 <= intent["confidence"] <= 1:
                errors.append({"path": prefix + ".confidence", "code": "confidence_range"})
            if PROHIBITED_TERMS.search(" ".join(str(intent.get(key, "")) for key in ("intent", "rationale", "expected_output"))):
                errors.append({"path": prefix, "code": "prohibited_capability"})
        return errors


def execute(root: Path, output: Path | None = None, provider: PlannerProvider | None = None) -> dict[str, Any]:
    mission = load(root / "config/mission.json")
    raw_evidence = load(root / "evidence/recon-report.json")
    evidence, quarantined = sanitize_evidence(raw_evidence)
    selected = provider or DeterministicPlanner()
    proposal = selected.propose({"mission": mission, "evidence": evidence})
    errors = PolicyValidator(mission).validate(proposal)
    accepted = not errors
    report = {
        "schema": "aoa.governed-plan/1.0",
        "version": "0.6.7",
        "mission_id": mission["mission_id"],
        "provider": selected.name,
        "llm_configured": provider is not None,
        "llm_used": provider is not None,
        "context_boundaries": {"mission": "trusted-instructions", "evidence": "untrusted-data"},
        "input_evidence_sha256": canonical_hash(raw_evidence),
        "quarantined_content": quarantined,
        "proposal": proposal if accepted else None,
        "rejected_proposal_sha256": None if accepted else canonical_hash(proposal),
        "policy_errors": errors,
        "accepted": accepted,
        "tool_calls_executed": 0,
        "network_connections_opened": 0,
        "physical_contact": False,
        "physical_writes": False,
        "approval": {"required": True, "status": "pending", "scope": "plan-only; no execution"},
        "next_gate": "human_review_of_plan_before_any_separate_virtual_action_authorization",
    }
    if output:
        output.mkdir(parents=True, exist_ok=True)
        (output / "governed-plan.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        manifest = {"version": "0.6.7", "report_sha256": canonical_hash(report), "llm_used": report["llm_used"],
                    "tool_calls_executed": 0, "physical_contact": False, "physical_writes": False}
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("evidence/demo"))
    args = parser.parse_args()
    print(json.dumps(execute(Path(__file__).resolve().parents[1], args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
