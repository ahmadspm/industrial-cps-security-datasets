from __future__ import annotations

from typing import Protocol

from .models import ActionProposal, MissionContract, Observation


class ReasoningProvider(Protocol):
    """Provider-neutral boundary for an LLM-backed AoA planner."""

    provider_name: str
    llm_connected: bool

    def propose(
        self,
        mission: MissionContract,
        observations: list[Observation],
    ) -> ActionProposal | None: ...


class DeterministicBaselineProvider:
    """Transparent baseline used to test the harness without claiming LLM use."""

    provider_name = "deterministic-baseline"
    llm_connected = False

    def propose(
        self,
        mission: MissionContract,
        observations: list[Observation],
    ) -> ActionProposal | None:
        completed_tools = [item.tool for item in observations]
        discovered_hosts: list[str] = []
        enumerated_hosts: set[str] = set()
        for item in observations:
            if item.tool == "safe_host_discovery":
                discovered_hosts = list(item.data.get("live_hosts", []))
            if item.tool == "safe_service_discovery":
                enumerated_hosts.add(str(item.arguments.get("target")))

        n = len(observations) + 1
        if "passive_entry_observation" not in completed_tools:
            return ActionProposal(
                action_id=f"A-{n:03d}",
                objective="Establish the authorised starting context",
                hypothesis="The supplied entry point is a simulated IT/OT gateway",
                tool="passive_entry_observation",
                arguments={"target": mission.entry_point},
                expected_information="Entry-point identity and zone",
                confidence=0.75,
            )
        if "safe_host_discovery" not in completed_tools:
            return ActionProposal(
                action_id=f"A-{n:03d}",
                objective="Identify live Digital Twin hosts",
                hypothesis="Multiple IT and OT assets are reachable inside the authorised range",
                tool="safe_host_discovery",
                arguments={"cidr": mission.authorised_cidr},
                expected_information="Synthetic live-host inventory",
                confidence=0.72,
            )
        remaining = [host for host in discovered_hosts if host not in enumerated_hosts]
        if remaining:
            return ActionProposal(
                action_id=f"A-{n:03d}",
                objective="Identify services without modifying the target",
                hypothesis="The host exposes a service relevant to the IT/OT data path",
                tool="safe_service_discovery",
                arguments={"target": remaining[0]},
                expected_information="Declared synthetic ports and service identities",
                confidence=0.70,
            )
        return None

