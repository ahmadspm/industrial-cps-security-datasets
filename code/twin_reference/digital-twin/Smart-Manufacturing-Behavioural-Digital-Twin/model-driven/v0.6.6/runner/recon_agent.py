"""Governed, read-only AoA reconnaissance over virtual Digital Twin data."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


TECHNIQUES = {
    "T0846": "Remote System Discovery",
    "T0846.001": "Port Scan",
    "T0888": "Remote System Information Discovery",
    "T0840": "Network Connection Enumeration",
    "T0861": "Point & Tag Identification",
    "T0801": "Monitor Process State",
}

ALLOWED_ACTIONS = {
    "query_virtual_asset_catalogue", "inspect_declared_service_metadata",
    "inspect_topic_and_node_metadata", "correlate_existing_evidence",
    "prioritize_virtual_targets", "generate_recon_report",
}


@dataclass(frozen=True)
class Authorization:
    mission_id: str
    authorized_assets: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    physical_access: bool = False
    active_scanning: bool = False
    writes: bool = False

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Authorization":
        data = dict(value)
        data["authorized_assets"] = tuple(data.get("authorized_assets", ()))
        data["allowed_actions"] = tuple(data.get("allowed_actions", ()))
        return cls(**data)


@dataclass(frozen=True)
class AgentAction:
    step: int
    action: str
    target: str
    status: str
    evidence_source: str
    technique: str | None
    rationale: str


class GovernanceError(PermissionError):
    pass


class GovernedReconAgent:
    def __init__(self, assets: dict[str, Any], authorization: Authorization) -> None:
        self.assets = {item["id"]: item for item in assets["assets"]}
        self.authorization = authorization
        self.actions: list[AgentAction] = []
        self.denials: list[dict[str, Any]] = []

    def authorize(self, action: str, target: str) -> None:
        asset = self.assets.get(target)
        reasons = []
        if action not in ALLOWED_ACTIONS or action not in self.authorization.allowed_actions:
            reasons.append("action_not_authorized")
        if target not in self.authorization.authorized_assets:
            reasons.append("asset_out_of_scope")
        if asset is None:
            reasons.append("asset_unknown")
        elif asset.get("physical"):
            reasons.append("physical_asset_excluded")
        if self.authorization.physical_access or self.authorization.active_scanning or self.authorization.writes:
            reasons.append("unsafe_authorization_flags")
        if reasons:
            denial = {"action": action, "target": target, "reasons": reasons}
            self.denials.append(denial)
            raise GovernanceError(json.dumps(denial, sort_keys=True))

    def act(self, action: str, target: str, source: str, technique: str | None, rationale: str) -> None:
        self.authorize(action, target)
        self.actions.append(AgentAction(len(self.actions) + 1, action, target, "simulated-read-only", source, technique, rationale))

    def run(self, evidence: dict[str, Any]) -> dict[str, Any]:
        candidates = []
        for asset_id in self.authorization.authorized_assets:
            asset = self.assets.get(asset_id)
            if not asset or asset.get("physical"):
                continue
            self.act("query_virtual_asset_catalogue", asset_id, "virtual-assets.json", "T0846", "enumerate only pre-declared virtual assets")
            self.act("inspect_declared_service_metadata", asset_id, "virtual-assets.json", "T0888", "read declared role, service and zone metadata")
            risk = 0
            reasons = []
            services = asset.get("services", [])
            if services:
                risk += 2
                reasons.append("declared_network_service")
            if asset.get("zone") in {"control", "integration", "sensor_integration"}:
                risk += 2
                reasons.append("ot_or_integration_zone")
            if asset_id in {"mqtt_broker", "iot_gateway"}:
                risk += 2
                reasons.append("communication_dependency")
            candidates.append({"asset_id": asset_id, "score": risk, "reasons": reasons,
                               "services": services, "source": "declared_metadata_not_scan"})

        evidence_target = "digital_twin"
        if evidence_target in self.authorization.authorized_assets:
            self.act("correlate_existing_evidence", evidence_target, "experiment-matrix.json", "T0840", "use recorded communication relationships without live capture")
            self.act("inspect_topic_and_node_metadata", evidence_target, "semantic contracts", "T0861", "read approved topic and logical-node catalogue")
        candidates.sort(key=lambda item: (-item["score"], item["asset_id"]))
        if candidates:
            self.act("prioritize_virtual_targets", candidates[0]["asset_id"], "derived ranking", "T0888", "rank virtual targets using declared dependencies")
        self.act("generate_recon_report", "digital_twin", "agent working memory", None, "produce bounded evidence and stop before active testing")

        evidence_findings = []
        for experiment in evidence.get("experiments", []):
            if experiment.get("degraded"):
                evidence_findings.append({"profile": experiment["profile"], "findings": experiment.get("findings", []),
                                          "interpretation": "existing simulated evidence; not a discovered vulnerability"})
        return {
            "schema": "aoa.governed-recon-report/1.0",
            "version": "0.6.6",
            "mission_id": self.authorization.mission_id,
            "mode": "deterministic-read-only",
            "llm_used": False,
            "active_scanning": False,
            "commands_executed": 0,
            "network_connections_opened": 0,
            "physical_contact": False,
            "physical_writes": False,
            "technique_catalogue": TECHNIQUES,
            "actions": [asdict(item) for item in self.actions],
            "denials": self.denials,
            "target_ranking": candidates,
            "existing_evidence_findings": evidence_findings,
            "next_gate": "human_review_before_any_active_virtual-service testing",
            "completed": True,
        }


def load(path: Path) -> dict[str, Any]: return json.loads(path.read_text())


def execute(root: Path, output: Path | None = None) -> dict[str, Any]:
    agent = GovernedReconAgent(load(root / "config/virtual-assets.json"), Authorization.from_dict(load(root / "scenarios/authorized-recon.json")))
    report = agent.run(load(root / "evidence/impairment-summary.json"))
    if output:
        output.mkdir(parents=True, exist_ok=True)
        text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        manifest = {"version":"0.6.6", "report_sha256":hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                    "llm_used":False,"active_scanning":False,"physical_contact":False,"physical_writes":False}
        (output / "recon-report.json").write_text(text)
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("evidence/demo"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    print(json.dumps(execute(root, args.output), indent=2, sort_keys=True))


if __name__ == "__main__": main()
