# Dataset card

## Intended use

Offline research into typed cybersecurity graph relationships, synthetic protocol features, operational signal changes, retrieval/reference-label analysis, and governed agent behaviour in a digital-twin fixture environment.

The custodian is Dr Ahmad Mohsin. Upstream repository revisions are pinned in `metadata/sources.csv`. Individual records and files are linked to their sources and transformations in `metadata/provenance.csv`.

## Representation and limitations

This is a curated release view, not a complete mirror of raw source archives. Pseudonymization and attribute removal reduce direct disclosure but do not establish formal anonymity. Do not attempt re-identification or infer the real institution's network from the reference models. No inverse pseudonym map or private transformation key is distributed.

Knowledge-graph structural checks test identifiers and endpoint membership. They do not confirm that every vulnerability, mitigation or attack relationship is true. CVSS/EPSS/KEV attributes are historical source values, not current vulnerability advice. The release is unsuitable for production asset-risk decisions without renewed source verification.

Synthetic attackability scores and protocol records are not observed physical attacks. Operational event features preserve numeric/boolean observations and state equality but omit original signal names, addresses, timestamps and uncontrolled strings. Sampling gaps and unknown provenance must not be interpreted as physical faults without separate evidence.

CTI benchmark GT values remain upstream reference labels, not independently adjudicated truth. Five ambiguous description groups are withheld. Keep each description/instruction group in a single future split. The deduplicated fine-tuning file is training material and must not be used as an independent test set.

G4 scenarios contain expected decisions. Deterministic replay verifies fixture policy and implementation behaviour; it does not reproduce live LLM inference, Neo4j reasoning, adversarial effectiveness against real systems or physical-to-digital fidelity.

## Release scope

The collection excludes raw diagnostic logs, source screenshots, account/credential tables, private identity maps, unrestricted third-party narratives and graph edges without matching endpoints. Researchers should use the published schemas and provenance to interpret the retained representations.

Report data-quality issues through the public repository's issue tracker. Do not include real credentials, network identifiers or raw private logs in an issue.
