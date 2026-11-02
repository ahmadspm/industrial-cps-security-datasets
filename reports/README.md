# Reproducible research-quality reports

| Report | Meaning |
|---|---|
| `training_compatibility.json` | Source-record and query exclusions, normalized subset scope and legacy hash |
| `graph_connectivity.json`, `graph_nodes.csv` | Typed-node incidence, isolation, weak components and relation-row counts |
| `join_coverage.json` | Exact-key coverage for specified joins, plus unsupported mappings |
| `agent_predicate_coverage.json` | Every expected-field scope, its occurrences and missing-output/context treatment |
| `evaluation_baselines.json` | Executed deterministic comparators; **not real-model results** |
| `connected_task.json` | Connected-task size and evidence limits |
| `connected_source_audit.json` | Second-implementation source consistency checks; **not human review** |

Rebuild quality reports with `scripts/research_quality.py`, then run `evaluation/run_baselines.py` and `evaluation/audit_connected.py`. Read [research methods](../docs/RESEARCH_METHODS.md) for analytical scope and [evaluation instructions](../evaluation/README.md) for genuine model runs and independent review.
