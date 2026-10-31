from __future__ import annotations

from typing import Any

from .models import MissionContract, Observation


def planner_system_prompt() -> str:
    return """You are the planning component of an Autonomous Offensive Agent operating only
inside an authorised synthetic smart-factory Digital Twin. Your present phase is
reconnaissance. Propose exactly one read-only action from permitted_tools, or mark the
mission complete. Never invent tool results, enlarge scope, contact the physical factory,
request credentials, exploit a service, create persistence, or cause denial of service.
Base each hypothesis on supplied evidence. A deterministic policy gate will independently
validate every proposal. Return only the requested structured object."""


def build_planner_input(
    mission: MissionContract,
    observations: list[Observation],
) -> dict[str, Any]:
    return {
        "mission": mission.model_dump(mode="json"),
        "digital_twin_context": {
            "testbed": "fischertechnik Training Factory Industry 4.0",
            "candidate_layers": ["industrial_dmz", "ot_supervisory", "ot_control"],
            "candidate_protocols": ["MQTT", "OPC UA", "S7comm"],
            "knowledge_status": "declared context; not a discovery result",
        },
        "observations": [item.model_dump(mode="json") for item in observations],
        "decision_rules": {
            "one_action_only": True,
            "read_only": True,
            "stop_when_inventory_is_evidenced": True,
            "unknown_is_not_fact": True,
        },
    }
