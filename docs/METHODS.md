# Curation and exclusions

The release was built from four pinned upstream repositories and five owner-supplied archives. Raw source bytes were verified during private staging. This public repository is intended to start with clean history, not inherit raw staging commits.

## Identifier treatment

Inventory exports use a column whitelist. Real names, locations, IPs, subnets and free-text operational annotations are omitted. Stable HMAC-based pseudonyms preserve joins and state equality without distributing the private key. Synthetic endpoint/account/session identifiers are likewise pseudonymized. Operational exports use a reduced feature schema and per-trace relative timestamps.

Reference implementation network examples were remapped consistently into reserved benchmarking ranges; loopback and unspecified addresses remain conventional software examples. Subnet relationships needed by fixture policy tests are preserved. No production connection is required by the offline replay.

## Graph quality

Release graph fields are factual identifiers, historical scores and enum attributes. Narrative descriptions, reference URLs, account/credential tables, raw host addresses, inferred tactic labels, redundant node copies and untyped relation tables are omitted. Typed relation rules filter 14,884 unmatched source rows. Remaining released relation rows have zero unmatched endpoint references under those declared rules. Ambiguous CAPEC level attributes are omitted; one ID-only node is retained per standard identifier.

Source limitations remain documented rather than repaired by fabrication. In particular, the earlier KG1 check found 14,066 CVE-to-CWE references to 37 identifiers absent from its node table; these are not promoted into asserted public graph edges.

## Labels and duplicates

Thirteen benchmark records in five repeated-description groups with differing reference labels are excluded. This avoids resolving uncertain labels by arbitrary choice. Other repeated descriptions are retained when complete records differ. Future split groups are supplied; no historical experimental split is asserted.

Fine-tuning data contained 129 exact record duplicates. Retaining the first occurrence produces 358 unique records. Synthetic, training, expected-decision and observed-feature evidence classes remain distinct.

## Screening and release scope

The large raw CVE narrative table had 105 credential-like reference URL matches and seven description matches. A structured 112-field redaction patch was tested privately, but the minimized public graph omits both descriptions and reference URLs entirely. No source token was used or tested against a service. Source code with a nonempty proxy-token fallback is excluded along with the G4 execution tooling.

Raw diagnostic logs, screenshots/PDFs, account tables, credentials, private identity maps, unrelated historical reports, staging transfer scripts and numbered source-archive bundles are excluded. The included reference-code fixtures and earlier model versions are retained only where needed for offline tests or their dependencies; historical live-model evidence reports are not redistributed as newly reproduced results.
