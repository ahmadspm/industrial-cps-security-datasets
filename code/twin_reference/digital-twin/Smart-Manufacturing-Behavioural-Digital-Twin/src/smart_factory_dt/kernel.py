from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Any

from .clock import ClockMode, TwinClock
from .observation import ObservationKind, TwinObservation
from .state_store import CanonicalTwinState


class RuntimeMode(StrEnum):
    SIMULATION = "simulation"
    REPLAY = "replay"
    PHYSICAL_OBSERVATION = "physical_observation"
    TEST = "test"


@dataclass
class StationState:
    station_id: str
    name: str
    state: str = "IDLE"
    active: bool = False
    sensors: dict[str, float | bool | str] = field(default_factory=dict)
    actuators: dict[str, float | bool | str] = field(default_factory=dict)
    transition_count: int = 0


@dataclass
class WorkpieceState:
    workpiece_id: str
    colour: str
    stage: str = "CREATED"
    route: list[str] = field(default_factory=list)


class FactoryTwin:
    """Single-writer canonical state with immutable external snapshots."""

    STATIONS = {
        "DSI": "Delivery and Input",
        "VGR": "Vacuum Gripper Robot",
        "HBW": "High-Bay Warehouse",
        "MPO": "Multi-Processing Station",
        "SLD": "Sorting Line with Colour Detection",
        "DSO": "Delivery and Output",
    }

    def __init__(
        self,
        runtime_mode: RuntimeMode = RuntimeMode.SIMULATION,
        *,
        clock: TwinClock | None = None,
    ) -> None:
        self.runtime_mode = runtime_mode
        if clock is None:
            clock_mode = ClockMode.REPLAY if runtime_mode == RuntimeMode.REPLAY else ClockMode.REALTIME
            clock = TwinClock(mode=clock_mode)
        self.clock = clock
        self.canonical = CanonicalTwinState(clock=self.clock)
        self.revision = 0
        self.stations = {
            station_id: StationState(station_id, name)
            for station_id, name in self.STATIONS.items()
        }
        self.workpieces: dict[str, WorkpieceState] = {}
        self.inventory: dict[str, str] = {}
        self.events: list[dict[str, Any]] = []

    @staticmethod
    def _entity_for_topic(topic: str, payload: dict[str, Any]) -> str:
        """Map an MQTT/OT topic to one stable canonical entity identifier."""
        if topic.startswith("f/i/state/"):
            return f"station:{topic.rsplit('/', 1)[-1].upper()}"
        if topic == "f/i/stock":
            return "inventory:HBW"
        if topic == "f/i/nfc/ds":
            workpiece_id = str(payload.get("id") or "unknown").strip().upper()
            return f"workpiece:{workpiece_id}"
        if topic in {"f/i/environment", "f/i/camera", "i/ptu/pos"}:
            return f"sensor:{topic.replace('/', ':').upper()}"
        if topic.startswith("fl/"):
            return f"channel:{topic.upper()}"
        return f"topic:{topic}"

    def observe_topic(
        self,
        topic: str,
        payload: dict[str, Any],
        *,
        kind: ObservationKind = ObservationKind.OBSERVED,
        source: str = "mqtt",
        timestamp: object | None = None,
        confidence: float = 1.0,
        evidence: dict[str, Any] | None = None,
        inference_rule: str | None = None,
    ) -> dict[str, bool]:
        """Apply one provenance-aware observation to the canonical state."""
        if not topic.strip():
            raise ValueError("topic must not be empty")
        entity_id = self._entity_for_topic(topic, payload)
        values = {key: deepcopy(value) for key, value in payload.items() if key not in {"ts", "timestamp"}}
        return self.canonical.apply(TwinObservation(
            entity_id=entity_id,
            values=values,
            source=source,
            kind=kind,
            timestamp=timestamp or payload.get("ts") or payload.get("timestamp"),
            confidence=confidence,
            evidence={"topic": topic, **(evidence or {})},
            inference_rule=inference_rule,
        ))

    def transition(self, station_id: str, state: str, *, active: bool) -> None:
        station = self.stations[station_id]
        station.state = state
        station.active = active
        station.transition_count += 1
        self.revision += 1
        self.events.append({
            "revision": self.revision,
            "station": station_id,
            "state": state,
            "active": active,
        })

    def run_cycle(self, workpiece_id: str, colour: str = "red") -> None:
        if workpiece_id in self.workpieces:
            raise ValueError(f"duplicate workpiece: {workpiece_id}")
        workpiece = WorkpieceState(workpiece_id, colour)
        self.workpieces[workpiece_id] = workpiece
        sequence = [
            ("DSI", "NFC_DETECTED"),
            ("VGR", "TRANSPORT_TO_HBW"),
            ("HBW", "STORE_WORKPIECE"),
            ("VGR", "TRANSPORT_TO_MPO"),
            ("MPO", "PROCESS_WORKPIECE"),
            ("VGR", "TRANSPORT_TO_SLD"),
            ("SLD", "DETECT_AND_SORT"),
            ("VGR", "TRANSPORT_TO_DSO"),
            ("DSO", "ORDER_COMPLETE"),
        ]
        for station_id, state in sequence:
            self.transition(station_id, state, active=True)
            workpiece.stage = state
            workpiece.route.append(station_id)
            self.transition(station_id, "IDLE", active=False)
        workpiece.stage = "COMPLETED"

    def snapshot(self) -> dict[str, Any]:
        captured_at = datetime.now(timezone.utc).isoformat()
        state = {
            "runtime_mode": self.runtime_mode,
            "revision": self.revision,
            "stations": {key: asdict(value) for key, value in self.stations.items()},
            "workpieces": {key: asdict(value) for key, value in self.workpieces.items()},
            "inventory": self.inventory,
            "events": self.events,
            "canonical_state": self.canonical.snapshot(),
        }
        canonical = json.dumps(state, sort_keys=True, separators=(",", ":"), default=str)
        return deepcopy({
            "schema": "aoa.dt.snapshot/1.0",
            "captured_at": captured_at,
            "read_only": True,
            "fingerprint_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
            "factory": state,
        })

