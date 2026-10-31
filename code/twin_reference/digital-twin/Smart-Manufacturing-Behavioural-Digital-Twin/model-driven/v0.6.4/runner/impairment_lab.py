"""Deterministic communication-impairment laboratory for the factory twin."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import random
from statistics import mean
from typing import Any


CYCLE = (
    ("dps", "workpiece_detected", "f/i/state/dsi"),
    ("vgr", "pick_input", "f/i/state/vgr"),
    ("hbw", "store_workpiece", "f/i/state/hbw"),
    ("vgr", "retrieve_workpiece", "f/i/state/vgr"),
    ("mpo", "process_workpiece", "f/i/state/mpo"),
    ("vgr", "transport_to_sld", "f/i/state/vgr"),
    ("sld", "sort_by_colour", "f/i/state/sld"),
    ("vgr", "deliver_output", "f/i/state/vgr"),
    ("dps", "cycle_complete", "f/i/state/dso"),
)


@dataclass(frozen=True)
class ImpairmentProfile:
    name: str
    fixed_delay_ms: float = 0.0
    jitter_ms: float = 0.0
    loss_sequences: tuple[int, ...] = ()
    duplicate_sequences: tuple[int, ...] = ()
    reorder_pair: tuple[int, int] | None = None
    disconnect_from: int | None = None
    disconnect_through: int | None = None
    freshness_threshold_ms: float = 250.0
    seed: int = 640

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ImpairmentProfile":
        data = dict(value)
        for key in ("loss_sequences", "duplicate_sequences"):
            data[key] = tuple(data.get(key, ()))
        if data.get("reorder_pair") is not None:
            data["reorder_pair"] = tuple(data["reorder_pair"])
        return cls(**data)


@dataclass(frozen=True)
class Delivery:
    sent_sequence: int
    delivery_order: int
    station: str
    state: str
    topic: str
    workpiece_id: str
    sent_ms: float
    received_ms: float | None
    latency_ms: float | None
    outcome: str
    duplicate: bool = False
    reason: str | None = None


class ImpairmentEngine:
    def __init__(self, profile: ImpairmentProfile) -> None:
        self.profile = profile
        self.random = random.Random(profile.seed)

    def _disconnected(self, sequence: int) -> bool:
        start, end = self.profile.disconnect_from, self.profile.disconnect_through
        return start is not None and end is not None and start <= sequence <= end

    def apply(self, workpiece_id: str = "WP-001") -> list[Delivery]:
        pending: list[dict[str, Any]] = []
        for sequence, (station, state, topic) in enumerate(CYCLE, 1):
            sent_ms = sequence * 250.0
            if self._disconnected(sequence):
                pending.append(dict(sent_sequence=sequence, station=station, state=state, topic=topic,
                                    workpiece_id=workpiece_id, sent_ms=sent_ms, received_ms=None,
                                    latency_ms=None, outcome="dropped", duplicate=False,
                                    reason="broker_disconnected"))
                continue
            if sequence in self.profile.loss_sequences:
                pending.append(dict(sent_sequence=sequence, station=station, state=state, topic=topic,
                                    workpiece_id=workpiece_id, sent_ms=sent_ms, received_ms=None,
                                    latency_ms=None, outcome="dropped", duplicate=False,
                                    reason="profile_loss"))
                continue
            jitter = self.random.uniform(-self.profile.jitter_ms, self.profile.jitter_ms)
            latency = max(0.0, self.profile.fixed_delay_ms + jitter)
            record = dict(sent_sequence=sequence, station=station, state=state, topic=topic,
                          workpiece_id=workpiece_id, sent_ms=sent_ms,
                          received_ms=round(sent_ms + latency, 3), latency_ms=round(latency, 3),
                          outcome="delivered", duplicate=False, reason=None)
            pending.append(record)
            if sequence in self.profile.duplicate_sequences:
                duplicate = dict(record)
                duplicate["received_ms"] = round(record["received_ms"] + 1.0, 3)
                duplicate["latency_ms"] = round(record["latency_ms"] + 1.0, 3)
                duplicate["duplicate"] = True
                duplicate["reason"] = "qos1_redelivery"
                pending.append(duplicate)

        delivered = [item for item in pending if item["outcome"] == "delivered"]
        if self.profile.reorder_pair:
            first, second = self.profile.reorder_pair
            left = next((item for item in delivered if item["sent_sequence"] == first and not item["duplicate"]), None)
            right = next((item for item in delivered if item["sent_sequence"] == second and not item["duplicate"]), None)
            if left and right:
                right["received_ms"] = right["sent_ms"]
                left["received_ms"] = right["received_ms"] + 0.5
                left["latency_ms"] = round(left["received_ms"] - left["sent_ms"], 3)
                right["latency_ms"] = round(right["received_ms"] - right["sent_ms"], 3)
                left["reason"] = right["reason"] = "profile_reorder"

        delivered.sort(key=lambda item: (item["received_ms"], item["duplicate"]))
        drops = [item for item in pending if item["outcome"] == "dropped"]
        ordered = delivered + drops
        return [Delivery(delivery_order=index, **item) for index, item in enumerate(ordered, 1)]


class TwinReceiver:
    def __init__(self, freshness_threshold_ms: float) -> None:
        self.freshness_threshold_ms = freshness_threshold_ms
        self.expected_sequence = 1
        self.last_arrival_sequence = 0
        self.seen: set[int] = set()
        self.revision = 0
        self.canonical: dict[str, dict[str, Any]] = {}
        self.findings: list[dict[str, Any]] = []

    def accept(self, delivery: Delivery) -> None:
        if delivery.outcome != "delivered":
            self.findings.append({"code": "MESSAGE_LOSS", "sequence": delivery.sent_sequence, "reason": delivery.reason})
            return
        sequence = delivery.sent_sequence
        if sequence in self.seen:
            self.findings.append({"code": "DUPLICATE_SUPPRESSED", "sequence": sequence})
            return
        if sequence < self.last_arrival_sequence:
            self.findings.append({"code": "OUT_OF_ORDER", "previous": self.last_arrival_sequence, "observed": sequence})
        if sequence != self.expected_sequence:
            code = "SEQUENCE_GAP" if sequence > self.expected_sequence else "OUT_OF_ORDER"
            self.findings.append({"code": code, "expected": self.expected_sequence, "observed": sequence})
        if delivery.latency_ms is not None and delivery.latency_ms > self.freshness_threshold_ms:
            self.findings.append({"code": "STALE_OBSERVATION", "sequence": sequence, "latency_ms": delivery.latency_ms})
        self.seen.add(sequence)
        self.last_arrival_sequence = sequence
        while self.expected_sequence in self.seen:
            self.expected_sequence += 1
        self.revision += 1
        self.canonical[delivery.station] = {
            "state": delivery.state,
            "topic": delivery.topic,
            "cycle_sequence": sequence,
            "revision": self.revision,
            "received_ms": delivery.received_ms,
            "classification": "impaired-simulated",
        }


def run_experiment(profile: ImpairmentProfile, workpiece_id: str = "WP-001") -> tuple[dict[str, Any], list[Delivery]]:
    deliveries = ImpairmentEngine(profile).apply(workpiece_id)
    receiver = TwinReceiver(profile.freshness_threshold_ms)
    for item in deliveries:
        receiver.accept(item)
    delivered = [item for item in deliveries if item.outcome == "delivered"]
    unique = [item for item in delivered if not item.duplicate]
    latencies = [item.latency_ms for item in unique if item.latency_ms is not None]
    successive_variation = [abs(latencies[index] - latencies[index - 1]) for index in range(1, len(latencies))]
    codes = sorted({item["code"] for item in receiver.findings})
    final_dps = receiver.canonical.get("dps", {}).get("state")
    report = {
        "schema": "smart-factory-dt.impairment-report/1.0",
        "model_version": "0.6.4",
        "profile": asdict(profile),
        "workpiece_id": workpiece_id,
        "sent_messages": len(CYCLE),
        "delivered_messages": len(delivered),
        "unique_commits": receiver.revision,
        "dropped_messages": sum(item.outcome == "dropped" for item in deliveries),
        "duplicate_deliveries": sum(item.duplicate for item in deliveries),
        "mean_latency_ms": round(mean(latencies), 3) if latencies else None,
        "max_latency_ms": max(latencies) if latencies else None,
        "mean_ipdv_ms": round(mean(successive_variation), 3) if successive_variation else 0.0,
        "freshness_threshold_ms": profile.freshness_threshold_ms,
        "finding_codes": codes,
        "findings": receiver.findings,
        "final_states": {key: value["state"] for key, value in receiver.canonical.items()},
        "completed": final_dps == "cycle_complete" and receiver.seen == set(range(1, 10)),
        "degraded": bool(receiver.findings),
        "physical_contact": False,
        "physical_writes": False,
        "wire_protocol_emulation": False,
    }
    return report, deliveries


def export(output: Path, report: dict[str, Any], deliveries: list[Delivery]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    event_text = "".join(json.dumps(asdict(item), sort_keys=True) + "\n" for item in deliveries)
    report_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    manifest = {
        "model_version": "0.6.4",
        "profile": report["profile"]["name"],
        "event_sha256": hashlib.sha256(event_text.encode()).hexdigest(),
        "report_sha256": hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "physical_contact": False,
        "physical_writes": False,
        "wire_protocol_emulation": False,
    }
    (output / "deliveries.jsonl").write_text(event_text)
    (output / "report.json").write_text(report_text)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def load_profile(path: Path) -> ImpairmentProfile:
    return ImpairmentProfile.from_dict(json.loads(path.read_text()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=Path)
    parser.add_argument("--output", type=Path, default=Path("evidence/demo"))
    parser.add_argument("--workpiece", default="WP-001")
    args = parser.parse_args()
    report, deliveries = run_experiment(load_profile(args.profile), args.workpiece)
    export(args.output, report, deliveries)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
