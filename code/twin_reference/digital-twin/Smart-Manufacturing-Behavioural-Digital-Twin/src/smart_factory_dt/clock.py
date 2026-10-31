"""Shared clock semantics for live, replay, and simulation twin modes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import RLock
from typing import Optional


class ClockMode(str, Enum):
    REALTIME = "realtime"
    MANUAL = "manual"
    REPLAY = "replay"


def parse_timestamp(value: object) -> datetime:
    """Normalize ISO-8601, Unix epoch, and datetime values to UTC."""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(float(value), tz=timezone.utc)
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("timestamp must not be empty")
        try:
            dt = datetime.fromtimestamp(float(text), tz=timezone.utc)
        except ValueError:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    else:
        raise TypeError(f"unsupported timestamp type: {type(value).__name__}")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass
class TwinClock:
    """One clock abstraction shared by all twin execution modes."""

    mode: ClockMode = ClockMode.REALTIME
    initial_time: Optional[datetime] = None
    speed: float = 1.0

    def __post_init__(self) -> None:
        if self.speed <= 0:
            raise ValueError("clock speed must be greater than zero")
        self._lock = RLock()
        self._current = parse_timestamp(self.initial_time or datetime.now(timezone.utc))

    def now(self) -> datetime:
        with self._lock:
            if self.mode == ClockMode.REALTIME:
                return datetime.now(timezone.utc)
            return self._current

    def now_iso(self) -> str:
        return self.now().isoformat().replace("+00:00", "Z")

    def set(self, timestamp: object) -> datetime:
        if self.mode == ClockMode.REALTIME:
            raise RuntimeError("a realtime clock cannot be set")
        with self._lock:
            self._current = parse_timestamp(timestamp)
            return self._current

    def advance(self, seconds: float) -> datetime:
        if self.mode == ClockMode.REALTIME:
            raise RuntimeError("a realtime clock cannot be advanced manually")
        if seconds < 0:
            raise ValueError("clock cannot move backwards")
        with self._lock:
            self._current += timedelta(seconds=float(seconds) * self.speed)
            return self._current


