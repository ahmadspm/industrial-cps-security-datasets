# Sources and third-party notices

The collection combines project-authored data with source-derived cybersecurity facts and reference tasks. The collection's CC BY 4.0 notice does not replace rights or conditions attached to third-party elements. Modified views must not be described as official MITRE/CVE publications or as endorsed by those organizations.

## MITRE materials

© 2026 The MITRE Corporation. This work is reproduced and distributed with the permission of The MITRE Corporation.

ATT&CK identifiers and relationships derive from the MITRE ATT&CK knowledge base. CWE identifiers and relationships derive from Common Weakness Enumeration. CAPEC identifiers and relationships derive from Common Attack Pattern Enumeration and Classification. Their research, development and commercial reuse permissions require preservation of their applicable notices and terms. The project does not assert complete threat coverage.

- ATT&CK: https://attack.mitre.org/resources/terms-of-use/
- CWE: https://cwe.mitre.org/about/termsofuse.html
- CAPEC: https://capec.mitre.org/about/termsofuse.html

These canonical source terms apply to source-derived material and accompany its attribution. No MITRE endorsement or trademark license is implied.

## CVE and vulnerability attributes

CVE identifiers and historical attributes are supplied as source-derived facts, not current operational advice. Raw CVE narrative descriptions and source-reference URLs are omitted from the graph view. Consult the applicable CVE/CNA/NVD/FIRST/CISA sources before operational reuse or updates.

## Reference benchmarks and project sources

CTI-ATE and CTI-RCM reference tasks are derived from the pinned G2 source. They are modified release views: direct URL fields are removed, pattern-based identifier treatment is applied and ambiguous record groups are excluded. Retain attribution to the benchmark creators and applicable original content providers; this collection does not convert their text into independently authored project content.

The underlying CTIBench dataset is distributed by AI4Sec under CC BY-NC-SA 4.0. The adapted benchmark directory retains that license, including its non-commercial and share-alike conditions, rather than the collection's default CC BY 4.0. See `data/benchmarks/LICENSE`. Cite Alam, M. T., Bhusal, D., Nguyen, L., & Rastogi, N. (2024), CTIBench: A benchmark for evaluating LLMs in cyber threat intelligence, Advances in Neural Information Processing Systems, 37, 50805–50825; https://arxiv.org/abs/2406.07599. Original dataset: https://huggingface.co/datasets/AI4Sec/cti-bench.

The four pinned project repositories are listed in `metadata/sources.csv`. Relevant upstream research papers should be cited when using their methods or benchmarks. Absence of a DOI in this collection is not permission to invent one.

The pinned G1 source requests citation of:

Nandiya, P., Mohsin, A., Ibrahim, A., Sarker, I. H., & Janicke, H. (2026). BRIDG-ICS: AI-grounded knowledge graphs for intelligent threat analytics in Industry 5.0 cyber-physical systems. Cybersecurity, 9, 167. https://doi.org/10.1186/s42400-026-00597-0

The pinned G2 source requests citation of its manuscript:

Nandiya, P., Mohsin, A., Sarker, I. H., Ibrahim, A., & Janicke, H. (2026). NeuroGraph: An AI graph-driven neuro-symbolic framework for explainable threat reasoning in advanced manufacturing. Manuscript (status as stated in the pinned source; not a new publication-status verification).

Python dependency packages are installed separately for replay and retain their own licenses.
