# Synthetic data: protocol analytics and modelled cyber risk

The folder contains 10,220 synthetic records: 340 attackability rows and 9,880 protocol-log rows. Endpoint, account and session identifiers are pseudonyms. Treat these records as controlled research inputs.

## File guide

| File | Rows | Main research features |
|---|---:|---|
| `ATTACKABLE.csv` | 68 | Directed modelled flow-risk attributes |
| `ATTACKABLE2.csv` | 136 | Alternative synthetic attackability view |
| `ATTACKABLE3.csv` | 136 | Alternative synthetic attackability view |
| `protocol_logs_EtherNet-IP.csv` | 1,000 | CIP service/status and response/volume attributes |
| `protocol_logs_HTTPS.csv` | 1,000 | Request/authentication/status and response attributes |
| `protocol_logs_MQTT.csv` | 400 | Publish/subscribe, QoS, authentication and timing attributes |
| `protocol_logs_MQTTS.csv` | 400 | MQTT activity with TLS-related attributes |
| `protocol_logs_ModbusTCP.csv` | 1,000 | Function, address, quantity, status and response attributes |
| `protocol_logs_OPC_UA.csv.gz` | 4,000 | Message/action/security-mode and audit-related attributes |
| `protocol_logs_RDP.csv` | 720 | Session, authentication, result and response attributes |
| `protocol_logs_S7comm.csv` | 560 | PDU/service, memory-area and response attributes |
| `protocol_logs_SSH.csv` | 800 | Session/authentication, result and response attributes |

## Research supported

| Study | Proposed comparison | Measures |
|---|---|---|
| Protocol-aware security analytics | Per-protocol models versus a shared feature baseline | Feature coverage, stability across protocols, model agreement |
| Synthetic anomaly detection | Threshold/persistence baselines versus learned detectors, using documented injected anomalies | Precision/recall, PR-AUC, false alarms per record or time unit, detection delay |
| Control-sensitive risk modelling | Vary control-strength and attack-cost assumptions in graph experiments | Ranking sensitivity, modelled risk reduction and path-cost changes |
| Cross-protocol representation | Compare generic timing/volume features with protocol-specific fields | Transfer gap and sensitivity to missing fields |

Define anomaly labels and injection rules separately if conducting supervised detection. A failed protocol result, high severity, large volume or high risk weight is not automatically a verified malicious event. Split by scenario/flow where available; random row splits can overstate generalization.

The three attackability files are alternative source views, not guaranteed independent train/test sets. Check overlapping flows and attributes before combining them. Measurements here do not establish real device latency, packet-level fidelity or production intrusion-detection performance.

## Published connection

[P1: BRIDG-ICS](../../docs/RELATED_PUBLICATIONS.md#p1-bridg-ics) is the associated published framework for industrial graph analytics and modelled threat/risk analysis. Source-specific transformations and counts are recorded in [provenance](../../metadata/provenance.csv). Combine with [inventory](../inventory/README.md) and [knowledge_graph](../knowledge_graph/README.md) after validating identifier joins.
