# Author research articles and dataset connections

This guide distinguishes **work co-authored by Ahmad Mohsin** from **third-party dataset sources**. CTIBench is by Alam and colleagues; it is not an article by the repository custodian. Its attribution remains necessary because the benchmark folder contains adapted CTIBench records.

## Co-authored research

| Reference | Article or research output | Version/status represented here | Main folder connections |
|---|---|---|---|
| [P1: BRIDG-ICS](#p1-bridg-ics) | Industrial security knowledge graphs and threat analytics | Published in Cybersecurity, 2026 | Inventory, knowledge graph, synthetic data |
| [P2: NeuroGraph](#p2-neurograph) | Graph-grounded neuro-symbolic threat reasoning | Author-linked arXiv version; acceptance in International Journal of Information Security was reported by the author; final journal DOI/details are not asserted here | Knowledge graph, benchmarks, training |
| [P3: Human-AI collaboration with trusted autonomy](#p3-human-ai-collaboration-with-trusted-autonomy) | Human oversight, trust and autonomy in SOCs | ACM Transactions on Internet Technology, 2026 | Related methodology for agent oversight |
| [P4: HySecTwin](#p4-hysectwin) | Semantic digital twins with deterministic/fuzzy security reasoning | Author's repository and linked arXiv version; repository README describes the manuscript as under review | Operational features, inventory, synthetic monitoring experiments |
| [P5: Autonomous cyber-physical security assessment](#p5-autonomous-cyber-physical-security-assessment) | Behavioural digital twin and cooperative agentic security assessment | Author-supplied manuscript; public article URL, journal DOI and publication year are not supplied in this record | Agent scenarios and behavioural/operational research context |

These are distinct article/version records. A linked preprint, repository or supplied manuscript is not automatically a publisher's version of record. The transformed public datasets are not asserted to reproduce every input or result of these articles.

## P1: BRIDG-ICS

Nandiya, P., Mohsin, A., Ibrahim, A., Sarker, I. H., & Janicke, H. (2026). BRIDG-ICS: AI-grounded knowledge graphs for intelligent threat analytics in Industry 5.0 cyber-physical systems. *Cybersecurity, 9*, Article 167. https://doi.org/10.1186/s42400-026-00597-0

Associated published framework for integrated industrial asset/CTI graphs and contextual threat/risk analysis. Relevant folders: [inventory](../data/inventory/README.md), [knowledge_graph](../data/knowledge_graph/README.md) and [synthetic](../data/synthetic/README.md). Release-specific filtering and pseudonymization limit direct reproduction of the full paper experiments.

## P2: NeuroGraph

Nandiya, P., Mohsin, A., Ibrahim, A., Sarker, I. H., & Janicke, H. (2026). *NeuroGraph: An AI graph-driven neuro-symbolic framework for explainable threat reasoning in advanced manufacturing*. arXiv:2609.00604. https://arxiv.org/abs/2609.00604

[Associated G2 source project](https://github.com/ahmadspm/Nuero-RAG-GRAPh-CPS-Intelligence-Modelling)

This is the custodian's co-authored article relevant to graph-grounded query generation, evidence retrieval and explainable CTI reasoning. It belongs in the author's research list. Relevant folders: [knowledge_graph](../data/knowledge_graph/README.md), [benchmarks](../data/benchmarks/README.md) and [training](../data/training/README.md). CTIBench remains the external source of the underlying benchmark tasks; it is not a substitute citation for NeuroGraph's research contribution.

## P3: Human-AI collaboration with trusted autonomy

Mohsin, A., Janicke, H., Ibrahim, A., Sarker, I. H., & Camtepe, S. (2026). A unified framework for human–AI collaboration in security operations centers with trusted autonomy. *ACM Transactions on Internet Technology*. https://doi.org/10.1145/3837073

[Author-deposited version and journal reference](https://arxiv.org/abs/2505.23397)

Related methodology for autonomy, trust and human oversight. Its SOC case study is distinct from the industrial scenario records. Cite it when an experiment uses its oversight/autonomy framework rather than treating it as the source of the G4 fixtures.

## P4: HySecTwin

Holmes, D., Mohsin, A., Nepal, S., Sikos, L., Sarker, I. H., & Janicke, H. (2026). *HySecTwin: A knowledge-driven digital twin framework augmented with hybrid reasoning for cyber-physical systems*. https://arxiv.org/abs/2605.11682

[Author's project repository](https://github.com/ahmadspm/HybridSec-Digital-Twin-CSP-Modelling) · [Reasoning reproducibility package](https://github.com/ahmadspm/HybridSec-Digital-Twin-CSP-Modelling/tree/main/Reproducibility)

The repository supplies semantic modelling, digital-twin artefacts, deterministic rules and fuzzy-reasoning reference material. It is the appropriate author project to link for hybrid reasoning and semantic monitoring. Relevant folders: [operational](../data/operational/README.md), [inventory](../data/inventory/README.md) and [synthetic](../data/synthetic/README.md). This dataset's reduced/pseudonymous traces are not asserted to contain the complete HySecTwin experiment or its original physical-fidelity measurements.

## P5: Autonomous cyber-physical security assessment

Nandiya, P., Mohsin, A., Lohmann, G., Ekelhart, A., Sarker, I. H., & Janicke, H. (n.d.). *Autonomous cyber-physical security assessment in smart manufacturing with a behavioural digital twin and agentic AI*. Author-supplied manuscript.

[Source project identified in the manuscript](https://github.com/ahmadspm/Digital-TwinAutonomous-CPS-Security-Testing) (access depends on the source repository's visibility).

The supplied manuscript describes a behavioural manufacturing twin and cooperative LLM agents, including AOA/ASBIO, for controlled cyber-physical security assessment. Its availability statement identifies the G4 project, which is the source lineage of this collection's [agent scenarios](../data/agent_scenarios/README.md). The 400 released expected-decision cases remain fixtures; their inclusion is not a rerun of the manuscript's model/production-impact experiments. A public full-text URL or publisher DOI should be added when supplied; the uploaded manuscript itself has not been republished here.

## Third-party dataset attribution

### T1: CTIBench — third-party benchmark source

Alam, M. T., Bhusal, D., Nguyen, L., & Rastogi, N. (2024). CTIBench: A benchmark for evaluating LLMs in cyber threat intelligence. *Advances in Neural Information Processing Systems, 37*, 50805–50825. https://doi.org/10.52202/079017-1607

[Official proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5acd3c628aa1819fbf07c39ef73e7285-Abstract-Datasets_and_Benchmarks_Track.html) · [Original dataset](https://huggingface.co/datasets/AI4Sec/cti-bench)

This is **not the custodian's article**. It is retained exclusively as attribution for the adapted CTI-ATE/CTI-RCM data. The [benchmark license](../data/benchmarks/LICENSE) remains CC BY-NC-SA 4.0. Curated counts and transformations differ from the original benchmark.

## Citation practice

Cite this release through `CITATION.cff`, the relevant co-authored research method, and any third-party data source actually used. File-level lineage is in `metadata/provenance.csv`; related article/project mappings are in `metadata/research_file_map.csv`. Proposed studies do not inherit a paper's reported results. Publication/version descriptions above reflect the linked or supplied evidence rather than invented journal metadata.
