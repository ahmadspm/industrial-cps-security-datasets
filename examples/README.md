# Reproducible starter experiments

Run from the repository root with Python 3.11 or later; no packages, model, API key or equipment are required:

```bash
python3 examples/run_starters.py --output /tmp/cps-starters
python3 examples/check_starters.py
```

`baselines/results.json` records the measured reference run. `baselines/splits.json.gz` freezes group membership. Output excludes timestamps and machine paths for byte-for-byte comparisons.

1. **Exploratory anomaly analysis:** training event-class frequencies score unfamiliar events. The 95th percentile threshold is fitted on training events only. SHA256 assigns complete traces to train/test. Flag rates measure rarity, not maliciousness; `ok` is not used as an attack label.
2. **Graph mapping:** rank CWE identifiers by training CVE-group prevalence and evaluate held-out HAS_CWE reference mappings with Hit@1, Hit@5 and MRR. Deduplicate CVE/CWE pairs. All test CVE groups remain disjoint. No graph side information is used. A stronger model must withhold target and inverse relations and audit other leakage paths.
3. **Agent decisions:** an always-stop policy provides a deliberately simple comparator. Families SC-02, SC-06, SC-14 and SC-18 are held out; this documented selection includes both stop and continue requirements. Only explicit boolean `expected_final.stop` fields are evaluated; missing fields are excluded, not inferred. The split was selected for class coverage when introducing this protocol; future methods must freeze it. Report both decision classes. No tool is executed.

These are illustrative research protocols, not official benchmark partitions. The graph split is group-based rather than temporal. Agent-family holdout does not guarantee semantic independence: related families may share rules. Report per-family results and evaluate further independently authored families before claiming generalization. Baseline scores establish a reproducible floor, not novel findings. Test flag rate has no ground-truth attack interpretation.

The new audit counted **27 distinct trace IDs** in the 14,124 released events; earlier documentation stated 29. No events were removed in this documentation correction.
