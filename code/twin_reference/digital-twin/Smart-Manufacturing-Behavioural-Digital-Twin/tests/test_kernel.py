import unittest
from datetime import datetime, timezone

from smart_factory_dt import ClockMode, FactoryTwin, ObservationKind, RuntimeMode, TwinClock


class FactoryTwinTests(unittest.TestCase):
    def test_complete_cycle_is_sequential_and_complete(self) -> None:
        twin = FactoryTwin(RuntimeMode.TEST)
        twin.run_cycle("WP-0001", "blue")
        snapshot = twin.snapshot()
        workpiece = snapshot["factory"]["workpieces"]["WP-0001"]
        self.assertEqual(workpiece["stage"], "COMPLETED")
        self.assertEqual(
            workpiece["route"],
            ["DSI", "VGR", "HBW", "VGR", "MPO", "VGR", "SLD", "VGR", "DSO"],
        )
        self.assertTrue(snapshot["read_only"])
        self.assertEqual(snapshot["schema"], "aoa.dt.snapshot/1.0")

    def test_snapshot_is_a_deep_copy(self) -> None:
        twin = FactoryTwin(RuntimeMode.TEST)
        snapshot = twin.snapshot()
        snapshot["factory"]["stations"]["DSI"]["state"] = "MUTATED"
        self.assertEqual(twin.stations["DSI"].state, "IDLE")

    def test_duplicate_workpiece_is_rejected(self) -> None:
        twin = FactoryTwin(RuntimeMode.TEST)
        twin.run_cycle("WP-0001")
        with self.assertRaises(ValueError):
            twin.run_cycle("WP-0001")

    def test_live_topic_updates_canonical_station_with_provenance(self) -> None:
        clock = TwinClock(ClockMode.MANUAL, datetime(2026, 8, 25, tzinfo=timezone.utc))
        twin = FactoryTwin(RuntimeMode.TEST, clock=clock)
        accepted = twin.observe_topic(
            "f/i/state/vgr",
            {"ts": "2026-08-25T00:00:01Z", "state": "TRANSPORT_TO_HBW", "active": True},
            source="factory-mqtt",
        )
        self.assertTrue(all(accepted.values()))
        entity = twin.canonical.entity("station:VGR")
        self.assertEqual(entity["state"]["value"], "TRANSPORT_TO_HBW")
        self.assertEqual(entity["state"]["kind"], "observed")
        self.assertEqual(entity["state"]["evidence"]["topic"], "f/i/state/vgr")

    def test_replayed_and_simulated_observations_are_distinguishable(self) -> None:
        clock = TwinClock(ClockMode.MANUAL, datetime(2026, 8, 25, tzinfo=timezone.utc))
        twin = FactoryTwin(RuntimeMode.TEST, clock=clock)
        twin.observe_topic("f/i/stock", {"ts": 1787616001, "count": 3}, kind=ObservationKind.REPLAYED)
        twin.observe_topic("fl/mpo/ack", {"ts": 1787616002, "code": 2}, kind=ObservationKind.SIMULATED)
        self.assertEqual(twin.canonical.entity("inventory:HBW")["count"]["kind"], "replayed")
        self.assertEqual(twin.canonical.entity("channel:FL/MPO/ACK")["code"]["kind"], "simulated")

    def test_stale_observation_is_audited_but_does_not_overwrite(self) -> None:
        clock = TwinClock(ClockMode.MANUAL, datetime(2026, 8, 25, tzinfo=timezone.utc))
        twin = FactoryTwin(RuntimeMode.TEST, clock=clock)
        twin.observe_topic("f/i/state/sld", {"ts": "2026-08-25T00:00:10Z", "state": "SORTING"})
        result = twin.observe_topic("f/i/state/sld", {"ts": "2026-08-25T00:00:05Z", "state": "IDLE"})
        self.assertFalse(result["state"])
        self.assertEqual(twin.canonical.entity("station:SLD")["state"]["value"], "SORTING")
        self.assertFalse(twin.canonical.history()[-1]["accepted"]["state"])


if __name__ == "__main__":
    unittest.main()

