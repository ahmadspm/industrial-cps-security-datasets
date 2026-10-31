# Benchmarks: LLM and retrieval evaluation for CTI

These are adapted CTIBench reference tasks. They support evaluation of cybersecurity language models, prompting, retrieval and graph-assisted reasoning.

| File | Released records | Task | Suitable measures |
|---|---:|---|---|
| `cti-ate.csv.gz` | 60 | Extract ATT&CK technique identifiers from threat descriptions | Set-based precision, recall and F1; invalid-ID rate |
| `cti-rcm.csv.gz` | 996 | Map vulnerability descriptions to CWE reference labels | Normalized label accuracy; macro-F1 when label support is reported |
| `cti-rcm-2021.csv.gz` | 991 | Additional root-cause mapping comparison set | Accuracy/F1 and performance difference from the other RCM set |

Five ambiguous repeated-description groups were excluded: four records from CTI-RCM and nine from CTI-RCM-2021. `GT` remains an upstream reference label; `source_record_ordinal` traces the original row, and `reference_label_status` records the evidence boundary. Original URL fields were removed.

## Research supported

- Compare a base model, prompting variants and a separately adapted model under the same evaluation protocol.
- Compare no retrieval, text retrieval and Graph-RAG using a declared evidence corpus.
- Test whether schema constraints reduce invalid technique/CWE identifiers.
- Examine abstention and evidence citation when the reference answer cannot be supported by the supplied context.
- Compare the two RCM sets as distinct evaluation conditions, without assuming the CVE identifier year establishes an exact disclosure timestamp.

Use [description-group identifiers](../../metadata/benchmark_split_groups.csv) to keep related records together in any new splits. Keep the [training](../training/README.md) file separate, audit overlap and report any benchmark use in prompt or hyperparameter selection. Technique extraction may have multiple valid identifiers; define normalization, set matching and reference handling explicitly.

The curated counts and transformations differ from the original benchmark. A measured result on this release must identify this version rather than claim an exact reproduction of the original paper's scores. Reference accuracy does not independently prove factual correctness.

## Published article and license

[P2: CTIBench](../../docs/RELATED_PUBLICATIONS.md#p2-ctibench) is the published source benchmark article. [P1](../../docs/RELATED_PUBLICATIONS.md#p1-bridg-ics) is relevant industrial graph context for proposed Graph-RAG experiments, not the source of these CTIBench tasks.

This directory retains **CC BY-NC-SA 4.0**, including non-commercial and share-alike conditions. See [LICENSE](LICENSE) and retain the original creators' attribution and this adaptation notice.
