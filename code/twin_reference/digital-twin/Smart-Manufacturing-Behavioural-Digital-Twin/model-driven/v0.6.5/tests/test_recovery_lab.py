import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))

from recovery_lab import RecoveryRuntime, execute, load_profile


class RecoveryLabTests(unittest.TestCase):
    def profile(self, name): return load_profile(ROOT / "scenarios" / name)

    def test_nominal_completes_exactly_once(self):
        report = execute(self.profile("nominal.json"))
        self.assertTrue(report["completed"])
        self.assertEqual(report["delivered_transitions"], 1)
        self.assertEqual(report["canonical_revision"], 9)

    def test_mqtt_loss_propagates_to_process_hold(self):
        runtime = RecoveryRuntime(self.profile("mqtt-loss-retry.json"))
        report = runtime.run()
        self.assertEqual(report["hold_count"], 1)
        self.assertTrue(any(item.action == "ENTER_HOLD" for item in runtime.events))
        self.assertIn("COMMUNICATION_TIMEOUT", {item["code"] for item in report["findings"]})

    def test_retry_replay_resumes_and_completes(self):
        report = execute(self.profile("mqtt-loss-retry.json"))
        self.assertTrue(report["completed"])
        self.assertEqual(report["retry_count"], 2)
        self.assertEqual(report["recovery_count"], 1)

    def test_broker_outage_uses_retained_snapshot(self):
        runtime = RecoveryRuntime(self.profile("broker-outage-resync.json"))
        report = runtime.run()
        self.assertTrue(report["completed"])
        self.assertTrue(any(item.action == "READ_RETAINED_SNAPSHOT" for item in runtime.events))

    def test_opcua_stale_is_distinguished_from_timeout(self):
        report = execute(self.profile("opcua-stale-recovery.json"))
        self.assertEqual({item["code"] for item in report["findings"]}, {"OBSERVATION_STALE"})
        self.assertTrue(report["completed"])

    def test_recovery_exhaustion_fails_safe(self):
        report = execute(self.profile("recovery-exhausted.json"))
        self.assertFalse(report["completed"])
        self.assertEqual(report["process_state"], "FAIL_SAFE")
        self.assertIn("RECOVERY_EXHAUSTED", {item["code"] for item in report["findings"]})

    def test_failed_recovery_keeps_current_resource_reserved(self):
        report = execute(self.profile("recovery-exhausted.json"))
        self.assertEqual(report["held_resources"], ["VGR"])
        self.assertEqual(report["workpiece_state"], "HELD_COMMUNICATION")

    def test_successful_recovery_releases_all_resources(self):
        for name in ("mqtt-loss-retry.json", "broker-outage-resync.json", "opcua-stale-recovery.json"):
            self.assertEqual(execute(self.profile(name))["held_resources"], [])

    def test_recovery_time_is_reported(self):
        report = execute(self.profile("broker-outage-resync.json"))
        self.assertEqual(report["recovery_time_ms"], 900.0)

    def test_identity_is_preserved_across_recovery(self):
        report = execute(self.profile("mqtt-loss-retry.json"), workpiece_id="WP-RED-77")
        self.assertEqual(report["workpiece_id"], "WP-RED-77")
        self.assertTrue(report["completed"])

    def test_evidence_export_is_parseable(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            report = execute(self.profile("mqtt-loss-retry.json"), output)
            lines = (output / "recovery-events.jsonl").read_text().splitlines()
            self.assertEqual(len(lines), report["event_count"])
            self.assertEqual(json.loads(lines[-1])["sequence"], len(lines))

    def test_all_profiles_prohibit_physical_effects(self):
        for path in (ROOT / "scenarios").glob("*.json"):
            report = execute(load_profile(path))
            self.assertFalse(report["physical_contact"])
            self.assertFalse(report["physical_writes"])


if __name__ == "__main__": unittest.main()
