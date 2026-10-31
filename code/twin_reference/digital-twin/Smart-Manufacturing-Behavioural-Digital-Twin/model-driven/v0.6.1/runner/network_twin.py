"""Stateful offline network twin for the fischertechnik 24 V factory."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TrafficEvent:
    sequence: int
    simulation_ms: float
    source: str
    destination: str
    protocol: str
    operation: str
    detail: str
    size_bytes: int
    outcome: str = "delivered"
    topic: str | None = None
    qos: int | None = None
    workpiece_id: str | None = None
    station: str | None = None
    state: str | None = None


class EvidenceRecorder:
    def __init__(self) -> None:
        self.events: list[TrafficEvent] = []

    def add(self, **fields: Any) -> TrafficEvent:
        event = TrafficEvent(sequence=len(self.events) + 1, **fields)
        self.events.append(event)
        return event

    def export(self, directory: Path, manifest: dict[str, Any]) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "traffic.jsonl").open("w") as handle:
            for event in self.events:
                handle.write(json.dumps(asdict(event), sort_keys=True) + "\n")
        with (directory / "traffic.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(asdict(self.events[0]).keys()))
            writer.writeheader()
            writer.writerows(asdict(event) for event in self.events)
        (directory / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


class MqttBrokerModel:
    def __init__(self, recorder: EvidenceRecorder) -> None:
        self.recorder = recorder
        self.sessions: set[str] = set()
        self.subscriptions: dict[str, set[str]] = {}
        self.retained: dict[str, dict[str, Any]] = {}

    def connect(self, client: str, time_ms: float) -> None:
        self.sessions.add(client)
        self.recorder.add(simulation_ms=time_ms, source=client, destination="mqtt_broker", protocol="MQTT/TCP", operation="CONNECT", detail="persistent session", size_bytes=48)
        self.recorder.add(simulation_ms=time_ms + .2, source="mqtt_broker", destination=client, protocol="MQTT/TCP", operation="CONNACK", detail="session accepted", size_bytes=8)

    def subscribe(self, client: str, topic_filter: str, time_ms: float) -> None:
        if client not in self.sessions:
            raise PermissionError("MQTT client is not connected")
        self.subscriptions.setdefault(topic_filter, set()).add(client)
        self.recorder.add(simulation_ms=time_ms, source=client, destination="mqtt_broker", protocol="MQTT/TCP", operation="SUBSCRIBE", detail=topic_filter, topic=topic_filter, qos=1, size_bytes=40)
        self.recorder.add(simulation_ms=time_ms + .2, source="mqtt_broker", destination=client, protocol="MQTT/TCP", operation="SUBACK", detail="QoS 1 granted", topic=topic_filter, qos=1, size_bytes=8)

    @staticmethod
    def _matches(topic_filter: str, topic: str) -> bool:
        if topic_filter.endswith("/#"):
            return topic.startswith(topic_filter[:-1])
        return topic_filter == topic

    def publish(self, client: str, topic: str, payload: dict[str, Any], time_ms: float, qos: int = 1, retain: bool = False) -> list[str]:
        if client not in self.sessions:
            raise PermissionError("MQTT client is not connected")
        size = 32 + len(topic) + len(json.dumps(payload))
        self.recorder.add(simulation_ms=time_ms, source=client, destination="mqtt_broker", protocol="MQTT/TCP", operation="PUBLISH", detail="application message", topic=topic, qos=qos, size_bytes=size, workpiece_id=payload.get("workpiece_id"), station=payload.get("station"), state=payload.get("state"))
        if qos == 1:
            self.recorder.add(simulation_ms=time_ms + .3, source="mqtt_broker", destination=client, protocol="MQTT/TCP", operation="PUBACK", detail="packet acknowledged", topic=topic, qos=qos, size_bytes=8)
        if retain:
            self.retained[topic] = dict(payload)
        recipients = sorted({subscriber for flt, clients in self.subscriptions.items() if self._matches(flt, topic) for subscriber in clients})
        for recipient in recipients:
            self.recorder.add(simulation_ms=time_ms + .6, source="mqtt_broker", destination=recipient, protocol="MQTT/TCP", operation="PUBLISH_FORWARD", detail="matched subscription", topic=topic, qos=qos, size_bytes=size, workpiece_id=payload.get("workpiece_id"), station=payload.get("station"), state=payload.get("state"))
        return recipients


class OpcUaServerModel:
    def __init__(self, recorder: EvidenceRecorder) -> None:
        self.recorder = recorder
        self.sessions: set[str] = set()
        self.monitored: dict[str, set[str]] = {}
        self.values: dict[str, Any] = {}
        self.writable = {"Interface.Dashboard.Order", "Interface.TXT.SensorData", "Interface.TXT.NFC"}

    def activate_session(self, client: str, time_ms: float) -> None:
        self.sessions.add(client)
        for offset, operation in enumerate(("HELLO", "OPEN_SECURE_CHANNEL", "CREATE_SESSION", "ACTIVATE_SESSION")):
            self.recorder.add(simulation_ms=time_ms + offset * .4, source=client, destination="plc", protocol="OPC UA/UA TCP", operation=operation, detail="SecurityPolicy modelled", size_bytes=128 + offset * 24)

    def monitor(self, client: str, node: str, time_ms: float) -> None:
        if client not in self.sessions:
            raise PermissionError("OPC UA session is not active")
        self.monitored.setdefault(node, set()).add(client)
        self.recorder.add(simulation_ms=time_ms, source=client, destination="plc", protocol="OPC UA/UA TCP", operation="CREATE_MONITORED_ITEM", detail=node, size_bytes=196)

    def update(self, node: str, value: Any, time_ms: float, metadata: dict[str, Any]) -> list[str]:
        self.values[node] = value
        recipients = sorted(self.monitored.get(node, set()))
        for client in recipients:
            self.recorder.add(simulation_ms=time_ms, source="plc", destination=client, protocol="OPC UA/UA TCP", operation="DATA_CHANGE_NOTIFICATION", detail=node, size_bytes=220, **metadata)
        return recipients

    def write(self, client: str, node: str, value: Any, time_ms: float) -> bool:
        allowed = client in self.sessions and node in self.writable
        self.recorder.add(simulation_ms=time_ms, source=client, destination="plc", protocol="OPC UA/UA TCP", operation="WRITE", detail=node, size_bytes=208, outcome="accepted" if allowed else "denied")
        if allowed:
            self.values[node] = value
        return allowed


class PlcRuntime:
    def __init__(self, recorder: EvidenceRecorder, opcua: OpcUaServerModel, scan_ms: float = 20.0) -> None:
        self.recorder, self.opcua, self.scan_ms = recorder, opcua, scan_ms
        self.scan_number = 0
        self.input_image: dict[str, str] = {}
        self.output_image: dict[str, str] = {}

    def scan(self, station: str, sensor_state: str, actuator_action: str, time_ms: float, workpiece_id: str) -> float:
        self.scan_number += 1
        self.input_image[station] = sensor_state
        self.recorder.add(simulation_ms=time_ms, source=station, destination="plc", protocol="24 V digital/analog I/O", operation="READ_INPUT_IMAGE", detail=sensor_state, size_bytes=2, station=station, state=sensor_state, workpiece_id=workpiece_id)
        decision_time = time_ms + self.scan_ms * .6
        self.recorder.add(simulation_ms=decision_time, source="plc", destination="plc", protocol="IEC 61131-3 control", operation="EXECUTE_SCAN", detail=f"scan {self.scan_number}", size_bytes=0, station=station, state=sensor_state, workpiece_id=workpiece_id)
        self.output_image[station] = actuator_action
        end_time = time_ms + self.scan_ms
        self.recorder.add(simulation_ms=end_time, source="plc", destination=station, protocol="24 V digital/analog I/O", operation="WRITE_OUTPUT_IMAGE", detail=actuator_action, size_bytes=2, station=station, state=sensor_state, workpiece_id=workpiece_id)
        self.opcua.update(f"Factory.{station}.State", sensor_state, end_time + 1, {"station":station,"state":sensor_state,"workpiece_id":workpiece_id})
        return end_time


class FactoryNetworkTwin:
    STATES = [
        ("dps", "workpiece_detected", "hold_input"), ("vgr", "pick_input", "vacuum_on"),
        ("hbw", "store_workpiece", "move_to_slot"), ("vgr", "retrieve_workpiece", "transport_to_mpo"),
        ("mpo", "process_workpiece", "oven_and_machine"), ("vgr", "transport_to_sld", "move_to_sorting"),
        ("sld", "sort_by_colour", "conveyor_and_gate"), ("vgr", "deliver_output", "vacuum_off"),
        ("dps", "cycle_complete", "release_output")
    ]

    def __init__(self, root: Path) -> None:
        self.root = root
        self.assets = json.loads((root / "config/assets.json").read_text())
        self.topics = json.loads((root / "config/topics.json").read_text())
        self.zones = json.loads((root / "config/zones_conduits.json").read_text())
        self.recorder = EvidenceRecorder()
        self.broker = MqttBrokerModel(self.recorder)
        self.opcua = OpcUaServerModel(self.recorder)
        self.plc = PlcRuntime(self.recorder, self.opcua)
        self.canonical: dict[str, dict[str, Any]] = {}
        self.revision = 0
        self.time_ms = 0.0
        self._bootstrap()

    def _bootstrap(self) -> None:
        for client in ("iot_gateway", "digital_twin", "txt_controller"):
            self.broker.connect(client, self.time_ms)
            self.time_ms += 1
        self.broker.subscribe("digital_twin", "f/i/#", self.time_ms)
        self.broker.subscribe("iot_gateway", "i/#", self.time_ms + 1)
        self.opcua.activate_session("iot_gateway", self.time_ms + 2)
        self.time_ms += 6
        for station in {station for station, _, _ in self.STATES}:
            self.opcua.monitor("iot_gateway", f"Factory.{station}.State", self.time_ms)
            self.time_ms += .5

    def _topic(self, station: str, state: str) -> str:
        if station == "dps":
            return self.topics["state_topics"]["dps_output" if state == "cycle_complete" else "dps_input"]
        return self.topics["state_topics"][station]

    def _commit(self, payload: dict[str, Any], topic: str) -> None:
        self.revision += 1
        self.canonical[payload["station"]] = {**payload, "topic":topic, "revision":self.revision, "provenance":"simulated"}

    def run_complete_cycle(self, workpiece_id: str = "WP-001") -> dict[str, Any]:
        for station, state, actuator in self.STATES:
            self.time_ms += 250
            self.time_ms = self.plc.scan(station, state, actuator, self.time_ms, workpiece_id)
            topic = self._topic(station, state)
            payload = {"station":station,"state":state,"workpiece_id":workpiece_id,"plc_scan":self.plc.scan_number}
            recipients = self.broker.publish("iot_gateway", topic, payload, self.time_ms + 4, qos=1, retain=True)
            if "digital_twin" in recipients:
                self._commit(payload, topic)
        return {"workpiece_id":workpiece_id,"completed":True,"revision":self.revision,"traffic_events":len(self.recorder.events)}

    def publish_txt_telemetry(self, payload: dict[str, Any]) -> bool:
        self.time_ms += 25
        recipients = self.broker.publish("txt_controller", "i/bme680", payload, self.time_ms, qos=1)
        if "iot_gateway" in recipients:
            return self.opcua.write("iot_gateway", "Interface.TXT.SensorData", payload, self.time_ms + 2)
        return False

    def target_catalogue(self) -> list[dict[str, Any]]:
        allowed = []
        for asset in self.assets["assets"]:
            if asset["agent_exposure"] in {"simulated_service", "read_only_snapshot"}:
                allowed.append({"asset_id":asset["id"],"zone":asset["zone"],"services":asset.get("services",[]),"access":asset["agent_exposure"],"physical_writes":False})
        return allowed

    def manifest(self) -> dict[str, Any]:
        config_hash = hashlib.sha256((self.root / "config/assets.json").read_bytes() + (self.root / "config/topics.json").read_bytes() + (self.root / "config/zones_conduits.json").read_bytes()).hexdigest()
        return {"model_version":"0.6.1","config_sha256":config_hash,"traffic_events":len(self.recorder.events),"canonical_revision":self.revision,"physical_writes":False,"wire_protocol_emulation":False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("evidence/demo"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    twin = FactoryNetworkTwin(root)
    print(json.dumps(twin.run_complete_cycle(), indent=2))
    twin.recorder.export(args.output, twin.manifest())
    (args.output / "aoa-targets.json").write_text(json.dumps(twin.target_catalogue(), indent=2) + "\n")


if __name__ == "__main__":
    main()
