import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))

from network_fidelity import NetworkFidelityModel, canonical_observation


class NetworkFidelityTests(unittest.TestCase):
    def setUp(self):
        self.config_path = ROOT / "config" / "cyber_physical_network.json"
        self.model = NetworkFidelityModel.from_file(self.config_path, seed=11)

    def test_plc_observation_uses_vendor_gateway_path(self):
        path = self.model.path("plc", "digital_twin")
        self.assertEqual(
            [(source, target) for source, target, _ in path],
            [("plc", "opcua_server"), ("opcua_server", "iot_gateway"),
             ("iot_gateway", "mqtt_broker"), ("mqtt_broker", "digital_twin")],
        )

    def test_station_control_plane_does_not_cross_mqtt(self):
        path = self.model.path("plc", "station_io")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0][2]["plane"], "control")
        self.assertNotIn("MQTT", path[0][2]["protocol_stack"])

    def test_observation_preserves_provenance_sequence_and_protocols(self):
        trace = canonical_observation(self.model, "VGR", "TRANSPORT_TO_HBW", sequence=42)
        self.assertTrue(trace.delivered)
        self.assertEqual(trace.sequence, 42)
        self.assertEqual(trace.provenance, "simulated")
        self.assertEqual(trace.payload["station"], "VGR")
        protocol_text = " ".join(p for hop in trace.hops for p in hop.protocols)
        self.assertIn("OPC UA", protocol_text)
        self.assertIn("MQTT", protocol_text)

    def test_identical_seed_is_deterministic(self):
        first = canonical_observation(NetworkFidelityModel.from_file(self.config_path, seed=7), "MPO", "OVEN")
        second = canonical_observation(NetworkFidelityModel.from_file(self.config_path, seed=7), "MPO", "OVEN")
        self.assertEqual(first, second)

    def test_loss_stops_delivery(self):
        config = json.loads(self.config_path.read_text())
        next(link for link in config["links"] if link["id"] == "gateway-mqtt")["loss_probability"] = 1.0
        trace = canonical_observation(NetworkFidelityModel(config, seed=1), "SLD", "SORTING")
        self.assertFalse(trace.delivered)
        self.assertEqual(trace.hops[-1].link_id, "gateway-mqtt")

    def test_physical_commands_fail_closed(self):
        self.assertFalse(self.model.can_command("digital_twin", "station_io"))
        self.assertFalse(self.model.can_command("mqtt_broker", "plc"))


if __name__ == "__main__":
    unittest.main()
