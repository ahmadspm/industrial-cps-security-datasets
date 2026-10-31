import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
from network_twin import FactoryNetworkTwin, MqttBrokerModel, EvidenceRecorder


class FactoryNetworkTwinTests(unittest.TestCase):
    def setUp(self): self.twin = FactoryNetworkTwin(ROOT)

    def test_all_physical_stations_are_independent_assets_without_ips(self):
        assets = {a["id"]:a for a in self.twin.assets["assets"]}
        for station in ("dps","vgr","hbw","mpo","sld","ssc"):
            self.assertIn(station, assets)
            self.assertIsNone(assets[station]["ip"])

    def test_vendor_controller_addresses_are_modelled(self):
        assets = {a["id"]:a for a in self.twin.assets["assets"]}
        self.assertEqual(assets["plc"]["ip"], "198.18.1.1")
        self.assertEqual(assets["iot_gateway"]["ip"], "198.18.1.5")
        self.assertEqual(assets["txt_controller"]["ip"], "198.18.1.10")

    def test_complete_cycle_updates_every_production_station(self):
        result = self.twin.run_complete_cycle()
        self.assertTrue(result["completed"])
        self.assertEqual(set(self.twin.canonical), {"dps","vgr","hbw","mpo","sld"})
        self.assertEqual(self.twin.canonical["dps"]["state"], "cycle_complete")

    def test_cycle_couples_io_scan_opcua_mqtt_and_twin(self):
        self.twin.run_complete_cycle()
        operations = {e.operation for e in self.twin.recorder.events}
        for required in ("READ_INPUT_IMAGE","EXECUTE_SCAN","WRITE_OUTPUT_IMAGE","DATA_CHANGE_NOTIFICATION","PUBLISH","PUBACK","PUBLISH_FORWARD"):
            self.assertIn(required, operations)

    def test_mqtt_requires_connection(self):
        broker = MqttBrokerModel(EvidenceRecorder())
        with self.assertRaises(PermissionError): broker.publish("intruder", "f/i/state/vgr", {}, 0)

    def test_topic_filter_routes_factory_events(self):
        self.twin.run_complete_cycle()
        forwards = [e for e in self.twin.recorder.events if e.operation == "PUBLISH_FORWARD" and e.destination == "digital_twin"]
        self.assertEqual(len(forwards), len(self.twin.STATES))

    def test_unlisted_opcua_write_fails_closed(self):
        self.assertFalse(self.twin.opcua.write("iot_gateway", "Factory.vgr.Motor", 1, 20))

    def test_txt_telemetry_uses_mqtt_then_allowlisted_opcua_write(self):
        self.assertTrue(self.twin.publish_txt_telemetry({"temperature":22.4,"humidity":41.0}))
        tail = self.twin.recorder.events[-3:]
        self.assertIn("PUBLISH_FORWARD", [e.operation for e in tail])
        self.assertEqual(tail[-1].operation, "WRITE")
        self.assertEqual(tail[-1].outcome, "accepted")

    def test_aoa_catalogue_excludes_physical_station_access(self):
        catalogue = self.twin.target_catalogue()
        self.assertFalse({"dps","vgr","hbw","mpo","sld","ssc"} & {a["asset_id"] for a in catalogue})
        self.assertTrue(all(not a["physical_writes"] for a in catalogue))

    def test_evidence_export_is_synchronized_and_machine_readable(self):
        self.twin.run_complete_cycle()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            self.twin.recorder.export(path, self.twin.manifest())
            lines = (path / "traffic.jsonl").read_text().splitlines()
            self.assertEqual(len(lines), len(self.twin.recorder.events))
            self.assertEqual(json.loads(lines[-1])["sequence"], len(lines))
            self.assertFalse(json.loads((path / "manifest.json").read_text())["physical_writes"])


if __name__ == "__main__": unittest.main()
