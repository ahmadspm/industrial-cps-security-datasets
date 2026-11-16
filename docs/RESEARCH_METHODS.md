# Research methods and data interpretation

## Purpose of research and scientific methods

Research methods are the documented procedures used to collect, produce, and analyze evidence. Scientific inquiry connects a well-defined question to a study design, observations or experiments, and conclusions that can be scrutinized and revised. Methodology explains why the chosen procedures are appropriate for the question. Depending on the claim, a study may use controlled experiments, observational analysis, simulation, formal verification, or qualitative inquiry. [1]

Methods matter because the design determines what the evidence can establish. A baseline shows what the proposed method adds. An independent test set helps estimate how it performs on unfamiliar cases. Documented data, software, parameters, and analysis allow another researcher to reproduce a computation. Replication tests whether a finding holds using new evidence. Reporting uncertainty, alternative explanations, and failure cases helps readers judge how far the results apply. [1]

### Higher degree by research training

For PhD and master's by research candidates, methods connect the thesis question to its contribution. At proposal stage, candidates justify the design, evidence requirements, and feasibility. During the study, they document data sources, decisions, and changes to the protocol. In the thesis, they explain how the results answer the question and where the evidence is limited. A master's by research project can apply these principles to a focused question within a defined scope. A PhD uses them to substantiate a significant original contribution. [2, 3]

## Why datasets matter for smart systems research

Smart systems combine Internet of Things (IoT) devices, cyber-physical systems (CPS), communications, and intelligent components. A single observation may reflect a sensor measurement, a controller decision, a network delay, or a change in the physical process. Asset inventories, communication records, event traces, reference labels, and models provide complementary evidence. Their provenance, timing, coverage, and links to the physical system determine which research problems they can address. Use the [dataset metadata catalog](../metadata/dataset_catalog.csv) to identify suitable files and check their evidence class.

| Research application | Role of the dataset | Evaluation considerations |
|---|---|---|
| Machine learning and system modeling | Train classifiers, learn event patterns, calibrate process models, or establish benchmarks. | Hold out independent traces or groups and compare with simple baselines. Check that labels and units support the intended prediction. |
| Large language model augmentation | Retrieve relevant records from a knowledge graph or document index so an LLM can produce traceable answers. Use labeled pairs for supervised adaptation where appropriate. | Score retrieval and answer quality separately. Check citations, unsupported assertions, and appropriate abstention. |
| Agentic AI | Provide read-only evidence and expected-decision fixtures for evaluating whether an agent requests review, respects approval requirements, or stops under uncertainty. | Report decision agreement and policy violations by scenario family. Use independently reviewed cases for broader claims. |
| Digital twins | Use asset and flow records to describe the system, native models to represent behavior, and mapped observations to calibrate and validate the twin. | Verify equipment identity, units, and time alignment. Compare simulated and observed behavior on independent runs. [5] |

### Cybersecurity, safety, and critical infrastructure

In water, energy, transport, and manufacturing, a cyber incident or an incorrect automated decision can affect both service continuity and physical safety. Dataset-based research can examine asset exposure, telemetry quality, anomaly detection, advisory decisions, and recovery. Evaluate cybersecurity outcomes such as evidence accuracy and false alarms alongside process outcomes such as constraint violations, service interruption, and recovery time, where the study has appropriate measurements. Simulation and offline replay support controlled comparisons. Claims about a specific operational environment require representative observations and independent validation under declared operating conditions. [4–6]

## References for research design and application

1. National Academies of Sciences, Engineering, and Medicine (2019). [*Reproducibility and Replicability in Science*](https://www.nationalacademies.org/read/25303).
2. Australian Qualifications Framework. [*AQF Qualifications*](https://www.aqf.edu.au/framework/aqf-qualifications).
3. Tertiary Education Quality and Standards Agency (2025). [*Guidance Note: Research and Research Training*](https://www.teqsa.gov.au/sites/default/files/2025-01/guidance-note-research-and-research-training.pdf).
4. NIST (2023). [*Artificial Intelligence Risk Management Framework (AI RMF 1.0)*](https://doi.org/10.6028/NIST.AI.100-1).
5. NIST (2025). [*Security and Trust Considerations for Digital Twin Technology*](https://doi.org/10.6028/NIST.IR.8356).
6. NIST (2023). [*Guide to Operational Technology (OT) Security*, SP 800-82 Rev. 3](https://csrc.nist.gov/pubs/sp/800/82/r3/final).

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

