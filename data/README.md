# Cybersecurity research guide

This directory organizes the release by the role each dataset plays in cybersecurity research. The studies below are supported research directions; they are not claims that every proposed experiment has already been conducted.

| Folder | Data and research purpose | Example research question | Published reading |
|---|---|---|---|
| [inventory](inventory/README.md) | Assets, zones, conduits and communication dependencies; attack-surface and segmentation analysis | Which assets or conduits create the largest exposure between process and enterprise zones? | [P1](../docs/RELATED_PUBLICATIONS.md#p1-bridg-ics) |
| [knowledge_graph](knowledge_graph/README.md) | Typed CTI and industrial graph; vulnerability prioritization, attack-path reasoning and graph completion | Does asset context change vulnerability or mitigation priorities compared with score-only ranking? | [P1: BRIDG-ICS](../docs/RELATED_PUBLICATIONS.md#p1-bridg-ics), [P2: NeuroGraph](../docs/RELATED_PUBLICATIONS.md#p2-neurograph) |
| [synthetic](synthetic/README.md) | Synthetic protocol activity and attackability attributes; controlled security-analytics experiments | How do protocol features and assumed controls affect an analytical risk score? | [P1](../docs/RELATED_PUBLICATIONS.md#p1-bridg-ics) |
| [benchmarks](benchmarks/README.md) | Curated CTI task/reference-label pairs; LLM, RAG and Graph-RAG evaluation | Does retrieval improve technique extraction or weakness mapping against the supplied references? | [P2: NeuroGraph](../docs/RELATED_PUBLICATIONS.md#p2-neurograph); [T1: external CTIBench source](../docs/RELATED_PUBLICATIONS.md#t1-ctibench--third-party-benchmark-source) |
| [training](training/README.md) | Deduplicated instruction/output pairs; cybersecurity query-generation and model-adaptation research | Can a small adapted model generate schema-valid, evidence-supported graph queries? | [P2: NeuroGraph](../docs/RELATED_PUBLICATIONS.md#p2-neurograph), [P1: BRIDG-ICS](../docs/RELATED_PUBLICATIONS.md#p1-bridg-ics) |
| [operational](operational/README.md) | Reduced event features; process-aware anomaly analysis and monitoring research | Can temporal consistency checks identify unusual signal transitions while controlling false alarms? | [P4: HySecTwin](../docs/RELATED_PUBLICATIONS.md#p4-hysectwin), as related semantic-monitoring methodology |
| [agent_scenarios](agent_scenarios/README.md) | Expected-decision fixtures; agent planning, policy compliance and trusted-autonomy evaluation | Does an agent respect tool availability, risk limits, termination conditions and evidence requirements? | [P5: behavioural DT and agentic AI](../docs/RELATED_PUBLICATIONS.md#p5-autonomous-cyber-physical-security-assessment); [P3: trusted autonomy](../docs/RELATED_PUBLICATIONS.md#p3-human-ai-collaboration-with-trusted-autonomy) |

Each folder README gives a file guide, proposed studies, evaluation measures and the data's evidence boundaries. [The file-level research map](../metadata/research_file_map.csv) assigns every released data file a research role. [Co-authored articles, manuscripts and third-party sources](../docs/RELATED_PUBLICATIONS.md) separates the custodian's research contributions from external dataset attribution, with the status of each linked version stated explicitly.

## Combining the folders

1. Use inventory tables to define the assets, zones and communication boundary of a study.
2. Add graph context to investigate vulnerability dependencies and candidate mitigation priorities.
3. Use synthetic records for controlled analytical comparisons; use operational features for observation-based temporal analysis.
4. Use training data to develop a method, and separate reference benchmarks to evaluate its CTI outputs.
5. Use agent scenarios to test decision and policy behaviour before considering any separately authorized system deployment.

Validate identifier joins between folders rather than assuming that every source uses the same asset namespace. Keep related descriptions, instructions, graph entities and traces together when constructing train/test splits. See [benchmark split groups](../metadata/benchmark_split_groups.csv).

## Evidence and reuse

Synthetic risk attributes, upstream reference labels, operational observations and expected agent decisions have different meanings. Report the evidence class used in each experiment. Intrusion detection requires verified attack labels or separately documented injected scenarios; this release does not provide a universal malicious/benign label for all records. Physical fidelity and live model performance require their own experiments.

Start with [schemas](../docs/SCHEMAS.md), [the dataset card](../docs/DATASET_CARD.md), [methods](../docs/METHODS.md) and [validation](../docs/VALIDATION.md). The CTIBench-derived folder retains [CC BY-NC-SA 4.0](benchmarks/LICENSE); other scopes are listed in [the license map](../metadata/licenses.csv).
