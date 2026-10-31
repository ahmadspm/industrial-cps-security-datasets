from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/2005/07/scxml}"


@dataclass(frozen=True)
class TraceStep:
    step: int
    event: str
    source: str
    target: str
    actions: tuple[str, ...]


class ScxmlRunner:
    """Small deterministic adapter for this model's event/transition subset."""

    def __init__(self, model_path: str | Path) -> None:
        self.root = ET.parse(model_path).getroot()
        self.states: dict[str, ET.Element] = {}
        self.parent: dict[str, str | None] = {}
        self._index(self.root, None)
        initial = self.root.attrib["initial"]
        self.state = self._initial_atomic(initial)
        self.initial_actions = self._entry_actions(self.state)
        self.trace: list[TraceStep] = []

    def _index(self, element: ET.Element, parent_id: str | None) -> None:
        for child in element:
            if child.tag == f"{NS}state":
                state_id = child.attrib["id"]
                if state_id in self.states:
                    raise ValueError(f"duplicate state: {state_id}")
                self.states[state_id] = child
                self.parent[state_id] = parent_id
                self._index(child, state_id)

    def _initial_atomic(self, state_id: str) -> str:
        state = self.states[state_id]
        while "initial" in state.attrib:
            state_id = state.attrib["initial"]
            state = self.states[state_id]
        return state_id

    def _entry_actions(self, state_id: str) -> tuple[str, ...]:
        actions: list[str] = []
        onentry = self.states[state_id].find(f"{NS}onentry")
        if onentry is not None:
            for log in onentry.findall(f"{NS}log"):
                expr = log.attrib.get("expr", "").strip("'\"")
                actions.append(expr)
        return tuple(actions)

    @staticmethod
    def _matches(patterns: str, event: str) -> bool:
        for pattern in patterns.split():
            if pattern == event or (pattern.endswith(".*") and event.startswith(pattern[:-1])):
                return True
        return False

    def dispatch(self, event: str) -> TraceStep:
        candidate: str | None = self.state
        transition: ET.Element | None = None
        while candidate is not None and transition is None:
            for item in self.states[candidate].findall(f"{NS}transition"):
                if self._matches(item.attrib.get("event", ""), event):
                    transition = item
                    break
            candidate = self.parent[candidate]
        if transition is None:
            raise ValueError(f"event {event!r} is invalid in state {self.state!r}")
        source = self.state
        target = self._initial_atomic(transition.attrib["target"])
        self.state = target
        step = TraceStep(len(self.trace) + 1, event, source, target, self._entry_actions(target))
        self.trace.append(step)
        return step

