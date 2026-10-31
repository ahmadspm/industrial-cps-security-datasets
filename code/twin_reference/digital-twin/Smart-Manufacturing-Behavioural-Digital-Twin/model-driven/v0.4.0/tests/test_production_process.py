from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models/processes/smart-factory-production.bpmn"
NS = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}


class ProductionProcessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = ET.parse(MODEL).getroot()
        self.process = self.root.find("bpmn:process", NS)

    def test_model_is_executable_bpmn(self) -> None:
        self.assertIsNotNone(self.process)
        self.assertEqual(self.process.attrib["isExecutable"], "true")
        self.assertEqual(len(self.process.findall("bpmn:startEvent", NS)), 1)
        self.assertEqual(len(self.process.findall("bpmn:endEvent", NS)), 2)

    def test_all_factory_stations_are_explicit_process_nodes(self) -> None:
        names = " ".join(task.attrib.get("name", "") for task in self.process.findall("bpmn:serviceTask", NS))
        for station in ("DSI", "VGR", "HBW", "MPO", "SLD", "DSO"):
            self.assertIn(station, names)

    def test_rework_is_bounded_and_returns_to_processing(self) -> None:
        properties = {item.attrib["name"] for item in self.process.findall("bpmn:property", NS)}
        self.assertEqual(properties, {"reworkCount", "maxRework"})
        flows = {flow.attrib["id"]: flow for flow in self.process.findall("bpmn:sequenceFlow", NS)}
        condition = flows["Flow_Rework"].find("bpmn:conditionExpression", NS)
        self.assertIn("reworkCount < maxRework", condition.text)
        self.assertEqual(flows["Flow_Reprocess"].attrib["targetRef"], "VGR_To_MPO")
        self.assertEqual(flows["Flow_Reject"].attrib["targetRef"], "EndRejected")

    def test_accepted_route_reaches_completion(self) -> None:
        flows = {flow.attrib["id"]: flow for flow in self.process.findall("bpmn:sequenceFlow", NS)}
        self.assertEqual(flows["Flow_Accepted"].attrib["targetRef"], "VGR_To_DSO")
        self.assertEqual(flows["Flow_11"].attrib["targetRef"], "EndComplete")


if __name__ == "__main__":
    unittest.main()

