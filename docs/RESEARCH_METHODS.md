# Research methods and data interpretation

## Data and analytical tools

- `scripts/research_quality.py` builds reproducible quality artifacts from the released source tables.
- `data/training/release_compatible.json` is the preferred restricted-grammar query subset: **66 distinct normalized queries**, derived from **118** legacy records with an accepted query. The original 358 records remain unchanged for provenance. Query-level exclusions and transformations are in `reports/training_compatibility.json`.
- `reports/graph_connectivity.json` and `graph_nodes.csv` describe typed-node incidence, isolated nodes, weak components and relation counts, both with and without synthetic attackability edges.
- `reports/join_coverage.json` and `metadata/asset_graph_crosswalk.csv` establish **94/94** inventory-to-product ID matches and **79/79** flow-endpoint matches. Host IDs are a separate namespace. Component joins and unsupported signal/agent joins remain explicit.
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

## Research design and dataset selection

1. **Define the claim and the unit of analysis.** Use an asset for evidence retrieval, a benchmark item for CTI classification, a complete trace for operational studies, and a scenario family for agent comparisons. State whether your outcome measures source agreement, expert judgment, simulated behavior, or physical observations.
2. **Select files through the [dataset metadata catalog](../metadata/dataset_catalog.csv).** Record the repository commit, file paths, record units, evidence class, and license. Check provenance and interpretation limits before combining files. Count shared graph/synthetic tables once in pooled totals, and keep derived queries with their legacy source group.
3. **Verify joins and define the eligible population.** Use the released asset-to-product crosswalk. Keep assets with no source-linked CVEs in the denominator if evaluating abstention. Treat host IDs separately. Establish and document a new crosswalk before associating trace signals or agent targets with physical equipment.
4. **Freeze splits and baselines before tuning.** Hold out entire traces, scenario families, source groups, or environments according to the claim. Keep upstream benchmark duplicates, near-duplicates, and graph target edges out of training or retrieval context where they would reveal the answer. Fit pre-processing and thresholds on development data.
5. **Report uncertainty and failure modes.** Report counts and denominators, missing predictions, coverage, and per-group results. Use group-level intervals where sample size permits. Archive splits, settings, model versions, predictions, and scoring outputs.

For a task-by-task plan, see the [research problems, AI methods, and digital-twin applications](RESEARCH_APPLICATIONS.md) and the [evaluation suite](../evaluation/README.md).

## Developing and validating a digital twin

Begin with a declared purpose, such as behavior replay, observation-quality monitoring, or evaluation of a defensive approval policy. Use inventory and flow tables for an asset and communication view, then use the native models for examples of process dynamics, controller behavior, and state transitions. The knowledge graph can supply sourced cybersecurity context. Keep model state, observed data, and inferred assessments distinct in the interface and exports.

For a twin of a specific testbed, record stable equipment IDs, station and signal mappings, units, timestamp alignment, sampling assumptions, and the applicable configuration. Calibrate with mapped observations and validate on independent runs. Report timing error, state agreement, and any gaps in coverage. Until those checks are complete, use operational files for trace-level studies and the illustrative models for simulated behavior. [Native model examples](../examples/digital_twins/README.md)

## Reproduce

```bash
python3 scripts/research_quality.py
python3 evaluation/run_baselines.py
python3 evaluation/audit_connected.py
python3 -m unittest discover -s tests -v
python3 scripts/validate_release.py
```

