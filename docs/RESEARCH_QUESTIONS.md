# Research questions and evaluation design

Each row identifies the strongest claim supported by the released evidence. Proposed studies still require a literature review and an independently defined evaluation protocol.

| Research question | Released data | Method and comparison | Evaluation unit and metrics | Suitability and limitation |
|---|---|---|---|---|
| Can a fixed monitoring budget cover more exposed flows? | Inventory, zones, conduits, dataflows | Boundary-aware placement versus degree-based placement | Withheld topology variants; weighted flow coverage, cost | Structural analysis directly supported; no measured service-loss outcome |
| Does relation typing improve CWE prediction? | Knowledge graph and HAS_CWE mappings | Typed inference versus training-only label popularity | Hold out whole CVE groups; Hit@k, MRR | Reference mapping recovery; remove target and inverse paths from model inputs |
| Does retrieval reduce unsupported threat identifiers? | CTI benchmarks and graph | Frozen model with and without retrieval | Group duplicate descriptions; exact match, unsupported-ID rate, abstention coverage | Conditional on controlled model and source separation; benchmark overlap must be checked |
| Are unfamiliar event patterns transferable across traces? | Operational event features | Event rarity versus transition-based model | Whole held-out traces; flag rate, unseen-class rate | Exploratory only; attack precision/recall needs independent adjudication |
| Does fine-tuning generalize to new query structures? | Instruction/output pairs | Base model versus adapted model | New template-disjoint evaluation set; execution and semantic agreement | Training data alone cannot establish generalization |
| Do guard rules reduce disallowed decisions? | Agent scenario expected outputs | Unguarded versus guarded decision policy; constant-stop comparator | Held-out scenario families; stop/continue recall, prohibited-decision rate, coverage | Expected-decision agreement; no real tool execution or operational safety certification |
| Does evidence corruption change recommendations? | Derived graph or CTI variants | Clean versus explicitly perturbed inputs | Paired cases; decision-change and recovery rates | New perturbation protocol required; no supplied poisoning ground truth |
| Does evidence presentation improve analyst triage? | Validated cross-source joins | Controlled analyst study with/without traceable evidence | Participant/task; accuracy, time, confidence calibration | Requires new participant evidence and verified joins |

## Evidence and reporting rules

Upstream reference labels express source mappings. Synthetic records express generating assumptions. Operational events are observations without verified malicious labels. Agent fixtures specify expected decisions; they are not observed agent outcomes. Proposed applications are hypotheses until evaluated.

Report the released version, file hashes, grouping rule, exclusions, model configuration, baseline and uncertainty. Split groups before fitting thresholds or selecting features. Keep the test set fixed during method development. Bootstrap independent traces or scenario families rather than individual dependent rows. For graphs, state which relations were withheld and whether candidate labels unseen in training remain in evaluation.

## Starter protocols

See [examples](../examples/README.md) for runnable, standard-library baselines, explicit split manifests and recorded results. These illustrative protocols are newly introduced starting points, not official benchmark splits or reproductions of related papers.
