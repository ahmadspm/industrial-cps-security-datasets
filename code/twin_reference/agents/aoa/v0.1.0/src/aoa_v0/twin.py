from __future__ import annotations

from copy import deepcopy
from typing import Any

from .models import ActionProposal, Observation, ObservationKind


class HiddenTwinScenario:
    """Evaluator-owned scenario. Its complete inventory is never placed in agent state."""

    def __init__(self) -> None:
        self._assets: dict[str, dict[str, Any]] = {
            "198.18.0.10": {
                "asset_id": "IOT_GATEWAY",
                "role": "IT/OT gateway",
                "zone": "industrial_dmz",
                "services": {22: "ssh", 1883: "mqtt"},
            },
            "198.18.0.20": {
                "asset_id": "MQTT_BROKER",
                "role": "message broker",
                "zone": "ot_supervisory",
                "services": {1883: "mqtt"},
            },
            "198.18.0.30": {
                "asset_id": "OPCUA_SERVER",
                "role": "industrial data server",
                "zone": "ot_control",
                "services": {4840: "opcua"},
            },
            "198.18.0.40": {
                "asset_id": "PLC_S7_1500",
                "role": "factory controller",
                "zone": "ot_control",
                "services": {102: "s7comm"},
            },
        }

    @property
    def evaluator_ground_truth(self) -> dict[str, dict[str, Any]]:
        return deepcopy(self._assets)

    def execute(self, proposal: ActionProposal, sequence: int) -> Observation:
        if proposal.tool == "passive_entry_observation":
            target = str(proposal.arguments["target"])
            asset = self._assets.get(target, {})
            data = {
                "target": target,
                "observed_role": asset.get("role", "unknown"),
                "observed_zone": asset.get("zone", "unknown"),
            }
        elif proposal.tool == "safe_host_discovery":
            data = {"live_hosts": sorted(self._assets)}
        elif proposal.tool == "safe_service_discovery":
            target = str(proposal.arguments["target"])
            asset = self._assets.get(target, {})
            data = {
                "target": target,
                "asset_id": asset.get("asset_id", "unknown"),
                "role": asset.get("role", "unknown"),
                "zone": asset.get("zone", "unknown"),
                "services": asset.get("services", {}),
            }
        else:
            raise ValueError("tool is not implemented by the Digital Twin sandbox")

        return Observation(
            sequence=sequence,
            action_id=proposal.action_id,
            tool=proposal.tool,
            arguments=proposal.arguments,
            source="synthetic_smart_factory_dt",
            kind=ObservationKind.SIMULATED,
            confidence=1.0,
            data=data,
            evidence={
                "physical_contact": False,
                "state_changed": False,
                "scenario_channel": "authorised_dt_only",
            },
        )

