from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ObservationKind(str, Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    SIMULATED = "simulated"
    REPLAYED = "replayed"


class MissionContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mission_id: str
    objective: str
    phase: Literal["reconnaissance"] = "reconnaissance"
    engagement_mode: Literal["grey-box"] = "grey-box"
    authorised_cidr: str
    entry_point: str
    permitted_tools: list[str]
    prohibited_actions: list[str]
    max_actions: int = Field(default=8, ge=1, le=20)
    physical_factory_access: Literal[False] = False

    @field_validator("objective")
    @classmethod
    def objective_is_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("objective cannot be empty")
        return value.strip()


class ActionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str
    objective: str
    hypothesis: str
    tool: str
    arguments: dict[str, Any]
    expected_information: str
    confidence: float = Field(ge=0.0, le=1.0)


class PolicyDecision(BaseModel):
    allowed: bool
    reason: str
    requires_human_approval: bool = False


class Observation(BaseModel):
    sequence: int
    action_id: str
    tool: str
    arguments: dict[str, Any]
    source: str
    kind: ObservationKind
    observed_at: str = Field(default_factory=utc_now)
    confidence: float = Field(ge=0.0, le=1.0)
    data: dict[str, Any]
    evidence: dict[str, Any]


class EvaluationResult(BaseModel):
    host_recall: float
    service_precision: float
    evidence_coverage: float
    scope_violations: int
    completed: bool
