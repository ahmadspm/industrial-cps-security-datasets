import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))

from impairment_lab import ImpairmentEngine, TwinReceiver, export, load_profile, run_experiment


class ImpairmentLabTests(unittest.TestCase):
    def profile(self, name):
        return load_profile(ROOT / "scenarios" / name)

    def test_nominal_cycle_completes_without_findings(self):
        report, _ = run_experiment(self.profile("nominal.json"))
        self.assertTrue(report["completed"])
        self.assertFalse(report["degraded"])
        self.assertEqual(report["unique_commits"], 9)

    def test_delay_and_jitter_mark_observations_stale(self):
        report, _ = run_experiment(self.profile("delay-jitter.json"))
        self.assertIn("STALE_OBSERVATION", report["finding_codes"])
        self.assertGreater(report["mean_latency_ms"], report["freshness_threshold_ms"])
        self.assertGreater(report["mean_ipdv_ms"], 0)

    def test_loss_creates_gap_and_prevents_completion(self):
        report, _ = run_experiment(self.profile("loss.json"))
        self.assertIn("MESSAGE_LOSS", report["finding_codes"])
        self.assertIn("SEQUENCE_GAP", report["finding_codes"])
        self.assertFalse(report["completed"])
        self.assertEqual(report["unique_commits"], 8)

    def test_qos1_duplicate_is_suppressed(self):
        report, _ = run_experiment(self.profile("duplication.json"))
        self.assertEqual(report["duplicate_deliveries"], 2)
        self.assertIn("DUPLICATE_SUPPRESSED", report["finding_codes"])
        self.assertEqual(report["unique_commits"], 9)
        self.assertTrue(report["completed"])

    def test_reordering_is_detected(self):
        report, deliveries = run_experiment(self.profile("reordering.json"))
        self.assertTrue({"SEQUENCE_GAP", "OUT_OF_ORDER"} <= set(report["finding_codes"]))
        orders = [item.sent_sequence for item in deliveries if item.outcome == "delivered"]
        self.assertGreater(orders.index(4), orders.index(5))

    def test_broker_disconnection_drops_bounded_window(self):
        report, _ = run_experiment(self.profile("disconnection.json"))
        self.assertEqual(report["dropped_messages"], 3)
        self.assertFalse(report["completed"])
        self.assertTrue(all(item["reason"] == "broker_disconnected" for item in report["findings"] if item["code"] == "MESSAGE_LOSS"))

    def test_disconnection_recovers_for_later_messages(self):
        report, _ = run_experiment(self.profile("disconnection.json"))
        self.assertEqual(report["final_states"]["dps"], "cycle_complete")
        self.assertIn("deliver_output", report["final_states"].values())

    def test_seeded_jitter_is_reproducible(self):
        first, _ = run_experiment(self.profile("delay-jitter.json"))
        second, _ = run_experiment(self.profile("delay-jitter.json"))
        self.assertEqual(first, second)

    def test_delivery_order_is_monotonic(self):
        _, deliveries = run_experiment(self.profile("duplication.json"))
        self.assertEqual([item.delivery_order for item in deliveries], list(range(1, len(deliveries) + 1)))

    def test_all_profiles_prohibit_physical_effects(self):
        for path in (ROOT / "scenarios").glob("*.json"):
            report, _ = run_experiment(load_profile(path))
            self.assertFalse(report["physical_contact"])
            self.assertFalse(report["physical_writes"])
            self.assertFalse(report["wire_protocol_emulation"])

    def test_export_is_machine_readable_and_synchronized(self):
        report, deliveries = run_experiment(self.profile("loss.json"))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            export(output, report, deliveries)
            lines = (output / "deliveries.jsonl").read_text().splitlines()
            self.assertEqual(len(lines), len(deliveries))
            self.assertEqual(json.loads((output / "report.json").read_text())["profile"]["name"], "loss")
            self.assertEqual(json.loads(lines[0])["delivery_order"], 1)

    def test_final_state_projection_is_last_received_per_station(self):
        report, _ = run_experiment(self.profile("nominal.json"))
        self.assertEqual(report["final_states"], {
            "dps":"cycle_complete", "vgr":"deliver_output", "hbw":"store_workpiece",
            "mpo":"process_workpiece", "sld":"sort_by_colour"
        })


if __name__ == "__main__":
    unittest.main()
