from __future__ import annotations

import json

from .workflow import AoAWorkflow, build_default_mission


def main() -> None:
    workflow = AoAWorkflow()
    state = workflow.run(build_default_mission())
    print(json.dumps({"report": state["report"], "evaluation": workflow.evaluate(state)}, indent=2))


if __name__ == "__main__":
    main()

