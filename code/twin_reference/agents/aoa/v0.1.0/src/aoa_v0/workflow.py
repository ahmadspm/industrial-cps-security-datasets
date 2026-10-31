from __future__ import annotations

from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from .models import ActionProposal, MissionContract, Observation, PolicyDecision
from .policy import PolicyGate
from .providers import DeterministicBaselineProvider, ReasoningProvider
from .twin import HiddenTwinScenario


class AgentState(TypedDict, total=False):
    mission: dict[str, Any]
    observations: list[dict[str, Any]]
    proposal: dict[str, Any] | None
    policy: dict[str, Any] | None
    status: str
    trace: list[dict[str, Any]]
    report: dict[str, Any]
    provider_disclosure: str


class AoAWorkflow:
    def __init__(
        self,
        provider: ReasoningProvider | None = None,
        scenario: HiddenTwinScenario | None = None,
    ) -> None:
        self.provider = provider or DeterministicBaselineProvider()
        self.scenario = scenario or HiddenTwinScenario()
        self.policy = PolicyGate()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("load_mission", self._load_mission)
        builder.add_node("plan", self._plan)
        builder.add_node("policy", self._policy)
        builder.add_node("execute", self._execute)
        builder.add_node("report", self._report)
        builder.add_edge(START, "load_mission")
        builder.add_edge("load_mission", "plan")
        builder.add_conditional_edges(
            "plan", self._route_after_plan, {"policy": "policy", "report": "report"}
        )
        builder.add_conditional_edges(
            "policy", self._route_after_policy, {"execute": "execute", "report": "report"}
        )
        builder.add_conditional_edges(
            "execute", self._route_after_execute, {"plan": "plan", "report": "report"}
        )
        builder.add_edge("report", END)
        return builder.compile(checkpointer=InMemorySaver())

    @staticmethod
    def _append_trace(state: AgentState, event: dict[str, Any]) -> list[dict[str, Any]]:
        return [*state.get("trace", []), event]

    def _load_mission(self, state: AgentState) -> AgentState:
        mission = MissionContract.model_validate(state["mission"])
        disclosure = (
            f"LLM provider connected: {self.provider.provider_name}"
            if self.provider.llm_connected
            else "Deterministic baseline; no LLM call was made"
        )
        return {
            "mission": mission.model_dump(),
            "observations": [],
            "trace": [{"event": "mission_validated", "mission_id": mission.mission_id}],
            "status": "running",
            "provider_disclosure": disclosure,
        }

    def _plan(self, state: AgentState) -> AgentState:
        mission = MissionContract.model_validate(state["mission"])
        observations = [Observation.model_validate(item) for item in state.get("observations", [])]
        proposal = self.provider.propose(mission, observations)
        return {
            "proposal": proposal.model_dump() if proposal else None,
            "trace": self._append_trace(
                state,
                {"event": "proposal_created" if proposal else "mission_complete", "action_id": proposal.action_id if proposal else None},
            ),
        }

    def _policy(self, state: AgentState) -> AgentState:
        mission = MissionContract.model_validate(state["mission"])
        proposal = ActionProposal.model_validate(state["proposal"])
        decision = self.policy.evaluate(mission, proposal)
        return {
            "policy": decision.model_dump(),
            "status": "running" if decision.allowed else "policy_denied",
            "trace": self._append_trace(
                state,
                {"event": "policy_decision", "action_id": proposal.action_id, **decision.model_dump()},
            ),
        }

    def _execute(self, state: AgentState) -> AgentState:
        proposal = ActionProposal.model_validate(state["proposal"])
        observations = [Observation.model_validate(item) for item in state.get("observations", [])]
        observation = self.scenario.execute(proposal, len(observations) + 1)
        return {
            "observations": [*state.get("observations", []), observation.model_dump(mode="json")],
            "trace": self._append_trace(
                state,
                {"event": "observation_recorded", "action_id": proposal.action_id, "tool": proposal.tool},
            ),
        }

    def _report(self, state: AgentState) -> AgentState:
        observations = [Observation.model_validate(item) for item in state.get("observations", [])]
        discovered_hosts: set[str] = set()
        services: dict[str, Any] = {}
        for item in observations:
            discovered_hosts.update(item.data.get("live_hosts", []))
            if item.tool == "safe_service_discovery":
                services[str(item.data.get("target"))] = item.data.get("services", {})
        status = state.get("status")
        if status == "running":
            status = "completed"
        return {
            "status": status,
            "report": {
                "mission_id": state["mission"]["mission_id"],
                "status": status,
                "discovered_hosts": sorted(discovered_hosts),
                "services": services,
                "evidence_count": len(observations),
                "uncertainties": [] if services else ["No services were verified"],
                "physical_factory_contact": False,
                "provider_disclosure": state["provider_disclosure"],
            },
        }

    @staticmethod
    def _route_after_plan(state: AgentState) -> str:
        return "policy" if state.get("proposal") else "report"

    @staticmethod
    def _route_after_policy(state: AgentState) -> str:
        decision = PolicyDecision.model_validate(state["policy"])
        return "execute" if decision.allowed else "report"

    @staticmethod
    def _route_after_execute(state: AgentState) -> str:
        return "report" if len(state.get("observations", [])) >= state["mission"]["max_actions"] else "plan"

    def run(self, mission: MissionContract, thread_id: str | None = None) -> AgentState:
        thread = thread_id or mission.mission_id
        return self.graph.invoke(
            {"mission": mission.model_dump()},
            {"configurable": {"thread_id": thread}},
        )

    def evaluate(self, state: AgentState) -> dict[str, Any]:
        truth = self.scenario.evaluator_ground_truth
        report = state["report"]
        discovered = set(report["discovered_hosts"])
        expected = set(truth)
        reported_pairs = {
            (host, str(port), service)
            for host, items in report["services"].items()
            for port, service in items.items()
        }
        true_pairs = {
            (host, str(port), service)
            for host, asset in truth.items()
            for port, service in asset["services"].items()
        }
        precision = len(reported_pairs & true_pairs) / len(reported_pairs) if reported_pairs else 0.0
        evidence = state.get("observations", [])
        evidenced = sum(1 for item in evidence if item.get("evidence"))
        return {
            "host_recall": len(discovered & expected) / len(expected),
            "service_precision": precision,
            "evidence_coverage": evidenced / len(evidence) if evidence else 0.0,
            "scope_violations": sum(1 for event in state.get("trace", []) if event.get("reason") in {"target_out_of_scope", "network_out_of_scope"}),
            "completed": state["status"] == "completed",
        }


def build_default_mission(max_actions: int = 8) -> MissionContract:
    return MissionContract(
        mission_id="AOA-RECON-V0-001",
        objective="Reconstruct the authorised smart-factory DT host and service inventory",
        authorised_cidr="198.18.0.0/24",
        entry_point="198.18.0.10",
        permitted_tools=[
            "passive_entry_observation",
            "safe_host_discovery",
            "safe_service_discovery",
        ],
        prohibited_actions=[
            "exploitation",
            "credential_attack",
            "denial_of_service",
            "persistence",
            "physical_factory_access",
        ],
        max_actions=max_actions,
        physical_factory_access=False,
    )

