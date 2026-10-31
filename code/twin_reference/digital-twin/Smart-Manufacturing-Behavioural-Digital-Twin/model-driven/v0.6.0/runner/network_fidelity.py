"""Deterministic, offline cyber-physical communication model."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from heapq import heappop, heappush
import json
from pathlib import Path
import random
from typing import Any


@dataclass(frozen=True)
class HopTrace:
    link_id: str
    source: str
    target: str
    protocols: tuple[str, ...]
    latency_ms: float
    delivered: bool


@dataclass(frozen=True)
class DeliveryTrace:
    sequence: int
    source: str
    target: str
    observed_at_ms: float
    received_at_ms: float | None
    provenance: str
    payload: dict[str, Any]
    hops: tuple[HopTrace, ...]

    @property
    def delivered(self) -> bool:
        return self.received_at_ms is not None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class NetworkFidelityModel:
    def __init__(self, config: dict[str, Any], seed: int = 0):
        self.config = config
        self.random = random.Random(seed)
        self.nodes = config["nodes"]
        self.links = config["links"]

    @classmethod
    def from_file(cls, path: str | Path, seed: int = 0) -> "NetworkFidelityModel":
        return cls(json.loads(Path(path).read_text()), seed=seed)

    def _adjacency(self) -> dict[str, list[tuple[str, dict[str, Any]]]]:
        graph: dict[str, list[tuple[str, dict[str, Any]]]] = {node: [] for node in self.nodes}
        for link in self.links:
            graph[link["from"]].append((link["to"], link))
            if link.get("bidirectional"):
                graph[link["to"]].append((link["from"], link))
        return graph

    def path(self, source: str, target: str) -> list[tuple[str, str, dict[str, Any]]]:
        """Return the lowest nominal-latency configured path."""
        queue: list[tuple[float, str, list[tuple[str, str, dict[str, Any]]]]] = [(0.0, source, [])]
        visited: set[str] = set()
        graph = self._adjacency()
        while queue:
            cost, node, hops = heappop(queue)
            if node == target:
                return hops
            if node in visited:
                continue
            visited.add(node)
            for neighbour, link in graph[node]:
                if neighbour not in visited:
                    heappush(queue, (cost + float(link["latency_ms"]), neighbour, hops + [(node, neighbour, link)]))
        raise ValueError(f"No configured path from {source} to {target}")

    def can_command(self, source: str, target: str) -> bool:
        if not self.config["policies"].get("physical_write_enabled", False):
            return False
        forbidden = {tuple(edge) for edge in self.config["policies"]["forbidden_direct_edges"]}
        if (source, target) in forbidden:
            return False
        try:
            return all(link.get("writable", False) for _, _, link in self.path(source, target))
        except ValueError:
            return False

    def transmit(
        self,
        source: str,
        target: str,
        payload: dict[str, Any],
        sequence: int,
        observed_at_ms: float,
        provenance: str | None = None,
    ) -> DeliveryTrace:
        traces: list[HopTrace] = []
        elapsed = 0.0
        delivered = True
        for hop_source, hop_target, link in self.path(source, target):
            jitter = self.random.uniform(-float(link["jitter_ms"]), float(link["jitter_ms"]))
            latency = max(0.0, float(link["latency_ms"]) + jitter)
            lost = self.random.random() < float(link["loss_probability"])
            delivered = delivered and not lost
            elapsed += latency
            traces.append(HopTrace(link["id"], hop_source, hop_target, tuple(link["protocol_stack"]), latency, delivered))
            if lost:
                break
        return DeliveryTrace(
            sequence=sequence,
            source=source,
            target=target,
            observed_at_ms=observed_at_ms,
            received_at_ms=observed_at_ms + elapsed if delivered else None,
            provenance=provenance or self.config["policies"]["default_provenance"],
            payload=dict(payload),
            hops=tuple(traces),
        )


def canonical_observation(model: NetworkFidelityModel, station: str, state: str, sequence: int = 1) -> DeliveryTrace:
    return model.transmit(
        "plc",
        "digital_twin",
        {"station": station, "state": state, "source_protocol": "OPC UA→MQTT"},
        sequence=sequence,
        observed_at_ms=0.0,
    )
