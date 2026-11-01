# Research readiness: implementation and remaining evidence

## Implemented

- `scripts/research_quality.py` builds reproducible quality artifacts from the released source tables.
- `data/training/release_compatible.json` is the preferred restricted-grammar query subset: **66 distinct normalized queries**, derived from **118** legacy records with an accepted query. The original 358 records remain unchanged for provenance. Query-level exclusions and transformations are in `reports/training_compatibility.json`.
- `reports/graph_connectivity.json` and `graph_nodes.csv` describe typed-node incidence, isolated nodes, weak components and relation counts, both with and without synthetic attackability edges.
- `reports/join_coverage.json` and `metadata/asset_graph_crosswalk.csv` establish **94/94** inventory-to-product ID matches and **79/79** flow-endpoint matches. Host IDs are a separate namespace; the earlier host-only comparison was not a valid test of product join coverage. Component joins and unsupported signal/agent joins remain explicit.
- `metadata/trace_manifest.csv` provides counts, duration, event spacing, signal diversity, missingness and short-trace flags for all **27** released traces. `operational_semantics.json` distinguishes observed fields from unknown collection/process/units information.
- The [evaluation suite](../evaluation/README.md) scores all currently declared fixture field names and records context-dependent predicates as unscored when evidence is missing. All 400 cases remain in the denominator.
- A source-linked 94-case connected task includes **33 assets with CVE links** and **86 asset–CVE edges**. Baselines and a separate source-consistency audit run without a model or physical equipment.

## Compatibility scope

The preferred queries use a declared node-label/property mapping in `metadata/graph_import_schema.json`. They support exact identifier lookup and short typed paths. Legacy `HAS_CAPEC` direction is corrected only where endpoint types unambiguously identify the stored direction. Unsupported inferred relations are not invented. Queries requiring removed descriptions/names, missing IDs, unsupported grammar or absent relationships are excluded from the compatible subset, with per-query reasons. New instructions describe only the retained normalized query; they do not promise discarded alternatives.

Reference answers are recomputed against released tables. This is **not** Neo4j server execution or full Cypher syntax certification. A compatible database importer must use the supplied labels and properties. Before claiming engine execution accuracy, import the graph and run Neo4j `EXPLAIN` and read-only result comparisons under a pinned engine version. [Neo4j query plans](https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/execution-plans/).

## Measured structural results

| Measure | Result |
|---|---:|
| Typed graph nodes | 305,167 |
| Declared edge rows | 276,420 |
| Isolated typed nodes | 69,103 |
| Weak components, including isolated nodes | 69,226 |
| Largest weak component | 234,166 nodes |
| Edge rows excluding synthetic attackability | 276,216 |

Removing synthetic attackability edges does not change these connectivity counts in this snapshot. Connectedness is not semantic correctness. The isolated-node background is retained and reported, not silently dropped.

## Not yet established

**Real-model comparisons are not run.** This execution environment has no local inference executable, weights, relevant inference packages or model API credentials. The local Ollama runner is ready for a suitably provisioned machine; results are deliberately empty in `reports/model_comparisons.json`. Deterministic baselines are never relabelled as LLM results.

**Independent expert review is pending.** A 94-case review packet is supplied. Separate source-table implementation checks have passed, but no reviewer has signed off. Physical provenance, signal units, attack labels, technique/target mappings and asset applicability cannot be recovered merely by adding metadata files; missing evidence is labelled unknown.

## Reproduce

```bash
python3 scripts/research_quality.py
python3 evaluation/run_baselines.py
python3 evaluation/audit_connected.py
python3 -m unittest discover -s tests -v
python3 scripts/validate_release.py
```

Regenerating public metadata must not reveal private identifiers or fabricate semantics. If generated files intentionally change, review them and update their checksum entries. The frozen v1.0.0 release remains historical; these improvements are on the main branch until a subsequent release is created.
