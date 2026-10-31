from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
from resource_scheduler import ResourceScheduler  # noqa: E402


class ResourceSchedulerTests(unittest.TestCase):
    CONFIG = ROOT / "config/resources.json"

    def test_two_workpieces_preserve_route_and_complete(self) -> None:
        scheduler = ResourceScheduler.from_file(self.CONFIG)
        evidence = scheduler.run([
            {"workpiece_id": "WP-001", "arrival_s": 0},
            {"workpiece_id": "WP-002", "arrival_s": 1},
        ])
        self.assertEqual(len(evidence["operations"]), 18)
        for workpiece in ("WP-001", "WP-002"):
            route = [item["resource"] for item in evidence["operations"] if item["workpiece_id"] == workpiece]
            self.assertEqual(route, scheduler.route)

    def test_vgr_reservations_never_overlap(self) -> None:
        scheduler = ResourceScheduler.from_file(self.CONFIG)
        evidence = scheduler.run([
            {"workpiece_id": f"WP-{index:03d}", "arrival_s": index * 0.5}
            for index in range(5)
        ])
        vgr = sorted((item["started_at"], item["finished_at"]) for item in evidence["operations"] if item["resource"] == "VGR")
        for previous, current in zip(vgr, vgr[1:]):
            self.assertLessEqual(previous[1], current[0])

    def test_queue_wait_and_utilisation_are_reported(self) -> None:
        scheduler = ResourceScheduler.from_file(self.CONFIG)
        evidence = scheduler.run([
            {"workpiece_id": "WP-A", "arrival_s": 0},
            {"workpiece_id": "WP-B", "arrival_s": 0},
        ])
        self.assertGreater(evidence["resource_wait_s"]["DSI"], 0)
        self.assertGreater(evidence["resource_utilisation"]["VGR"], 0)
        self.assertLessEqual(evidence["resource_utilisation"]["VGR"], 1)

    def test_hbw_capacity_and_duplicate_identity_fail_closed(self) -> None:
        scheduler = ResourceScheduler.from_file(self.CONFIG)
        with self.assertRaises(ValueError):
            scheduler.run([{"workpiece_id": f"WP-{index}", "arrival_s": 0} for index in range(10)])
        scheduler = ResourceScheduler.from_file(self.CONFIG)
        with self.assertRaises(ValueError):
            scheduler.run([
                {"workpiece_id": "WP-X", "arrival_s": 0},
                {"workpiece_id": "WP-X", "arrival_s": 1},
            ])

    def test_schedule_is_deterministic(self) -> None:
        arrivals = [{"workpiece_id": "WP-B", "arrival_s": 0}, {"workpiece_id": "WP-A", "arrival_s": 0}]
        first = ResourceScheduler.from_file(self.CONFIG).run(arrivals)
        second = ResourceScheduler.from_file(self.CONFIG).run(arrivals)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()

