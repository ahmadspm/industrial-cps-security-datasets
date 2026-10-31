# Published research and dataset connections

Publication links were checked on 1 November 2026. The table distinguishes source/framework connections from suggested methodological reuse. A related paper does not establish that the public, transformed release is the exact input used in its experiments.

| Reference | Published venue | Connection to this collection |
|---|---|---|
| [P1: BRIDG-ICS](#p1-bridg-ics) | Cybersecurity, 2026 | Associated industrial graph/threat-analysis framework; relevant to inventory, graph and synthetic-data studies |
| [P2: CTIBench](#p2-ctibench) | NeurIPS 2024, Datasets and Benchmarks Track | Published source of the underlying CTI benchmark tasks; this release supplies explicitly modified views |
| [P3: Human–AI collaboration with trusted autonomy](#p3-human-ai-collaboration-with-trusted-autonomy) | ACM Transactions on Internet Technology, 2026 | Related methodology for agent oversight and trusted autonomy; not the source of the G4 scenario records |

## P1: BRIDG-ICS

Nandiya, P., Mohsin, A., Ibrahim, A., Sarker, I. H., & Janicke, H. (2026). BRIDG-ICS: AI-grounded knowledge graphs for intelligent threat analytics in Industry 5.0 cyber-physical systems. *Cybersecurity, 9*, Article 167. https://doi.org/10.1186/s42400-026-00597-0

The published framework connects industrial assets and CTI for contextual threat/risk analysis. It motivates the associated graph, inventory and synthetic analytical studies. Release-specific filtering, pseudonymization and omitted graph narratives limit direct reproduction of the paper's full experiments.

## P2: CTIBench

Alam, M. T., Bhusal, D., Nguyen, L., & Rastogi, N. (2024). CTIBench: A benchmark for evaluating LLMs in cyber threat intelligence. *Advances in Neural Information Processing Systems, 37*, 50805–50825. https://doi.org/10.52202/079017-1607

[Official proceedings page](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5acd3c628aa1819fbf07c39ef73e7285-Abstract-Datasets_and_Benchmarks_Track.html) · [Original dataset](https://huggingface.co/datasets/AI4Sec/cti-bench)

This release adapts CTI-ATE and the two CTI-RCM sets. Counts and identifier treatment differ from the originals; use the local benchmark README and license when reporting results. The underlying benchmark creators retain attribution, and adapted files retain CC BY-NC-SA 4.0.

## P3: Human-AI collaboration with trusted autonomy

Mohsin, A., Janicke, H., Ibrahim, A., Sarker, I. H., & Camtepe, S. (2026). A unified framework for human–AI collaboration in security operations centers with trusted autonomy. *ACM Transactions on Internet Technology*. https://doi.org/10.1145/3837073

[Author-deposited version and journal reference](https://arxiv.org/abs/2505.23397)

This related framework connects autonomy, trust and human oversight in SOC work. It provides methodological context for agent decision/oversight studies. Its SOC case study is distinct from this repository's industrial scenario fixtures. The author-deposited record identifies the July 2026 journal reference and publisher DOI; the publisher page may require access through ACM.

## Citation practice

Cite this release through `CITATION.cff`, the relevant underlying dataset creators, and whichever methodological papers an experiment actually uses. File-level lineage remains in `metadata/provenance.csv`. Unpublished manuscripts and preprints are not presented here as verified published journal articles. New proposed studies in the folder guides do not inherit a cited paper's reported outcomes.
