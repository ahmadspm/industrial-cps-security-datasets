# Operational features: temporal monitoring and process-aware security

`event_features.jsonl.gz` contains **14,124 reduced event-feature records from 29 traces**. Each row has `trace_id`, `record_index`, `relative_seconds`, `event_class`, `signal_id`, `value`, `previous_value` and `ok`.

Numeric/boolean observations and lists are retained. String states and signal/event identities are stable pseudonyms; raw paths, URLs, names, addresses and absolute timestamps are omitted.

## Research supported

| Study | Proposed approach | Measures |
|---|---|---|
| Process-aware anomaly detection | Compare transition constraints and persistence rules with unsupervised sequence/residual methods | Alarm rate, transition violations and detection delay on separately verified or injected events |
| Temporal consistency and data quality | Check ordering, repeated values, missing observations and irregular intervals within each trace | Duplicate/order violations, interval distributions and missing-value rates |
| Observation-driven state modelling | Learn candidate transition graphs from pseudonymous signal/state sequences | Transition coverage, reconstruction error and held-out sequence likelihood |
| Monitoring under impaired observations | Inject documented delay, loss or duplication into controlled copies | Degradation in state estimation, alarm stability and recovery delay |

Split whole traces or coherent sessions rather than random rows. Establish sampling assumptions before resampling. String pseudonyms preserve equality, not textual meaning; source signal units and full process semantics cannot be inferred from the token names.

These are observation-derived features, not a complete packet capture, a labelled attack corpus or certified physical ground truth. `ok` is an available source boolean, not a universal malicious/benign label. Anomaly observations alone do not prove a cyberattack, and supervised attack-detection claims require separately verified event labels.

## Connection to the author's research

[P4: HySecTwin](../../docs/RELATED_PUBLICATIONS.md#p4-hysectwin) is the custodian's co-authored semantic digital-twin/hybrid-reasoning project. Its [repository](https://github.com/ahmadspm/HybridSec-Digital-Twin-CSP-Modelling) and [reasoning reproducibility package](https://github.com/ahmadspm/HybridSec-Digital-Twin-CSP-Modelling/tree/main/Reproducibility) are relevant to deterministic/fuzzy monitoring and contextual security reasoning.

The 29 reduced traces here are not asserted to reproduce the complete HySecTwin experiments or original physical-to-twin latency measurements. Semantic rule replay would require an appropriate, separately supplied signal/ontology mapping; pseudonymous tokens alone do not recover equipment semantics. [P1: BRIDG-ICS](../../docs/RELATED_PUBLICATIONS.md#p1-bridg-ics) provides complementary industrial threat-modelling context. See the [dataset card](../../docs/DATASET_CARD.md) and [provenance register](../../metadata/provenance.csv).
