# Schemas and loading

## Common conventions

- UTF-8 text; comma-delimited CSV with a header; one object per JSONL line.
- `.gz` indicates gzip compression, not a separate proprietary format.
- Empty CSV cells mean missing/unsupplied values; they do not mean zero.
- Standard CVE/CWE/CAPEC/ATT&CK identifiers are normalized where available. Nonstandard identifiers use stable keyed pseudonyms. The private inverse map/key is not distributed.
- File-level SHA-256 values are in `metadata/checksums.csv`; source roles and transformations are in `metadata/provenance.csv`.

## Graph

Node primary keys are declared in `metadata/graph_node_keys.json`. Relation endpoint columns and their target node tables are declared in `metadata/graph_relation_rules.json`. Only rows whose declared endpoints exist are in the released edge tables. CVE nodes are sharded for convenient download. Numerical and enum columns retain source meaning, including historical CVSS, EPSS and KEV attributes. Structural checking is not semantic verification.

## Operational features

`trace_id` is a release-local trace identifier. `record_index` is the ordinal in its source JSONL file. `relative_seconds` is time from that trace's first parseable timestamp. `signal_id` and `event_class` are stable pseudonyms. `value` and `previous_value` preserve numbers, booleans, nulls and lists; uncontrolled strings become `state_...` pseudonyms. `ok` is a supplied boolean when available. Raw paths, URLs, names and absolute timestamps are not exported.

## Benchmarks and training

Benchmarks retain task description/prompt and reference GT fields, with `source_record_ordinal` for provenance and an explicit reference-label status. Original reference URLs are omitted. `metadata/benchmark_split_groups.csv` supplies stable group IDs to prevent related descriptions crossing future train/test boundaries.

Training JSON contains `instruction` and `output` pairs after exact-record deduplication. The original 487-row file is not duplicated in this public release.

## Agent scenarios

Each scenario contains its identifier, declared test count and a `tests` array with inputs and expected LLM/final outputs. These are fixtures. The offline test script evaluates the supplied deterministic reference implementation; it does not turn expected labels into physical observations.

## Research quality artifacts

The preferred query subset uses `metadata/graph_import_schema.json` labels and original CSV property names. `metadata/asset_graph_crosswalk.csv` declares exact inventory-to-product joins; host IDs are a separate namespace. `metadata/trace_manifest.csv` and `metadata/operational_semantics.json` report computed trace attributes and unknown collection/physical semantics. See [research readiness](RESEARCH_READINESS.md) and [evaluation contract](../evaluation/README.md).
