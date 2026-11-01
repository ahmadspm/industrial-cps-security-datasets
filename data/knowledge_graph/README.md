# Knowledge graph: contextual cybersecurity reasoning

This folder contains 305,167 released nodes and 276,420 edges whose declared endpoints pass the supplied typed-reference checks. The public projection retains identifiers, selected attributes and historical scores while omitting raw accounts, credentials, narrative descriptions and uncertain references.

## File groups

| Files | Research role |
|---|---|
| `cve_node_*.csv.gz`, `cwe_node.csv`, `capec_node.csv` and `HAS_CWE*`, `HAS_CAPEC.csv` | Vulnerability, weakness and attack-pattern associations; weakness-mapping and graph-completion studies |
| `technique_node.csv`, `tactic_node.csv`, `group_node.csv`, `malware_node.csv`, `BELONG_TO.csv`, `USE_TECHNIQUE.csv`, `USE_MALWARE.csv` | Adversarial-behaviour context and technique/tactic association analysis |
| `mitigation_node.csv`, `MITIGATES.csv`, `cweMitigation_node.csv`, `cweDetection_node.csv`, consequence/mode nodes and their `HAS_*` edges | Mitigation, detection and consequence reasoning |
| `product_node.csv`, host/machine/component/software/zone/protocol nodes, `RUNS.csv`, `HAS_COMPONENT.csv`, `LOCATED_IN.csv`, `USES_PROTOCOL.csv` | Industrial dependency and asset-context modelling |
| `COMMUNICATES_WITH.csv`, `HAS_VULNERABILITY*`, `ATTACKABLE*.csv` | Communication-aware exposure, modelled attack paths and synthetic edge-risk comparisons |
| Sensor/actuator/process-variable/event/alert nodes and `MEASURES.csv` | Modelled observation context; potential security-state correlation research |
| `IS_CHILD_OF.csv`, `IS_PEER_OF.csv`, `CAN_ALSO_BE.csv`, `CAN_PRECEDE.csv`, `REQUIRES.csv`, `STARTS_WITH.csv` | Weakness-taxonomy structure and dependency analysis |

The [file-level map](../../metadata/research_file_map.csv) provides an entry for each table/shard. Read the CVE shards as one logical node table. [Node primary keys](../../metadata/graph_node_keys.json) and [typed edge rules](../../metadata/graph_relation_rules.json) define the released graph structure.

## Research supported

| Study | Comparison or method | Measures |
|---|---|---|
| Contextual vulnerability prioritization | Score-only baselines versus asset/communication-aware ranking | Top-k agreement, ranking sensitivity, critical-asset coverage |
| Modelled attack-path and mitigation analysis | Unweighted versus attribute-weighted paths; explicit counterfactual control assumptions | Path cost/length, reachable critical nodes, modelled risk change |
| Graph completion | Rule-based, similarity and graph-learning models on held-out associations | Precision@k, recall@k, MRR, Hits@k |
| Graph-RAG evidence grounding | Retrieval with graph neighbourhoods versus text-only or entity-only retrieval | Evidence relevance, citation validity, task accuracy and unsupported-claim rate |
| Explainable security recommendations | Trace each proposed mitigation back to declared node/edge evidence | Evidence coverage, explanation consistency and reviewer agreement |

Remove target and derived/inverse target relations from training views when testing link prediction. Split by relevant entities or source versions where possible. The public graph omits narrative descriptions, so text/embedding experiments need an explicitly sourced, separately licensed corpus.

## Published connection and limits

[P1: BRIDG-ICS](../../docs/RELATED_PUBLICATIONS.md#p1-bridg-ics) provides the associated industrial graph/threat-analysis framework. [P2: NeuroGraph](../../docs/RELATED_PUBLICATIONS.md#p2-neurograph) is the custodian's co-authored work on graph-grounded query generation, retrieval and explainable threat reasoning. [T1: CTIBench](../../docs/RELATED_PUBLICATIONS.md#t1-ctibench--third-party-benchmark-source) is a separate third-party evaluation source, not an article by the custodian.

Endpoint validity establishes structural membership, not the truth of a vulnerability, inferred exploit or mitigation effect. Historical CVSS/EPSS/KEV attributes require updating before operational use. Synthetic `ATTACKABLE` values remain modelling inputs. This graph is not a packet capture or a set of verified compromises.

## Connectivity and verified joins

See [connectivity](../../reports/graph_connectivity.json), [per-type node incidence](../../reports/graph_nodes.csv) and [join coverage](../../reports/join_coverage.json). All 94 inventory assets match graph **product** identifiers; host nodes use another namespace. The [crosswalk](../../metadata/asset_graph_crosswalk.csv) records the supported join. Disconnected nodes are retained as declared background; a zero unmatched-edge count is not a claim of full connectivity or semantic validation. The [connected task](../../evaluation/README.md) demonstrates source-backed retrieval with abstention.
