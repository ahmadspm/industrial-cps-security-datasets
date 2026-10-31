from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
V02_RUNNER = ROOT.parent / "model-driven" / "v0.2.0" / "runner"
sys.path.insert(0, str(V02_RUNNER))
from scxml_runner import ScxmlRunner  # noqa: E402


SCENARIOS = {
    "dsi": ["sensor.workpiece_present", "nfc.valid", "vgr.pick_confirmed", "sensor.clear"],
    "hbw": ["command.store", "sensor.container_at_input", "sensor.workpiece_stored", "sensor.container_stored", "internal.reset"],
    "mpo": ["command.process", "timer.burn_complete", "sensor.at_saw", "timer.saw_complete", "sensor.at_eject", "sensor.ejected", "vgr.pick_confirmed", "internal.reset"],
    "sld": ["command.sort", "sensor.entry", "sensor.colour_detected", "encoder.started", "route.red", "sensor.ejected", "internal.reset"],
    "dso": ["vgr.place_confirmed", "sensor.output_present", "operator.remove", "sensor.clear"],
}


class StationModelTests(unittest.TestCase):
    def test_all_models_are_well_formed_scxml(self) -> None:
        for station in SCENARIOS:
            root = ET.parse(ROOT / "models/statecharts" / f"{station}.scxml").getroot()
            self.assertEqual(root.tag, "{http://www.w3.org/2005/07/scxml}scxml")
            self.assertEqual(root.attrib["version"], "1.0")

    def test_nominal_station_cycles_return_idle(self) -> None:
        for station, events in SCENARIOS.items():
            runner = ScxmlRunner(ROOT / "models/statecharts" / f"{station}.scxml")
            for event in events:
                runner.dispatch(event)
            self.assertEqual(runner.state, "idle", station)

    def test_invalid_events_fail_closed(self) -> None:
        for station in SCENARIOS:
            runner = ScxmlRunner(ROOT / "models/statecharts" / f"{station}.scxml")
            with self.assertRaises(ValueError, msg=station):
                runner.dispatch("unapproved.external.command")

    def test_fault_paths_enter_safe_state_and_reset(self) -> None:
        for station in SCENARIOS:
            runner = ScxmlRunner(ROOT / "models/statecharts" / f"{station}.scxml")
            runner.dispatch("fault.sensor")
            self.assertEqual(runner.state, "fault", station)
            self.assertTrue(any("safe_stop" in action for action in runner.trace[-1].actions), station)
            runner.dispatch("command.reset")
            self.assertEqual(runner.state, "idle", station)


if __name__ == "__main__":
    unittest.main()
