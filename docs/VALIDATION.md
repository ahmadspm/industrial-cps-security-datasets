# Data validation

These results describe the published data representation and network-remapped reference implementation.

| Check | Result |
|---|---:|
| Released graph nodes | 305,167 |
| Released graph edges checked against typed endpoint rules | 276,420 |
| Unmatched released graph references | 0 |
| Unique training records | 358 |
| Curated benchmark records | 2,047 |
| Benchmark records excluded for ambiguous reference groups | 13 |
| Expected-decision scenario cases | 400 |
| Reduced operational event records | 14,124 |
| Offline reference test suites passed | 24 / 24 |
| Offline reference tests passed | 285 / 285 |
| Deterministic experiment commands completed | 10 / 10 |

The validator checks file hashes when a manifest is present, graph endpoint membership, node-ID uniqueness, training deduplication, remaining benchmark description/label ambiguity, fixture counts, controlled operational value types, Python syntax, unapproved IPv4 literals and high-confidence credential patterns.

The offline replay covers reliability fixture cases, retrieval/planning fixtures, governed-tool decisions, end-to-end missions and six impairment profiles. Reliability runs use a fixture provider rather than a live Qwen model. Reference policy examples use reserved benchmarking networks; no physical testbed connection is required. One upstream station-test import path is supplied through the replay wrapper's environment rather than silently changing the original test's assertions.

The file `validation/replay_summary.json` records the suite results. `code/requirements-replay.txt` records dependency versions used for the legacy agent suites. Validation is not a claim of zero re-identification risk, certified semantic labels, live LLM performance, Neo4j execution accuracy, production security or measured physical-to-twin fidelity.

Graph references without matching endpoints and ambiguous label groups are excluded under the documented curation rules.

## Research-quality checks

The added research-quality suite contains 15 tests covering the normalized query subset, unsupported relations/identifiers, all-400-case accounting, malformed/missing predictions, risk and tool constraints, context-dependent assertions, plan fields, connected-task boundaries, source consistency and trace manifests. These checks supplement the historical 285 reference tests rather than replace or rerun them. See [research methods](RESEARCH_METHODS.md) for methods, scope and interpretation.
