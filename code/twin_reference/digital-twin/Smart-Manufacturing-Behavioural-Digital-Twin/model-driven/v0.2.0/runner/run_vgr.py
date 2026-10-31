from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys

from scxml_runner import ScxmlRunner


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python runner/run_vgr.py <scenario.json>")
    project = Path(__file__).resolve().parents[1]
    scenario = json.loads(Path(sys.argv[1]).read_text())
    runner = ScxmlRunner(project / "models/statecharts/vgr.scxml")
    trace = [asdict(runner.dispatch(event)) for event in scenario["events"]]
    output = {
        "schema": "smart-factory-dt.model-trace/1.0",
        "model": "VGR",
        "model_version": "0.2.0",
        "scenario": scenario["id"],
        "initial_state": "idle",
        "initial_actions": runner.initial_actions,
        "final_state": runner.state,
        "expected_final_state": scenario["expected_final_state"],
        "passed": runner.state == scenario["expected_final_state"],
        "steps": trace,
    }
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if output["passed"] else 1)


if __name__ == "__main__":
    main()

