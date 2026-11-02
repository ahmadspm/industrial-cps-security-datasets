# Data curation and representation

## Sources and provenance

The collection integrates four version-pinned research repositories and five source archives. `metadata/sources.csv` identifies source revisions. `metadata/provenance.csv` records file-level source roles and transformations. The published files are research views rather than complete source mirrors.

## Identifier treatment

Inventory tables retain a defined subset of attributes. Direct names, locations, IP addresses, subnets and unrestricted annotations are omitted. Stable HMAC-based pseudonyms preserve declared identifier joins and state equality. The identifier key and inverse mapping are not distributed. Operational timestamps are relative within each trace.

Reference-code network examples use reserved benchmarking ranges. Subnet relationships required by fixture policies are preserved. Offline evaluation requires no production connection.

## Graph construction

The public graph retains standard cybersecurity identifiers, selected historical scores, enum attributes and typed relationships. Narrative descriptions, account/credential tables and direct network addresses are omitted. Declared endpoint rules exclude 14,884 source rows without matching node references. Each retained edge has valid endpoints under those rules; this does not certify semantic correctness or physical applicability.

CAPEC identifiers with conflicting descriptive attributes are represented as ID-only nodes. Missing reference nodes and inferred relationships are not fabricated. Connectivity and relation incidence are described in `reports/graph_connectivity.json`.

## Reference labels and duplicates

Thirteen benchmark records across five repeated-description groups with differing labels are excluded. Other repeated descriptions remain where the complete records differ. Description-group IDs support grouped evaluation splits. Labels remain source references rather than independently adjudicated physical ground truth.

The legacy query collection contains 358 distinct records after removing 129 exact duplicates. The 66-query normalized subset uses supported schema properties, relationship directions and exact-identifier semantics. Its transformation and exclusion details are in `reports/training_compatibility.json`.

## Scope and privacy

The dataset omits raw diagnostic logs, screenshots, account/credential tables, direct identity mappings and unrestricted source narratives. These choices reduce disclosure and support bounded research use; they do not establish formal anonymity.

Synthetic assumptions, source-derived mappings, reduced observations and expected agent decisions retain distinct evidence classes. Earlier code versions are included where required by the documented reference tests. Reported deterministic results must not be interpreted as live-model or physical-system measurements.
