# Query-generation training data

**Preferred release-compatible subset:** [`release_compatible.json`](release_compatible.json), containing 66 distinct normalized queries with reference-table result IDs and source ordinals. Read [compatibility scope](../../docs/RESEARCH_READINESS.md) before using it. It is training material, not an independent held-out benchmark.

**Legacy source examples:** `fine_tuning.json` retains 358 original deduplicated instruction/output pairs unchanged. Do not execute or score them indiscriminately against the minimized public schema. Some require removed properties or absent relationships; `reports/training_compatibility.json` records every source record's accepted queries and exclusions. Unsupported relations are not supplied merely to satisfy old outputs.

The preferred subset uses exact-ID semantics, canonical properties, explicit relation direction, deterministic ordering and supported short paths. Its regenerated instructions describe the normalized query rather than promising discarded alternatives. The original file and its provenance remain available for historical work.

No Neo4j server execution or model fine-tuning was performed in producing this subset. Validation evaluates the declared restricted grammar against source tables. Keep identical identifiers and related query templates within one evaluation group; create independently authored template-disjoint evaluation material for generalization claims. Do not use `expected_ids` as input features. Compare base versus adapted models with matching retrieval context, output budget and engine configuration.
