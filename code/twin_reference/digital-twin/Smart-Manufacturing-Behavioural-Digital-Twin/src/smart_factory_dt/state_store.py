"""Thread-safe canonical state and audit history for the Digital Twin."""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from typing import Any, Deque, Dict, Optional

from smart_factory_dt.clock import TwinClock, parse_timestamp
from smart_factory_dt.observation import TwinObservation


@dataclass(frozen=True)
class StateRecord:
    value: Any
    timestamp: str
    source: str
    kind: str
    confidence: float
    evidence: Dict[str, Any]
    inference_rule: Optional[str]
    revision: int

    def to_dict(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)


class CanonicalTwinState:
    """Authoritative, provenance-aware state projection.

    A record is stored per entity and field. Stale observations are retained in
    the audit history but cannot overwrite newer canonical values.
    """

    def __init__(self, clock: Optional[TwinClock] = None, history_limit: int = 5000) -> None:
        if history_limit < 1:
            raise ValueError("history_limit must be at least 1")
        self.clock = clock or TwinClock()
        self._entities: Dict[str, Dict[str, StateRecord]] = {}
        self._history: Deque[Dict[str, Any]] = deque(maxlen=history_limit)
        self._revision = 0
        self._lock = RLock()

    @property
    def revision(self) -> int:
        return self._revision

    def apply(self, observation: TwinObservation) -> Dict[str, bool]:
        item = observation.to_dict(self.clock)
        timestamp = item["timestamp"]
        results: Dict[str, bool] = {}
        with self._lock:
            entity = self._entities.setdefault(observation.entity_id, {})
            for field_name, value in observation.values.items():
                current = entity.get(field_name)
                accepted = current is None or parse_timestamp(timestamp) >= parse_timestamp(current.timestamp)
                if accepted:
                    self._revision += 1
                    entity[field_name] = StateRecord(
                        value=deepcopy(value), timestamp=timestamp, source=observation.source,
                        kind=observation.kind.value, confidence=observation.confidence,
                        evidence=dict(observation.evidence), inference_rule=observation.inference_rule,
                        revision=self._revision,
                    )
                results[field_name] = accepted
            self._history.append({**item, "accepted": results.copy(), "revision": self._revision})
        return results

    def entity(self, entity_id: str, include_metadata: bool = True) -> Dict[str, Any]:
        with self._lock:
            records = self._entities.get(entity_id, {})
            if include_metadata:
                return {key: value.to_dict() for key, value in records.items()}
            return {key: deepcopy(value.value) for key, value in records.items()}

    def snapshot(self, include_metadata: bool = True) -> Dict[str, Any]:
        with self._lock:
            return {
                "revision": self._revision,
                "captured_at": self.clock.now_iso(),
                "entities": {
                    entity_id: self.entity(entity_id, include_metadata)
                    for entity_id in self._entities
                },
            }

    def history(self, limit: Optional[int] = None) -> list[Dict[str, Any]]:
        with self._lock:
            items = list(self._history)
            return deepcopy(items[-limit:] if limit is not None else items)


