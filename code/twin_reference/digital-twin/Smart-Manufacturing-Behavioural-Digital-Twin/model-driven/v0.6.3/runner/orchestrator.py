"""Workspace-native, bounded orchestration and conformance harness.

This module opens no sockets and performs no physical writes. It executes
independent asynchronous PLC, OPC UA projection, gateway, broker and Digital
Twin tasks and checks their causal evidence against a semantic oracle.
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


CYCLE = (
    ("dps", "workpiece_detected", "hold_input", "f/i/state/dsi"),
    ("vgr", "pick_input", "vacuum_on", "f/i/state/vgr"),
    ("hbw", "store_workpiece", "move_to_slot", "f/i/state/hbw"),
    ("vgr", "retrieve_workpiece", "transport_to_mpo", "f/i/state/vgr"),
    ("mpo", "process_workpiece", "oven_and_machine", "f/i/state/mpo"),
    ("vgr", "transport_to_sld", "move_to_sorting", "f/i/state/vgr"),
    ("sld", "sort_by_colour", "conveyor_and_gate", "f/i/state/sld"),
    ("vgr", "deliver_output", "vacuum_off", "f/i/state/vgr"),
    ("dps", "cycle_complete", "release_output", "f/i/state/dso"),
)


@dataclass(frozen=True)
class RuntimeEvent:
    sequence: int
    logical_ms: float
    correlation_id: str
    source: str
    destination: str
    protocol: str
    operation: str
    outcome: str
    payload: dict[str, Any]


class EvidenceLedger:
    def __init__(self) -> None:
        self.events: list[RuntimeEvent] = []
        self.logical_ms = 0.0

    def add(
        self,
        correlation_id: str,
        source: str,
        destination: str,
        protocol: str,
        operation: str,
        payload: dict[str, Any] | None = None,
        outcome: str = "delivered",
        advance_ms: float = 0.1,
    ) -> RuntimeEvent:
        self.logical_ms += advance_ms
        event = RuntimeEvent(
            sequence=len(self.events) + 1,
            logical_ms=round(self.logical_ms, 3),
            correlation_id=correlation_id,
            source=source,
            destination=destination,
            protocol=protocol,
            operation=operation,
            outcome=outcome,
            payload=dict(payload or {}),
        )
        self.events.append(event)
        return event

    def export(self, output: Path, report: dict[str, Any], manifest: dict[str, Any]) -> None:
        output.mkdir(parents=True, exist_ok=True)
        (output / "runtime-events.jsonl").write_text(
            "".join(json.dumps(asdict(item), sort_keys=True) + "\n" for item in self.events)
        )
        (output / "conformance-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def topic_matches(topic_filter: str, topic: str) -> bool:
    if topic_filter.endswith("/#"):
        return topic.startswith(topic_filter[:-1])
    return topic_filter == topic


class Broker:
    """Stateful MQTT semantic boundary; not a wire MQTT implementation."""

    PUBLISH_ACL = {
        "iot_gateway": ("f/i/#",),
        "txt_controller": ("i/#",),
        "digital_twin": (),
    }

    def __init__(self, ledger: EvidenceLedger) -> None:
        self.ledger = ledger
        self.sessions: set[str] = set()
        self.subscriptions: dict[str, list[tuple[str, asyncio.Queue]]] = {}

    async def connect(self, client: str) -> None:
        self.sessions.add(client)
        self.ledger.add("bootstrap", client, "mqtt_broker", "MQTT semantic", "CONNECT")
        self.ledger.add("bootstrap", "mqtt_broker", client, "MQTT semantic", "CONNACK")

    async def subscribe(self, client: str, topic_filter: str, queue: asyncio.Queue) -> None:
        if client not in self.sessions:
            raise PermissionError("MQTT client is not connected")
        self.subscriptions.setdefault(client, []).append((topic_filter, queue))
        self.ledger.add("bootstrap", client, "mqtt_broker", "MQTT semantic", "SUBSCRIBE", {"topic": topic_filter, "qos": 1})
        self.ledger.add("bootstrap", "mqtt_broker", client, "MQTT semantic", "SUBACK", {"topic": topic_filter, "qos": 1})

    async def publish(self, client: str, topic: str, payload: dict[str, Any], correlation_id: str) -> None:
        if client not in self.sessions:
            self.ledger.add(correlation_id, client, "mqtt_broker", "MQTT semantic", "PUBLISH", {"topic": topic}, "denied")
            raise PermissionError("MQTT client is not connected")
        allowed = any(topic_matches(pattern, topic) for pattern in self.PUBLISH_ACL.get(client, ()))
        if not allowed:
            self.ledger.add(correlation_id, client, "mqtt_broker", "MQTT semantic", "PUBLISH", {"topic": topic}, "denied")
            raise PermissionError(f"client {client} cannot publish {topic}")
        message = {"topic": topic, "payload": dict(payload), "qos": 1, "correlation_id": correlation_id}
        self.ledger.add(correlation_id, client, "mqtt_broker", "MQTT semantic", "PUBLISH", message)
        self.ledger.add(correlation_id, "mqtt_broker", client, "MQTT semantic", "PUBACK", {"topic": topic, "qos": 1})
        for subscriber, entries in self.subscriptions.items():
            for topic_filter, queue in entries:
                if topic_matches(topic_filter, topic):
                    await queue.put(message)
                    self.ledger.add(correlation_id, "mqtt_broker", subscriber, "MQTT semantic", "PUBLISH_FORWARD", message)


class OpcUaProjection:
    """Subscription/data-change semantic boundary; not UA Binary encoding."""

    def __init__(self, ledger: EvidenceLedger) -> None:
        self.ledger = ledger
        self.sessions: set[str] = set()
        self.monitored: dict[str, list[asyncio.Queue]] = {}

    async def activate(self, client: str) -> None:
        self.sessions.add(client)
        for operation in ("HELLO", "OPEN_SECURE_CHANNEL", "CREATE_SESSION", "ACTIVATE_SESSION"):
            self.ledger.add("bootstrap", client, "plc", "OPC UA semantic", operation)

    async def monitor(self, client: str, node: str, queue: asyncio.Queue) -> None:
        if client not in self.sessions:
            raise PermissionError("OPC UA session is not active")
        self.monitored.setdefault(node, []).append(queue)
        self.ledger.add("bootstrap", client, "plc", "OPC UA semantic", "CREATE_MONITORED_ITEM", {"node": node})

    async def update(self, node: str, value: str, payload: dict[str, Any], correlation_id: str) -> None:
        notification = {"node": node, "value": value, **payload, "correlation_id": correlation_id}
        for queue in self.monitored.get(node, []):
            await queue.put(notification)
            self.ledger.add(correlation_id, "plc", "iot_gateway", "OPC UA semantic", "DATA_CHANGE_NOTIFICATION", notification)


class DigitalTwinProjection:
    def __init__(self, ledger: EvidenceLedger) -> None:
        self.ledger = ledger
        self.canonical: dict[str, dict[str, Any]] = {}
        self.production_revision = 0
        self.last_cycle_sequence = 0
        self.findings: list[dict[str, Any]] = []

    async def consume(self, queue: asyncio.Queue) -> None:
        while True:
            message = await queue.get()
            try:
                if message is None:
                    return
                payload = message["payload"]
                if message["topic"].startswith("f/i/state/"):
                    observed = int(payload["cycle_sequence"])
                    if observed != self.last_cycle_sequence + 1:
                        self.findings.append({"code": "SEQUENCE_GAP", "expected": self.last_cycle_sequence + 1, "observed": observed})
                    self.last_cycle_sequence = observed
                    self.production_revision += 1
                    station = payload["station"]
                    self.canonical[station] = {
                        **payload,
                        "topic": message["topic"],
                        "revision": self.production_revision,
                        "classification": "simulated",
                    }
                    self.ledger.add(message["correlation_id"], "digital_twin", "canonical_state", "observation API", "TWIN_COMMIT", self.canonical[station])
            finally:
                queue.task_done()


class WorkspaceRuntime:
    REQUIRED_CHAIN = (
        "READ_INPUT_IMAGE", "EXECUTE_SCAN", "WRITE_OUTPUT_IMAGE",
        "DATA_CHANGE_NOTIFICATION", "PUBLISH", "PUBACK",
        "PUBLISH_FORWARD", "TWIN_COMMIT",
    )

    def __init__(self, timeout_s: float = 2.0) -> None:
        self.timeout_s = timeout_s
        self.ledger = EvidenceLedger()
        self.broker = Broker(self.ledger)
        self.opcua = OpcUaProjection(self.ledger)
        self.twin = DigitalTwinProjection(self.ledger)
        self.opc_queue: asyncio.Queue = asyncio.Queue(maxsize=4)
        self.twin_queue: asyncio.Queue = asyncio.Queue(maxsize=4)

    async def bootstrap(self) -> None:
        for client in ("iot_gateway", "digital_twin", "txt_controller"):
            await self.broker.connect(client)
        await self.broker.subscribe("digital_twin", "f/i/#", self.twin_queue)
        await self.opcua.activate("iot_gateway")
        for station in sorted({item[0] for item in CYCLE}):
            await self.opcua.monitor("iot_gateway", f"Factory.{station}.State", self.opc_queue)

    async def gateway_task(self) -> None:
        while True:
            notification = await self.opc_queue.get()
            try:
                if notification is None:
                    return
                payload = {
                    "station": notification["station"],
                    "state": notification["state"],
                    "workpiece_id": notification["workpiece_id"],
                    "cycle_sequence": notification["cycle_sequence"],
                    "source": "opcua",
                }
                await self.broker.publish("iot_gateway", notification["topic"], payload, notification["correlation_id"])
            finally:
                self.opc_queue.task_done()

    async def plc_task(self, workpiece_id: str) -> None:
        for number, (station, state, actuator, topic) in enumerate(CYCLE, 1):
            cid = f"{workpiece_id}:{number:02d}"
            common = {"station": station, "state": state, "workpiece_id": workpiece_id, "cycle_sequence": number}
            self.ledger.add(cid, station, "plc", "24 V I/O semantic", "READ_INPUT_IMAGE", common)
            self.ledger.add(cid, "plc", "plc", "IEC 61131-3 semantic", "EXECUTE_SCAN", common)
            self.ledger.add(cid, "plc", station, "24 V I/O semantic", "WRITE_OUTPUT_IMAGE", {**common, "actuator": actuator})
            await self.opcua.update(f"Factory.{station}.State", state, {**common, "topic": topic}, cid)
            await asyncio.wait_for(self.opc_queue.join(), timeout=self.timeout_s)
            await asyncio.wait_for(self.twin_queue.join(), timeout=self.timeout_s)

    async def run(self, workpiece_id: str = "WP-001") -> dict[str, Any]:
        await self.bootstrap()
        async with asyncio.TaskGroup() as tasks:
            tasks.create_task(self.gateway_task(), name="opcua-mqtt-gateway")
            tasks.create_task(self.twin.consume(self.twin_queue), name="digital-twin")
            await asyncio.wait_for(self.plc_task(workpiece_id), timeout=self.timeout_s * len(CYCLE))
            await self.opc_queue.put(None)
            await self.twin_queue.put(None)
        return self.conformance_report(workpiece_id)

    def conformance_report(self, workpiece_id: str) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []
        for number in range(1, len(CYCLE) + 1):
            cid = f"{workpiece_id}:{number:02d}"
            operations = [item.operation for item in self.ledger.events if item.correlation_id == cid]
            positions = [operations.index(required) if required in operations else -1 for required in self.REQUIRED_CHAIN]
            if -1 in positions or positions != sorted(positions):
                violations.append({"correlation_id": cid, "operations": operations})
        route = [self.twin.canonical[item[0]]["state"] for item in CYCLE if item[0] in self.twin.canonical]
        expected_final = {station: state for station, state, _, _ in CYCLE}
        final_states = {station: value["state"] for station, value in self.twin.canonical.items()}
        passed = not violations and not self.twin.findings and final_states == expected_final and self.twin.production_revision == len(CYCLE)
        return {
            "schema": "smart-factory-dt.runtime-conformance/1.0",
            "model_version": "0.6.3",
            "workpiece_id": workpiece_id,
            "passed": passed,
            "completed": final_states.get("dps") == "cycle_complete",
            "production_revision": self.twin.production_revision,
            "event_count": len(self.ledger.events),
            "final_states": final_states,
            "expected_final_states": expected_final,
            "state_sequence": [state for _, state, _, _ in CYCLE],
            "causal_violations": violations,
            "findings": list(self.twin.findings),
            "physical_contact": False,
            "physical_writes": False,
            "wire_protocol_emulation": False,
        }

    def manifest(self, report: dict[str, Any]) -> dict[str, Any]:
        event_bytes = "".join(json.dumps(asdict(item), sort_keys=True) + "\n" for item in self.ledger.events).encode()
        report_bytes = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
        return {
            "model_version": "0.6.3",
            "runtime": "python-asyncio-workspace",
            "event_sha256": hashlib.sha256(event_bytes).hexdigest(),
            "report_sha256": hashlib.sha256(report_bytes).hexdigest(),
            "event_count": len(self.ledger.events),
            "passed": report["passed"],
            "physical_contact": False,
            "physical_writes": False,
            "wire_protocol_emulation": False,
        }


async def execute(output: Path, workpiece_id: str = "WP-001") -> dict[str, Any]:
    runtime = WorkspaceRuntime()
    report = await runtime.run(workpiece_id)
    runtime.ledger.export(output, report, runtime.manifest(report))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("evidence/demo"))
    parser.add_argument("--workpiece", default="WP-001")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(execute(args.output, args.workpiece)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
