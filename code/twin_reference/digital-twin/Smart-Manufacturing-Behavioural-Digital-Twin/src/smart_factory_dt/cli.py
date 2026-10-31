from __future__ import annotations

import argparse
import json

from .kernel import FactoryTwin


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic smart-factory DT cycles")
    parser.add_argument("--cycles", type=int, default=1)
    args = parser.parse_args()
    if args.cycles < 1:
        parser.error("--cycles must be at least 1")
    twin = FactoryTwin()
    for index in range(args.cycles):
        twin.run_cycle(f"WP-{index + 1:04d}")
    print(json.dumps(twin.snapshot(), indent=2, default=str))


if __name__ == "__main__":
    main()

