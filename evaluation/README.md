# Evaluation suite and connected evidence task

This suite evaluates declared output constraints and released reference relationships. It does not execute attack tools or authorize physical actions.

## Current execution status

| Work | Status |
|---|---|
| All 400 agent fixtures routed through evaluators | Implemented and exercised with deterministic baselines |
| Machine-checkable expected fields | Implemented; missing outputs fail |
| Topology/category-dependent assertions | Explicitly unscored without reviewed context |
| Real model comparison | Runner provided; **not executed here** because no model runtime, weights or API credentials are available |
| Connected task | 94 cases; 33 assets with source-linked CVEs; reference retriever and abstention baseline executed |
| Source consistency audit | Separate implementation passed; shares source data |
| Independent expert review | **Pending**; review packet provided, no sign-off claimed |

## Agent output contract

Predictions are a JSON array. One record per case uses the original case `id`:

```json
{
  "id": "SC-01-T01",
  "nodes": {
    "assess": {"next_action": "attack", "detection_risk": 0.0},
    "generate_mitre_plan": {"target_node": "MQTT_BROKER", "technique_id": "T0800", "causal_chain": ["MQTT_BROKER"], "severity": "Low"},
    "select_tool": {"tool_name": "BrokerInfoProbeTool"}
  },
  "final": {"stop": false, "tool": "BrokerInfoProbeTool"}
}
```

This illustrates formatting only, not an asserted correct technique/target mapping. Other cases require different stages. Plan outputs use `phases`, each with `round`, `tool`, `target`, `technique`, `purpose`; `deep_recon` uses `recommended_target` and `recommended_technique`. Other field names follow the fixture predicates. Stage outputs must be retained by instrumenting the evaluated agent; final outputs alone cannot establish intermediate-stage correctness.

```bash
python3 evaluation/agent_evaluator.py --predictions predictions.json --output /tmp/agent-scores.json
python3 evaluation/run_baselines.py
python3 -m unittest discover -s tests -v
```

The evaluator handles all currently declared expected-field names. It reports exact/enum decisions, risk constraints, tool inclusion/exclusion, tool availability, target/chain checks, structured recon fields, technique-ID syntax, plan phases and continuation decisions. New unimplemented predicates raise errors. Duplicate or unknown prediction IDs raise errors; missing predictions remain failures across the full 400-case denominator.

Specification `agent-fields-v1` interprets `~x` as absolute tolerance 0.02 and `outcome_summary_contains` as **any** listed case-insensitive substring. These are declared evaluation conventions for ambiguous fixture notation, not independently reviewed truth. Keyword agreement is only a lexical proxy. Technique syntax does not establish ATT&CK semantic correctness. Narrative `note` fields are reported as documentation and excluded from scores. Report per-family results alongside micro predicate rates; an incomplete response cannot receive a fully covered pass.

For assertions requiring topology or technique/target semantics, supply a separate `--contexts contexts.json`, keyed by case ID, with reviewed `topology_nodes` and `technique_target_categories` (technique ID -> allowed target names). Preserve evidence for how that context was established. Vulnerability-score keys are not silently treated as topology. Without these maps, the relevant predicates are **unscored**, and a fully covered pass is impossible. The context file must never be synthesized from candidate model output.

## Real local-model comparisons

Install Ollama and at least two distinct models on a machine able to run them. The runner checks installed model digests and rejects two names resolving to identical weights. Use exact installed tags; the names below are examples, not a claim they were run here:

```bash
python3 evaluation/run_local_models.py --models qwen3:8b llama3.1:8b --task agents --output /tmp/cps-agent-models
python3 evaluation/run_local_models.py --models qwen3:8b llama3.1:8b --task connected --output /tmp/cps-connected-models
```

Both commands use the local Ollama API. They preserve prompts, raw responses, parsed outputs, errors, timings, input hashes, model digests and scores. Temperature is zero and the seed is fixed; cross-platform bitwise determinism is not guaranteed. No model is downloaded by the runner. `--limit 2` is a smoke test and is marked partial rather than a full comparison. Agent results explicitly identify frozen held-out families SC-02/06/14/18; these public fixtures are not contamination-resistant hidden tests. Review prompts and token/truncation statistics before scientific interpretation. The agent comparison evaluates one frozen policy prompt, not the original multi-agent runtime.

Connected comparisons run both **with evidence** and **without evidence** for each model. Expected answers are not sent. Passing with evidence tests supported retrieval, not memorization-free reasoning or physical applicability. No-evidence cases must abstain under the declared policy; reference-recovery scores and operational appropriateness must be interpreted separately. Preserve outputs even when parsing fails. For publication, report both linked and no-link groups, uncertainty over independent groups, and failure rates. The 94 assets are not necessarily independent physical installations.

Official interfaces: [Ollama API](https://docs.ollama.com/api/chat), [structured outputs](https://ollama.com/blog/structured-outputs).

## Connected task and independent review

`connected_questions.json` supplies asset questions and source-backed edge evidence. `connected_reference.json` contains evaluation answers; it is never read by the model runner. The path is inventory asset -> product -> CVE -> CWE -> mitigation **identifier**. An identifier-only mitigation node cannot justify an operational recommendation. A missing edge does not prove absence of vulnerability. Every answer requires `confirmed_vulnerable=false` and `action_authorized=false`, interpreted as *not established by the supplied evidence*, not as proof of safety.

```bash
python3 evaluation/run_connected.py > /tmp/connected-predictions.json
python3 evaluation/connected_evaluator.py --predictions /tmp/connected-predictions.json --output /tmp/connected-scores.json
python3 evaluation/audit_connected.py
```

The reference-table retriever's perfect mapping agreement is a consistency check against the same source mappings, not independent ground-truth validation. The always-abstain baseline is reported separately. `reports/connected_source_audit.json` uses another implementation to check evidence membership and answer completeness; this still does not replace expert review.

For independent review, give a qualified reviewer the source tables, questions, references and `independent_review.csv`. The reviewer should be independent of reference construction, document their identity/role and conflicts, check joins and every claimed evidence relation, distinguish source assertions from actual asset applicability, record disagreements, and sign off only after resolution. Review all 94 cases or publish the sampling rule and coverage. Do not edit original source mappings to force agreement. The review CSV is initially blank; regeneration preserves completed fields and marks changed references stale. No reviewer has been contacted and no independent human review has been claimed.
