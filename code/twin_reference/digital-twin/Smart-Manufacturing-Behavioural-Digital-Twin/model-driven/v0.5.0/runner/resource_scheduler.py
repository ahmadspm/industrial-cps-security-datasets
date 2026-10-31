from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Operation:
    workpiece_id: str
    sequence: int
    resource: str
    server: int
    requested_at: float
    started_at: float
    finished_at: float
    wait_s: float


class ResourceScheduler:
    """Deterministic finite-capacity scheduler with explicit reservations."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.route = list(config["route"])
        self.warehouse_slots = int(config["warehouse_slots"])
        self.resources = config["resources"]
        self.available = {
            name: [0.0] * int(spec["capacity"])
            for name, spec in self.resources.items()
        }
        self.operations: list[Operation] = []

    @classmethod
    def from_file(cls, path: str | Path) -> "ResourceScheduler":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def run(self, arrivals: list[dict[str, Any]]) -> dict[str, Any]:
        if len(arrivals) > self.warehouse_slots:
            raise ValueError("workpiece count exceeds HBW storage capacity")
        seen: set[str] = set()
        for item in sorted(arrivals, key=lambda row: (float(row["arrival_s"]), row["workpiece_id"])):
            workpiece_id = str(item["workpiece_id"])
            if workpiece_id in seen:
                raise ValueError(f"duplicate workpiece: {workpiece_id}")
            seen.add(workpiece_id)
            ready = float(item["arrival_s"])
            for sequence, resource in enumerate(self.route, 1):
                servers = self.available[resource]
                server = min(range(len(servers)), key=lambda index: (servers[index], index))
                start = max(ready, servers[server])
                duration = float(self.resources[resource]["duration_s"])
                finish = start + duration
                self.operations.append(Operation(
                    workpiece_id, sequence, resource, server, ready, start,
                    finish, start - ready,
                ))
                servers[server] = finish
                ready = finish
        return self.evidence()

    def evidence(self) -> dict[str, Any]:
        makespan = max((item.finished_at for item in self.operations), default=0.0)
        busy = {name: 0.0 for name in self.resources}
        wait = {name: 0.0 for name in self.resources}
        for item in self.operations:
            busy[item.resource] += item.finished_at - item.started_at
            wait[item.resource] += item.wait_s
        utilisation = {
            name: (busy[name] / (makespan * int(self.resources[name]["capacity"]))) if makespan else 0.0
            for name in self.resources
        }
        return {
            "schema": "smart-factory-dt.resource-trace/1.0",
            "makespan_s": makespan,
            "operations": [asdict(item) for item in self.operations],
            "resource_busy_s": busy,
            "resource_wait_s": wait,
            "resource_utilisation": utilisation,
        }

