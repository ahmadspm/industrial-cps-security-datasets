from __future__ import annotations

import json
import os
from typing import Any, Callable, Protocol

from .models import ActionProposal, MissionContract, Observation
from .prompting import build_planner_input, planner_system_prompt


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


class CallableLLMProvider:
    """Inject a governed LLM callable without coupling the workflow to a vendor SDK."""

    provider_name = "injected-structured-llm"
    llm_connected = True

    def __init__(self, invoke: Callable[[str, dict[str, Any]], dict[str, Any] | None]):
        self._invoke = invoke

    def propose(
        self,
        mission: MissionContract,
        observations: list[Observation],
    ) -> ActionProposal | None:
        result = self._invoke(planner_system_prompt(), build_planner_input(mission, observations))
        return ActionProposal.model_validate(result) if result is not None else None


class OpenAIResponsesProvider:
    """Structured OpenAI planner. Tool execution remains outside the model boundary."""

    llm_connected = True

    def __init__(self, model: str = "gpt-5-mini", client: Any | None = None) -> None:
        if client is None:
            from openai import OpenAI

            if not os.getenv("OPENAI_API_KEY"):
                raise RuntimeError("OPENAI_API_KEY is not configured")
            client = OpenAI()
        self.client = client
        self.model = model
        self.provider_name = f"openai-responses:{model}"

    def propose(
        self,
        mission: MissionContract,
        observations: list[Observation],
    ) -> ActionProposal | None:
        response = self.client.responses.create(
            model=self.model,
            instructions=planner_system_prompt(),
            input=json.dumps(build_planner_input(mission, observations)),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "aoa_action_or_completion",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "complete": {"type": "boolean"},
                            "proposal": {
                                "anyOf": [
                                    {"type": "null"},
                                    ActionProposal.model_json_schema(),
                                ]
                            },
                        },
                        "required": ["complete", "proposal"],
                    },
                }
            },
        )
        payload = json.loads(response.output_text)
        if payload["complete"]:
            return None
        return ActionProposal.model_validate(payload["proposal"])


def provider_from_environment() -> ReasoningProvider:
    """Select a real LLM only when explicitly enabled; otherwise disclose fallback."""

    if os.getenv("AOA_LLM_PROVIDER", "").lower() == "openai":
        return OpenAIResponsesProvider(model=os.getenv("AOA_OPENAI_MODEL", "gpt-5-mini"))
    return DeterministicBaselineProvider()
