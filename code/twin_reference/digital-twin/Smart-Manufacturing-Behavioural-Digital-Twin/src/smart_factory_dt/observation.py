"""Provenance-aware observations used to update canonical twin state."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Optional

from smart_factory_dt.clock import TwinClock, parse_timestamp


class ObservationKind(str, Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    SIMULATED = "simulated"
    REPLAYED = "replayed"


@dataclass(frozen=True)
class TwinObservation:
    entity_id: str
    values: Mapping[str, Any]
    source: str
    kind: ObservationKind = ObservationKind.OBSERVED
    timestamp: Optional[object] = None
    confidence: float = 1.0
    evidence: Mapping[str, Any] = field(default_factory=dict)
    inference_rule: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.entity_id.strip():
            raise ValueError("entity_id must not be empty")
        if not self.source.strip():
            raise ValueError("observation source must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.kind == ObservationKind.INFERRED and not self.inference_rule:
            raise ValueError("inferred observations require an inference_rule")

    def timestamp_iso(self, clock: TwinClock) -> str:
        dt = clock.now() if self.timestamp is None else parse_timestamp(self.timestamp)
        return dt.isoformat().replace("+00:00", "Z")

    def to_dict(self, clock: TwinClock) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "values": dict(self.values),
            "source": self.source,
            "kind": self.kind.value,
            "timestamp": self.timestamp_iso(clock),
            "confidence": self.confidence,
            "evidence": dict(self.evidence),
            "inference_rule": self.inference_rule,
        }


