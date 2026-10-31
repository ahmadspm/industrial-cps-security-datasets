from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

STATIONS = ("dps", "vgr", "hbw", "mpo", "sld")
TOPICS = {"dps":"f/i/state/dsi", "vgr":"f/i/state/vgr", "hbw":"f/i/state/hbw", "mpo":"f/i/state/mpo", "sld":"f/i/state/sld"}

def secret(name: str) -> str:
    return Path(os.environ[name]).read_text().strip()

def payload(station: str, state: str, sequence: int, workpiece_id: str = "WP-001") -> str:
    return json.dumps({"station":station,"state":state,"sequence":sequence,"workpiece_id":workpiece_id,"provenance":"wire-simulated"}, separators=(",",":"))

def decode(value: Any) -> dict[str, Any]:
    if isinstance(value, bytes): value = value.decode()
    return json.loads(value)
