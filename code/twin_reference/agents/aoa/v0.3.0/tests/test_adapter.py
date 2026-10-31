from __future__ import annotations

import copy
import unittest
from datetime import datetime, timezone

from aoa_v0.adapter import AdapterConfiguration, SmartFactorySnapshotAdapter
from aoa_v0.models import ActionProposal


def fixture_snapshot():
    return {
        "factory": {
            "canonical_state": {
                "revision": 12,
                "captured_at": "2026-08-24T03:00:00Z",
                "entities": {
                    "vgr": {"active": {"value": True, "kind": "observed"}},
                    "plc": {"state": {"value": "RUN", "kind": "observed"}},
                },
            },
            "communication": {
                "Gc": {
                    "vertices": {
                        "IOT_Gateway": "iot_gateway_raspberry_pi",
                        "PLC": "plc_24v",
                        "DigitalTwin": "digital_twin_software",
                        "PostgreSQL": "postgresql_database",
                    },
                    "edges_with_protocol": {
                        "IOT_Gateway": [{"dst": "PLC", "protocol": "OPC/UA"}],
                        "DigitalTwin": [{"dst": "PostgreSQL", "protocol": "TCP/5432"}],
                    },
                }
            },
            "inventory": {"slots": {"A1": {}, "A2": {}}},
            "workpieces": {"WP1": {}},
        }
    }


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.raw = fixture_snapshot()
        self.adapter = SmartFactorySnapshotAdapter(
            lambda: self.raw,
            AdapterConfiguration(
                runtime_mode="simulation",
                address_manifest={
                    "IOT_Gateway": "198.18.0.10",
                    "PLC": "198.18.0.30",
                    "DigitalTwin": "198.18.0.40",
                    "PostgreSQL": "198.18.0.50",
                },
                stale_after_seconds=60,
            ),
            clock=lambda: datetime(2026, 8, 24, 3, 0, 10, tzinfo=timezone.utc),
        )

    def proposal(self, tool, arguments):
        return ActionProposal(
            action_id="T-1", objective="test", hypothesis="test", tool=tool,
            arguments=arguments, expected_information="test", confidence=0.5,
        )

    def test_capture_is_read_only_and_fingerprinted(self):
        before = copy.deepcopy(self.raw)
        snapshot = self.adapter.capture()
        self.assertEqual(self.raw, before)
        self.assertEqual(snapshot.twin_revision, 12)
        self.assertEqual(snapshot.freshness_seconds, 10.0)
        self.assertFalse(snapshot.quality["stale"])
        self.assertEqual(len(snapshot.fingerprint_sha256), 64)

    def test_host_discovery_uses_declared_manifest(self):
        observation = self.adapter.execute(
            self.proposal("safe_host_discovery", {"cidr": "198.18.0.0/24"}), 1
        )
        self.assertEqual(len(observation.data["live_hosts"]), 4)
        self.assertTrue(observation.evidence["read_only_adapter"])
        self.assertFalse(observation.evidence["physical_contact"])

    def test_service_projection_uses_protocol_edges(self):
        observation = self.adapter.execute(
            self.proposal("safe_service_discovery", {"target": "198.18.0.30"}), 1
        )
        self.assertEqual(observation.data["asset_id"], "PLC")
        self.assertEqual(observation.data["services"], {4840: "opcua"})

    def test_missing_source_timestamp_is_marked_stale(self):
        del self.raw["factory"]["canonical_state"]["captured_at"]
        snapshot = self.adapter.capture()
        self.assertIsNone(snapshot.source_timestamp)
        self.assertTrue(snapshot.quality["stale"])


if __name__ == "__main__":
    unittest.main()
