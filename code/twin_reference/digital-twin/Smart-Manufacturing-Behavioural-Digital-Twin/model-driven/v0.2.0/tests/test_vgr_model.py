from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))

from scxml_runner import ScxmlRunner  # noqa: E402


class VgrModelTests(unittest.TestCase):
    MODEL = ROOT / "models/statecharts/vgr.scxml"

    def test_scxml_is_well_formed_and_versioned(self) -> None:
        root = ET.parse(self.MODEL).getroot()
        self.assertEqual(root.tag, "{http://www.w3.org/2005/07/scxml}scxml")
        self.assertEqual(root.attrib["version"], "1.0")

    def test_nominal_transfer_returns_ready(self) -> None:
        runner = ScxmlRunner(self.MODEL)
        events = [
            "command.start", "sensor.x_reference", "sensor.z_reference",
            "sensor.rotation_reference", "command.pick", "sensor.pick_height",
            "sensor.vacuum_detected", "sensor.z_reference", "sensor.target_rotation",
            "sensor.place_height", "sensor.vacuum_released", "sensor.z_reference",
            "sensor.rotation_reference", "internal.reset",
        ]
        for event in events:
            runner.dispatch(event)
        self.assertEqual(runner.state, "ready")
        self.assertEqual(len(runner.trace), 14)
        self.assertIn("VGR.transfer.complete", runner.trace[-2].actions)

    def test_vacuum_timeout_enters_safe_fault_and_recovers(self) -> None:
        runner = ScxmlRunner(self.MODEL)
        for event in [
            "command.start", "sensor.x_reference", "sensor.z_reference",
            "sensor.rotation_reference", "command.pick", "sensor.pick_height",
            "timer.vacuum_timeout",
        ]:
            runner.dispatch(event)
        self.assertEqual(runner.state, "fault")
        self.assertIn("VGR.safe_stop", runner.trace[-1].actions)
        runner.dispatch("command.acknowledge")
        self.assertEqual(runner.state, "home_horizontal")

    def test_invalid_event_fails_closed(self) -> None:
        runner = ScxmlRunner(self.MODEL)
        with self.assertRaises(ValueError):
            runner.dispatch("sensor.place_height")


if __name__ == "__main__":
    unittest.main()

