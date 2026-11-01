# Industrial CPS Security Research Datasets

[![Dataset version](assets/badges/dataset-version.svg)](CHANGELOG.md)
[![Dataset validation](https://github.com/ahmadspm/industrial-cps-security-datasets/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/ahmadspm/industrial-cps-security-datasets/actions/workflows/validate.yml)
[![Cite this dataset](assets/badges/citation.svg)](CITATION.cff)
[![License scopes](assets/badges/licenses.svg)](metadata/licenses.csv)
[![Research articles](assets/badges/research.svg)](docs/RELATED_PUBLICATIONS.md)

A curated research collection for industrial cybersecurity graphs, synthetic protocol analysis, de-identified operational event analysis and offline digital-twin/agent evaluation. Public views are derived from private source inputs. Raw operational logs, account/credential tables, screenshots, private identifiers and the source repository's earlier history are not part of this release.

| Directory | Contents | Evidence class |
|---|---|---|
| `data/inventory` | De-identified asset, zone and data-flow attributes | Inventory, not measured security effectiveness |
| `data/knowledge_graph` | 305,167 nodes and 276,420 typed-reference-checked edges | Source-derived factual attributes; semantic correctness not certified |
| `data/synthetic` | 10,220 synthetic protocol/attackability records | Synthetic, not physical attack ground truth |
| `data/benchmarks` | 60 CTI-ATE, 996 CTI-RCM and 991 CTI-RCM-2021 records | Upstream reference labels; 13 ambiguous records excluded |
| `data/training` | 358 legacy pairs; 66 normalized release-compatible queries | Training/reference material, not held-out evaluation |
| `data/operational` | 14,124 reduced event-feature records from 27 traces | De-identified observations; no physical-fidelity certification |
| `data/agent_scenarios` | 400 expected-decision test cases in 20 scenarios | Expected decisions, not 400 newly executed agent outcomes |
| `code/twin_reference` | Models, configurations, fixtures and tests needed for offline replay | Derived reference implementation |

## Research readiness and evaluation

See the [implementation and evidence status](docs/RESEARCH_READINESS.md) for the release-compatible query subset, graph connectivity and join coverage, trace metadata, complete fixture-field evaluator and connected evidence task. [Evaluation instructions](evaluation/README.md) include a local real-model comparison runner and an independent-review packet. **Real-model execution and independent expert sign-off remain pending.**

## Research guide

Read **Critical Infrastructure Cybersecurity Research: Digital Twins, AI and Knowledge Graphs**, by Dr Ahmad Mohsin (Research Fellow / Scientist), in the **[Researcher’s Guide (PDF)](RESEARCHERS_GUIDE.pdf)** for a 31-page academic guide with fourteen figures, including twelve redesigned image-generated scientific diagrams, potential research areas and problems, dataset suitability and evidence gaps, recent AI/OT security challenges, three opening pages illustrating CPS, critical infrastructure, digital twins and governed agentic AI, study protocols, loading examples and reproducibility guidance.

See the [data research guide](data/README.md) for the cybersecurity studies supported by each folder, file-level research roles, suggested evaluation measures and links to [co-authored articles and third-party sources](docs/RELATED_PUBLICATIONS.md). Each of the seven dataset folders has its own README.

Editable [source and build instructions](docs/guide/README.md) are included.

## Research lineage

This research programme began in **2023** with the [shift-left/shift-right security digital-twin work](https://doi.org/10.1109/TPS-ISA58951.2023.00042), followed by the [AI/XAI review](https://doi.org/10.1016/j.icte.2024.05.007) and the [security/privacy chapter](https://doi.org/10.1016/B978-0-443-43896-7.00016-9). Later work develops graph-grounded and LLM-enabled security reasoning, trusted autonomy and sector-specific virtual-twin applications. The guide explains these connections and their evaluation implications. This is the history of the research programme; individual released records are not all asserted to originate in 2023.

## Related research

| Reference | Publication / Version | Article Title | Research Themes |
|---|---|---|---|
| [P1: BRIDG-ICS](docs/RELATED_PUBLICATIONS.md#p1-bridg-ics) | Cybersecurity, 2026 | [BRIDG-ICS: AI-grounded knowledge graphs for intelligent threat analytics in Industry 5.0 cyber-physical systems](https://doi.org/10.1186/s42400-026-00597-0) | Knowledge graphs; threat analytics; cyber-risk modelling |
| [P2: NeuroGraph](docs/RELATED_PUBLICATIONS.md#p2-neurograph) | Author-reported acceptance in International Journal of Information Security; linked arXiv version | [NeuroGraph: An AI Graph-Driven Neuro-Symbolic Framework for Explainable Threat Reasoning in Advanced Manufacturing](https://arxiv.org/abs/2609.00604) | Neuro-symbolic AI; Graph-RAG; evidence-grounded threat reasoning; explainability |
| [P3: Trusted autonomy](docs/RELATED_PUBLICATIONS.md#p3-human-ai-collaboration-with-trusted-autonomy) | ACM Transactions on Internet Technology, 2026 | [A Unified Framework for Human–AI Collaboration in Security Operations Centers with Trusted Autonomy](https://doi.org/10.1145/3837073) | Human-AI collaboration; trust calibration; autonomy; security operations |
| [P4: HySecTwin](docs/RELATED_PUBLICATIONS.md#p4-hysectwin) | Linked arXiv version and author project; journal metadata not supplied | [HySecTwin: A Knowledge-Driven Digital Twin Framework Augmented with Hybrid Reasoning for Cyber-Physical Systems](https://arxiv.org/abs/2605.11682) | Semantic digital twins; hybrid reasoning; fuzzy inference; CPS security monitoring |
| [P5: Autonomous assessment](docs/RELATED_PUBLICATIONS.md#p5-autonomous-cyber-physical-security-assessment) | Research manuscript | [Autonomous Cyber-Physical Security Assessment in Smart Manufacturing with a Behavioural Digital Twin and Agentic AI](docs/RELATED_PUBLICATIONS.md#p5-autonomous-cyber-physical-security-assessment) | Behavioural digital twins; cooperative agents; autonomous security assessment; manufacturing resilience |
| [P6: Lifecycle foundations](docs/RELATED_PUBLICATIONS.md#p6-shift-left-and-shift-right-foundations) | IEEE TPS-ISA, 2023 | [Digital Twins and the Future of Their Use Enabling Shift Left and Shift Right Cybersecurity Operations](https://doi.org/10.1109/TPS-ISA58951.2023.00042) | Security digital twins; shift-left/shift-right; design-time and runtime security |
| [P7: AI/XAI review](docs/RELATED_PUBLICATIONS.md#p7-ai-and-explainable-ai-review) | ICT Express, 2024 | [Explainable AI for cybersecurity automation, intelligence and trustworthiness in digital twin: Methods, taxonomy, challenges and prospects](https://doi.org/10.1016/j.icte.2024.05.007) | Explainable AI; security analytics; automation; trustworthiness |
| [P8: Security and privacy](docs/RELATED_PUBLICATIONS.md#p8-digital-twin-security-and-privacy) | Foundations of Digital Twins, 2026 | [Security risks and privacy challenges in digital twins](https://doi.org/10.1016/B978-0-443-43896-7.00016-9) | Lifecycle security; privacy engineering; secure architecture; governance |
| [P9: Railway virtual twin](docs/RELATED_PUBLICATIONS.md#p9-railway-virtual-twin) | KES 2026 | [A Secure-by-Design Virtual Twin Framework for AI-Driven Threat Modeling in Railway OT Systems](https://www.researchgate.net/publication/414633139_A_Secure-by-Design_Virtual_Twin_Framework_for_AI-Driven_Threat_Modeling_in_Railway_OT_Systems) | Secure-by-design; virtual twins; AI-assisted threat modelling; railway OT |

The titles link to the article or its documented manuscript record. Research themes describe the scholarly focus; publication/version details remain explicit. [Article records and project links](docs/RELATED_PUBLICATIONS.md) · [BibTeX references](docs/references.bib). CTIBench is listed separately as a third-party data source, with its original attribution and license retained.

## Research protocols and reproducibility

Use the [research question–dataset matrix](docs/RESEARCH_QUESTIONS.md) to select inputs, methods and metrics. The [three runnable starter experiments](examples/README.md) include fixed group partitions and measured baselines for event rarity, graph mapping and expected agent decisions. The [archiving guide](docs/ARCHIVING.md) explains versioned citation and the remaining Zenodo DOI activation step.

## Quick start

Use Python 3.11 or later. Validation requires only the standard library:

```bash
python3 scripts/validate_release.py
```

CSV and JSONL files ending in `.gz` are ordinary gzip-compressed files. Each CVE shard has its own header; read all `cve_node_*.csv.gz` files as one logical node table.

```python
import csv, gzip
with gzip.open('data/operational/event_features.jsonl.gz', 'rt') as stream:
    first_event = next(stream)
print(first_event)
```

For offline replay, install `code/requirements-replay.txt` into an isolated Python environment, then run:

```bash
python3 scripts/replay_offline.py --source-root . --output replay_output
```

The replay script runs unit suites and deterministic fixture experiments. It does not start deployment services or require live model weights, Neo4j, or physical equipment.

## What changed for release

- Direct network, account, location and session identifiers are omitted or pseudonymized. Operational timestamps are relative; uncontrolled text values are pseudonyms.
- Synthetic endpoints are pseudonyms. Reference-code network examples use reserved benchmarking addresses, preserving the example subnet relationships.
- Unmatched graph edges are excluded rather than repaired with invented nodes. CAPEC nodes are ID-only where source attributes conflicted.
- Thirteen benchmark records across five ambiguous description/label groups are excluded. Related records have group identifiers for future split assignment.
- 129 exact duplicate training records are removed. No historical train/test partition is invented.
- The graph view omits narrative descriptions, reference URLs, account/credential tables and inferred tactic labels. Keep source attribution when reusing derived CTI facts.

Read [the dataset card](docs/DATASET_CARD.md), [schemas](docs/SCHEMAS.md), [methods and exclusions](docs/METHODS.md) and [validation report](docs/VALIDATION.md) before reuse.

## Citation

Use GitHub's **Cite this repository** option, the [CITATION.cff](CITATION.cff) metadata, or the dataset entry below. Cite the relevant research articles and external data sources used in your experiment; [BibTeX references](docs/references.bib) are provided for convenience.

```bibtex
@misc{mohsin2026industrialcpsdatasets,
  author       = {Mohsin, Ahmad},
  title        = {Industrial CPS Security Research Datasets: Curated Public Views},
  year         = {2026},
  version      = {1.0.0},
  howpublished = {GitHub dataset repository},
  url          = {https://github.com/ahmadspm/industrial-cps-security-datasets}
}
```

## Terms and attribution

Use `CITATION.cff` and cite relevant upstream sources listed in `metadata/sources.csv`. Original collection material is offered under CC BY 4.0 and project code under MIT. **The CTIBench-derived benchmark directory uses CC BY-NC-SA 4.0**, including non-commercial and share-alike conditions. Other source-derived third-party elements retain their original terms. See `LICENSE`, `LICENSE-CODE`, `data/benchmarks/LICENSE` and `THIRD_PARTY_NOTICES.md`. No third-party endorsement is implied. No DOI has been assigned.
