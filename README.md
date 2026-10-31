# Industrial CPS Security Research Datasets

A curated research collection for industrial cybersecurity graphs, synthetic protocol analysis, de-identified operational event analysis and offline digital-twin/agent evaluation.

**Release v1.0.0 — 1 November 2026.** Public views are derived from private source inputs. Raw operational logs, account/credential tables, screenshots, private identifiers and the source repository's earlier history are not part of this release.

| Directory | Contents | Evidence class |
|---|---|---|
| `data/inventory` | De-identified asset, zone and data-flow attributes | Inventory, not measured security effectiveness |
| `data/knowledge_graph` | 305,167 nodes and 276,420 typed-reference-checked edges | Source-derived factual attributes; semantic correctness not certified |
| `data/synthetic` | 10,220 synthetic protocol/attackability records | Synthetic, not physical attack ground truth |
| `data/benchmarks` | 60 CTI-ATE, 996 CTI-RCM and 991 CTI-RCM-2021 records | Upstream reference labels; 13 ambiguous records excluded |
| `data/training` | 358 unique instruction/output records | Training material, not held-out evaluation |
| `data/operational` | 14,124 reduced event-feature records from 29 traces | De-identified observations; no physical-fidelity certification |
| `data/agent_scenarios` | 400 expected-decision test cases in 20 scenarios | Expected decisions, not 400 newly executed agent outcomes |
| `code/twin_reference` | Models, configurations, fixtures and tests needed for offline replay | Derived reference implementation |

## Research guide

See the [data research guide](data/README.md) for the cybersecurity studies supported by each folder, file-level research roles, suggested evaluation measures and links to [co-authored articles and third-party sources](docs/RELATED_PUBLICATIONS.md). Each of the seven dataset folders has its own README.

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

## Citation and terms

Use `CITATION.cff` and cite relevant upstream sources listed in `metadata/sources.csv`. Original collection material is offered under CC BY 4.0 and project code under MIT. **The CTIBench-derived benchmark directory uses CC BY-NC-SA 4.0**, including non-commercial and share-alike conditions. Other source-derived third-party elements retain their original terms. See `LICENSE`, `LICENSE-CODE`, `data/benchmarks/LICENSE` and `THIRD_PARTY_NOTICES.md`. No third-party endorsement is implied. No DOI has been assigned.
