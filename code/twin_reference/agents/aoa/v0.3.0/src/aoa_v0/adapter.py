from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from ipaddress import ip_address, ip_network
from typing import Any, Callable, Literal

from pydantic import BaseModel, ConfigDict, Field

from .models import ActionProposal, Observation, ObservationKind


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_time(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


class AdapterConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runtime_mode: Literal["live", "replay", "simulation"] = "simulation"
    address_manifest: dict[str, str]
    stale_after_seconds: float = Field(default=30.0, gt=0)


class CanonicalObservationSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["aoa.dt.snapshot/1.0"] = "aoa.dt.snapshot/1.0"
    snapshot_id: str
    fingerprint_sha256: str
    captured_at: str
    source_timestamp: str | None
    runtime_mode: Literal["live", "replay", "simulation"]
    twin_revision: int
    entities: dict[str, dict[str, Any]]
    topology: list[dict[str, str]]
    inventory_count: int
    workpiece_count: int
    freshness_seconds: float | None
    quality: dict[str, Any]
    provenance: dict[str, Any]


PROTOCOL_PORTS = {
    "mqtt": (1883, "mqtt"),
    "opc/ua": (4840, "opcua"),
    "opc ua": (4840, "opcua"),
    "https": (443, "https"),
    "http/rest": (80, "http"),
    "ssh": (22, "ssh"),
    "tcp/5432": (5432, "postgresql"),
    "tcp/5433": (5433, "postgresql-mirror"),
}


class SmartFactorySnapshotAdapter:
    """Read-only projection of LiveTwinState.snapshot() for bounded AoA tools."""

    def __init__(
        self,
        snapshot_source: Callable[[], dict[str, Any]],
        configuration: AdapterConfiguration,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._snapshot_source = snapshot_source
        self.configuration = configuration
        self._clock = clock

    def capture(self) -> CanonicalObservationSnapshot:
        raw = deepcopy(self._snapshot_source())
        factory = deepcopy(raw.get("factory", raw))
        canonical = factory.get("canonical_state", {}) or {}
        communication = factory.get("communication", {}) or {}
        gc = communication.get("Gc", {}) or {}
        entities = deepcopy(canonical.get("entities", {}))

        vertices = gc.get("vertices", {}) or {}
        for entity_id, entity_type in vertices.items():
            entities.setdefault(entity_id, {"entity_type": entity_type, "projection": "communication_twin"})

        topology: list[dict[str, str]] = []
        for src, links in (gc.get("edges_with_protocol", {}) or {}).items():
            for link in links or []:
                topology.append({
                    "source": str(src),
                    "target": str(link.get("dst", "")),
                    "protocol": str(link.get("protocol", "unknown")),
                })

        source_value = canonical.get("captured_at") or factory.get("last_update")
        source_dt = _parse_time(source_value)
        captured_dt = self._clock().astimezone(timezone.utc)
        freshness = max((captured_dt - source_dt).total_seconds(), 0.0) if source_dt else None

        kinds: dict[str, int] = {}
        field_count = 0
        for fields in canonical.get("entities", {}).values():
            for record in fields.values():
                if isinstance(record, dict) and "kind" in record:
                    kind = str(record["kind"])
                    kinds[kind] = kinds.get(kind, 0) + 1
                    field_count += 1

        workpieces = factory.get("workpieces", {}) or {}
        inventory = factory.get("inventory", {}) or {}
        inventory_slots = inventory.get("slots", inventory) if isinstance(inventory, dict) else {}
        payload = {
            "runtime_mode": self.configuration.runtime_mode,
            "twin_revision": int(canonical.get("revision", 0) or 0),
            "entities": entities,
            "topology": topology,
            "inventory_count": len(inventory_slots) if isinstance(inventory_slots, dict) else 0,
            "workpiece_count": len(workpieces) if isinstance(workpieces, dict) else 0,
            "source_timestamp": source_dt.isoformat().replace("+00:00", "Z") if source_dt else None,
        }
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
        return CanonicalObservationSnapshot(
            snapshot_id=f"dt-{fingerprint[:16]}",
            fingerprint_sha256=fingerprint,
            captured_at=captured_dt.isoformat().replace("+00:00", "Z"),
            source_timestamp=payload["source_timestamp"],
            runtime_mode=self.configuration.runtime_mode,
            twin_revision=payload["twin_revision"],
            entities=entities,
            topology=topology,
            inventory_count=payload["inventory_count"],
            workpiece_count=payload["workpiece_count"],
            freshness_seconds=round(freshness, 6) if freshness is not None else None,
            quality={
                "canonical_field_count": field_count,
                "observation_kinds": kinds,
                "source_timestamp_present": source_dt is not None,
                "stale": freshness is None or freshness > self.configuration.stale_after_seconds,
                "address_manifest_declared": True,
            },
            provenance={
                "source_interface": "LiveTwinState.snapshot/read-only",
                "source_and_capture_time_separated": True,
                "physical_factory_contact": False,
                "state_changed": False,
            },
        )

    def _asset_inventory(self, snapshot: CanonicalObservationSnapshot) -> list[dict[str, str]]:
        assets = []
        for entity_id, address in self.configuration.address_manifest.items():
            if entity_id in snapshot.entities:
                item = snapshot.entities[entity_id]
                entity_type = item.get("entity_type", "digital_twin_entity") if isinstance(item, dict) else "digital_twin_entity"
                assets.append({"asset_id": entity_id, "address": address, "entity_type": str(entity_type)})
        return sorted(assets, key=lambda item: ip_address(item["address"]))

    @staticmethod
    def _services(snapshot: CanonicalObservationSnapshot, asset_id: str) -> dict[int, str]:
        services: dict[int, str] = {}
        for edge in snapshot.topology:
            if asset_id not in {edge["source"], edge["target"]}:
                continue
            protocol = edge["protocol"].lower()
            for marker, (port, service) in PROTOCOL_PORTS.items():
                if marker in protocol:
                    services[port] = service
        return dict(sorted(services.items()))

    def execute(self, proposal: ActionProposal, sequence: int) -> Observation:
        snapshot = self.capture()
        assets = self._asset_inventory(snapshot)
        by_address = {item["address"]: item for item in assets}

        if proposal.tool == "passive_entry_observation":
            target = str(proposal.arguments["target"])
            asset = by_address.get(target)
            data = {"target": target, "asset": asset, "snapshot_quality": snapshot.quality}
        elif proposal.tool == "safe_host_discovery":
            network = ip_network(str(proposal.arguments["cidr"]), strict=False)
            data = {
                "live_hosts": [item["address"] for item in assets if ip_address(item["address"]) in network],
                "assets": [item for item in assets if ip_address(item["address"]) in network],
            }
        elif proposal.tool == "safe_service_discovery":
            target = str(proposal.arguments["target"])
            asset = by_address.get(target)
            data = {
                "target": target,
                "asset_id": asset["asset_id"] if asset else "unknown",
                "role": asset["entity_type"] if asset else "unknown",
                "services": self._services(snapshot, asset["asset_id"]) if asset else {},
            }
        else:
            raise ValueError("tool is not implemented by the read-only Digital Twin adapter")

        kind = {
            "live": ObservationKind.OBSERVED,
            "replay": ObservationKind.REPLAYED,
            "simulation": ObservationKind.SIMULATED,
        }[self.configuration.runtime_mode]
        return Observation(
            sequence=sequence,
            action_id=proposal.action_id,
            tool=proposal.tool,
            arguments=proposal.arguments,
            source="behavioural_smart_factory_dt_adapter",
            kind=kind,
            confidence=1.0 if snapshot.quality["source_timestamp_present"] else 0.7,
            data=data,
            evidence={
                "snapshot_id": snapshot.snapshot_id,
                "fingerprint_sha256": snapshot.fingerprint_sha256,
                "source_timestamp": snapshot.source_timestamp,
                "captured_at": snapshot.captured_at,
                "twin_revision": snapshot.twin_revision,
                "physical_contact": False,
                "state_changed": False,
                "read_only_adapter": True,
            },
        )
