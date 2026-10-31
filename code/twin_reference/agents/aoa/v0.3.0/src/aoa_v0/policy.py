from __future__ import annotations

from ipaddress import ip_address, ip_network

from .models import ActionProposal, MissionContract, PolicyDecision


class PolicyGate:
    """Deterministic rules that neither the LLM nor a future ASBIO may override."""

    def evaluate(self, mission: MissionContract, proposal: ActionProposal) -> PolicyDecision:
        if proposal.tool not in mission.permitted_tools:
            return PolicyDecision(allowed=False, reason="tool_not_permitted")
        if mission.physical_factory_access:
            return PolicyDecision(allowed=False, reason="physical_factory_boundary_invalid")

        target = proposal.arguments.get("target")
        cidr = proposal.arguments.get("cidr")
        network = ip_network(mission.authorised_cidr, strict=False)
        if target is not None and ip_address(str(target)) not in network:
            return PolicyDecision(allowed=False, reason="target_out_of_scope")
        if cidr is not None and ip_network(str(cidr), strict=False) != network:
            return PolicyDecision(allowed=False, reason="network_out_of_scope")
        return PolicyDecision(allowed=True, reason="authorised_dt_read_only_action")

