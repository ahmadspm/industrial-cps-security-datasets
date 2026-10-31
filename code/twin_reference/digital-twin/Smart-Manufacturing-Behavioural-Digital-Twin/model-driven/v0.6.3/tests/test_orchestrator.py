import asyncio
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))

from orchestrator import Broker, CYCLE, DigitalTwinProjection, EvidenceLedger, WorkspaceRuntime, execute


class WorkspaceRuntimeTests(unittest.TestCase):
    def run_runtime(self):
        runtime = WorkspaceRuntime()
        report = asyncio.run(runtime.run())
        return runtime, report

    def test_complete_cycle_passes_conformance(self):
        _, report = self.run_runtime()
        self.assertTrue(report["passed"])
        self.assertTrue(report["completed"])

    def test_all_nine_production_observations_commit(self):
        runtime, report = self.run_runtime()
        self.assertEqual(report["production_revision"], 9)
        self.assertEqual(len([e for e in runtime.ledger.events if e.operation == "TWIN_COMMIT"]), 9)

    def test_final_station_states_match_semantic_oracle(self):
        _, report = self.run_runtime()
        self.assertEqual(report["final_states"], {station: state for station, state, _, _ in CYCLE})

    def test_each_cycle_step_has_complete_causal_chain(self):
        _, report = self.run_runtime()
        self.assertEqual(report["causal_violations"], [])

    def test_required_operations_are_present(self):
        runtime, _ = self.run_runtime()
        operations = {event.operation for event in runtime.ledger.events}
        self.assertTrue(set(WorkspaceRuntime.REQUIRED_CHAIN) <= operations)

    def test_correlation_id_covers_each_step(self):
        runtime, _ = self.run_runtime()
        ids = {event.correlation_id for event in runtime.ledger.events if event.correlation_id != "bootstrap"}
        self.assertEqual(ids, {f"WP-001:{number:02d}" for number in range(1, 10)})

    def test_digital_twin_remains_read_only(self):
        async def scenario():
            broker = Broker(EvidenceLedger())
            await broker.connect("digital_twin")
            with self.assertRaises(PermissionError):
                await broker.publish("digital_twin", "f/o/order", {}, "negative")
        asyncio.run(scenario())

    def test_unconnected_publisher_is_denied(self):
        async def scenario():
            broker = Broker(EvidenceLedger())
            with self.assertRaises(PermissionError):
                await broker.publish("intruder", "f/i/state/vgr", {}, "negative")
        asyncio.run(scenario())

    def test_sequence_gap_is_reported(self):
        async def scenario():
            ledger = EvidenceLedger()
            twin = DigitalTwinProjection(ledger)
            queue = asyncio.Queue()
            task = asyncio.create_task(twin.consume(queue))
            await queue.put({"topic":"f/i/state/vgr","correlation_id":"gap","payload":{"station":"vgr","state":"pick","cycle_sequence":2}})
            await queue.join()
            await queue.put(None)
            await task
            return twin
        twin = asyncio.run(scenario())
        self.assertEqual(twin.findings[0]["code"], "SEQUENCE_GAP")

    def test_manifest_prohibits_physical_contact_and_wire_claim(self):
        runtime, report = self.run_runtime()
        manifest = runtime.manifest(report)
        self.assertFalse(manifest["physical_contact"])
        self.assertFalse(manifest["physical_writes"])
        self.assertFalse(manifest["wire_protocol_emulation"])

    def test_evidence_export_is_parseable_and_synchronized(self):
        with tempfile.TemporaryDirectory() as directory:
            report = asyncio.run(execute(Path(directory)))
            events = (Path(directory) / "runtime-events.jsonl").read_text().splitlines()
            manifest = json.loads((Path(directory) / "manifest.json").read_text())
            stored = json.loads((Path(directory) / "conformance-report.json").read_text())
            self.assertEqual(len(events), manifest["event_count"])
            self.assertEqual(stored["passed"], report["passed"])
            self.assertEqual(json.loads(events[-1])["sequence"], len(events))

    def test_evidence_hashes_are_reproducible(self):
        first, first_report = self.run_runtime()
        second, second_report = self.run_runtime()
        self.assertEqual(first.manifest(first_report)["event_sha256"], second.manifest(second_report)["event_sha256"])
        self.assertEqual(first.manifest(first_report)["report_sha256"], second.manifest(second_report)["report_sha256"])


if __name__ == "__main__":
    unittest.main()
