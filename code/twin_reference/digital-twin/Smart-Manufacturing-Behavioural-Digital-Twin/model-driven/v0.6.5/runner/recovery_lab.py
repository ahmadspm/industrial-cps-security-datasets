"""Cross-layer fault propagation and recovery model for the factory twin."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


CYCLE = (
    ("dps", "workpiece_detected"), ("vgr", "pick_input"),
    ("hbw", "store_workpiece"), ("vgr", "retrieve_workpiece"),
    ("mpo", "process_workpiece"), ("vgr", "transport_to_sld"),
    ("sld", "sort_by_colour"), ("vgr", "deliver_output"),
    ("dps", "cycle_complete"),
)


@dataclass(frozen=True)
class RecoveryProfile:
    name: str
    fault_sequence: int | None = None
    fault_type: str | None = None
    recovery_policy: str = "none"
    fault_duration_ms: float = 0.0
    retry_budget: int = 0
    recovery_attempt: int = 1

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RecoveryProfile":
        return cls(**value)


@dataclass(frozen=True)
class RecoveryEvent:
    sequence: int
    logical_ms: float
    layer: str
    action: str
    process_state: str
    workpiece_state: str
    station: str | None
    cycle_sequence: int | None
    detail: str


class RecoveryRuntime:
    def __init__(self, profile: RecoveryProfile, workpiece_id: str = "WP-001") -> None:
        self.profile = profile
        self.workpiece_id = workpiece_id
        self.logical_ms = 0.0
        self.events: list[RecoveryEvent] = []
        self.process_state = "RUNNING"
        self.workpiece_state = "RECEIVED"
        self.canonical: dict[str, dict[str, Any]] = {}
        self.revision = 0
        self.resources = {"VGR": None, "HBW": None, "MPO": None, "SLD": None}
        self.findings: list[dict[str, Any]] = []
        self.hold_count = 0
        self.retry_count = 0
        self.recovery_count = 0
        self.delivered_transitions = 0

    def record(self, layer: str, action: str, detail: str, station: str | None = None,
               cycle_sequence: int | None = None, advance_ms: float = 1.0) -> None:
        self.logical_ms += advance_ms
        self.events.append(RecoveryEvent(len(self.events) + 1, self.logical_ms, layer, action,
                                         self.process_state, self.workpiece_state, station,
                                         cycle_sequence, detail))

    @staticmethod
    def resource_for(station: str) -> str | None:
        return station.upper() if station.upper() in {"VGR", "HBW", "MPO", "SLD"} else None

    def reserve(self, station: str) -> None:
        resource = self.resource_for(station)
        if resource:
            owner = self.resources[resource]
            if owner not in (None, self.workpiece_id):
                raise RuntimeError(f"resource conflict: {resource}")
            self.resources[resource] = self.workpiece_id
            self.record("resource", "RESERVE", resource, station)

    def release(self, station: str) -> None:
        resource = self.resource_for(station)
        if resource and self.resources[resource] == self.workpiece_id:
            self.resources[resource] = None
            self.record("resource", "RELEASE", resource, station)

    def commit(self, station: str, state: str, cycle_sequence: int) -> None:
        self.revision += 1
        self.canonical[station] = {"state": state, "cycle_sequence": cycle_sequence, "revision": self.revision}
        self.workpiece_state = state.upper()
        if state == "cycle_complete":
            self.delivered_transitions += 1
            self.workpiece_state = "DELIVERED"
        self.record("digital_twin", "COMMIT", state, station, cycle_sequence)

    def propagate_fault(self, station: str, cycle_sequence: int) -> bool:
        fault = self.profile.fault_type or "unknown"
        self.record("communication", "FAULT_INJECTED", fault, station, cycle_sequence)
        finding = "OBSERVATION_STALE" if fault == "opcua_stale" else "COMMUNICATION_TIMEOUT"
        self.findings.append({"code": finding, "station": station, "cycle_sequence": cycle_sequence})
        self.record("digital_twin", "DETECT", finding, station, cycle_sequence)
        self.process_state = "HOLDING"
        self.workpiece_state = "HELD_COMMUNICATION"
        self.hold_count += 1
        self.record("process", "ENTER_HOLD", "prevent next production transition", station, cycle_sequence)
        self.record("resource", "HOLD_RESERVATION", self.resource_for(station) or "none", station, cycle_sequence)
        self.logical_ms += self.profile.fault_duration_ms

        if self.profile.recovery_policy == "none":
            self.process_state = "FAIL_SAFE"
            self.record("safety", "FAIL_SAFE", "recovery disabled", station, cycle_sequence)
            return False

        self.process_state = "RECOVERING"
        self.record("recovery", "START", self.profile.recovery_policy, station, cycle_sequence)
        allowed_attempts = self.profile.retry_budget + 1
        for attempt in range(1, allowed_attempts + 1):
            self.retry_count += 1
            self.record("recovery", "ATTEMPT", f"attempt={attempt}", station, cycle_sequence)
            if attempt >= self.profile.recovery_attempt:
                action = "REPLAY_MISSING" if self.profile.recovery_policy == "retry_replay" else "READ_RETAINED_SNAPSHOT"
                self.record("communication", action, "reconcile sequence and state", station, cycle_sequence)
                self.process_state = "RESUMING"
                self.recovery_count += 1
                self.record("process", "RECONCILE", "identity, sequence and reservation valid", station, cycle_sequence)
                self.process_state = "RUNNING"
                self.record("process", "RESUME", "controlled continuation", station, cycle_sequence)
                return True
        self.process_state = "FAIL_SAFE"
        self.findings.append({"code": "RECOVERY_EXHAUSTED", "station": station, "cycle_sequence": cycle_sequence})
        self.record("safety", "FAIL_SAFE", "retry budget exhausted", station, cycle_sequence)
        return False

    def run(self) -> dict[str, Any]:
        self.record("process", "START", self.profile.name)
        for number, (station, state) in enumerate(CYCLE, 1):
            self.reserve(station)
            self.record("plc", "STATION_STEP", state, station, number, advance_ms=20.0)
            if number == self.profile.fault_sequence:
                if not self.propagate_fault(station, number):
                    break
            self.commit(station, state, number)
            self.release(station)
        completed = self.workpiece_state == "DELIVERED" and self.delivered_transitions == 1
        if completed:
            self.process_state = "COMPLETED"
            self.record("process", "COMPLETE", "exactly-once delivery")
        elif self.process_state != "FAIL_SAFE":
            self.process_state = "INCOMPLETE"
        return self.report(completed)

    def report(self, completed: bool) -> dict[str, Any]:
        held_resources = sorted(key for key, owner in self.resources.items() if owner is not None)
        return {
            "schema": "smart-factory-dt.recovery-report/1.0",
            "model_version": "0.6.5",
            "profile": asdict(self.profile),
            "workpiece_id": self.workpiece_id,
            "completed": completed,
            "process_state": self.process_state,
            "workpiece_state": self.workpiece_state,
            "canonical_revision": self.revision,
            "delivered_transitions": self.delivered_transitions,
            "hold_count": self.hold_count,
            "retry_count": self.retry_count,
            "recovery_count": self.recovery_count,
            "recovery_time_ms": self.profile.fault_duration_ms if self.recovery_count else None,
            "held_resources": held_resources,
            "final_states": {key: value["state"] for key, value in self.canonical.items()},
            "findings": self.findings,
            "event_count": len(self.events),
            "physical_contact": False,
            "physical_writes": False,
        }

    def export(self, output: Path, report: dict[str, Any]) -> None:
        output.mkdir(parents=True, exist_ok=True)
        event_text = "".join(json.dumps(asdict(item), sort_keys=True) + "\n" for item in self.events)
        report_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        manifest = {
            "model_version": "0.6.5", "profile": self.profile.name,
            "event_sha256": hashlib.sha256(event_text.encode()).hexdigest(),
            "report_sha256": hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "physical_contact": False, "physical_writes": False,
        }
        (output / "recovery-events.jsonl").write_text(event_text)
        (output / "report.json").write_text(report_text)
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def load_profile(path: Path) -> RecoveryProfile:
    return RecoveryProfile.from_dict(json.loads(path.read_text()))


def execute(profile: RecoveryProfile, output: Path | None = None, workpiece_id: str = "WP-001") -> dict[str, Any]:
    runtime = RecoveryRuntime(profile, workpiece_id)
    report = runtime.run()
    if output is not None:
        runtime.export(output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=Path)
    parser.add_argument("--output", type=Path, default=Path("evidence/demo"))
    args = parser.parse_args()
    print(json.dumps(execute(load_profile(args.profile), args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
