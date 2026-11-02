# Agent scenarios: planning, policy compliance and trusted autonomy

Twenty JSON files provide **400 expected-decision test cases**, with 20 variations per scenario. Each includes inputs, expected intermediate LLM outputs and expected final behaviour. This folder supports controlled evaluation of cybersecurity decision agents and their deterministic policy checks.

## Scenario guide

| File | Research focus |
|---|---|
| `scenario1.json` | Initial campaign admission/continuation decisions |
| `scenario2.json` | Termination when no registered tools are available |
| `scenario3.json` | Stopping at an accumulated detection-risk limit |
| `scenario4.json` | Risk-sensitive selection among available simulated tools |
| `scenario5.json` | Aborting when a required lower-risk alternative is unavailable |
| `scenario6.json` | Priority of the supplied campaign plan over generated planning |
| `scenario7.json` | Fallback when the planned tool is unavailable |
| `scenario8.json` | Valid decisions with a single available tool |
| `scenario9.json` | Reconnaissance loop guards and bounded recursion |
| `scenario10.json` | Pivot/replan decisions after repeated poor scores |
| `scenario11.json` | Continuation/escalation decisions for strong scores and low modelled risk |
| `scenario12.json` | Rejection of hallucinated tool identifiers |
| `scenario13.json` | Exclusion of simulation-only tools outside simulation mode |
| `scenario14.json` | ReAct endpoint termination under high modelled risk |
| `scenario15.json` | Reflect endpoint risk-threshold compliance |
| `scenario16.json` | Technique-identifier format validity |
| `scenario17.json` | Decision stability under mid-range conditions |
| `scenario18.json` | Structured factory-analysis output from the recon endpoint |
| `scenario19.json` | Plan completeness for requested round numbers |
| `scenario20.json` | Causal-chain starting-node consistency |

## Research supported

- Compare model-only decisions, deterministic policy checks and a combined agent/policy design.
- Evaluate tool-name grounding, termination behaviour, structured output and plan consistency.
- Study sensitivity to prompt wording, irrelevant context and conflicting candidate plans using explicitly documented perturbations.
- Evaluate human-review or authorization gates only where the added experimental protocol actually specifies those gates and labels.

Report decision agreement against the supplied references, policy-violation rate, invalid-tool rate, termination compliance, plan coverage and consistency across repeated runs. Keep scenario families together in held-out evaluation; 20 variations of one rule are not automatically independent evidence.

These cases contain expected outputs. They are not 400 observed physical attacks, not ground truth for attack success, and not by themselves an execution harness for the original G4 endpoints. The separate `code/twin_reference` implementation has its own fixtures; its reported tests must not be presented as execution of these 400 cases.

## Connection to the author's research

[P5: Autonomous cyber-physical security assessment](../../docs/RELATED_PUBLICATIONS.md#p5-autonomous-cyber-physical-security-assessment) is the research manuscript on a behavioural manufacturing twin and cooperative agentic AI, including AOA/ASBIO. Its data/code statement points to the G4 source project from which these scenario files originate. Cite the linked research record and identify the version used. The 400 expected-decision fixtures do not by themselves reproduce the manuscript's live-model or production-impact results.

[P3: Human-AI collaboration with trusted autonomy](../../docs/RELATED_PUBLICATIONS.md#p3-human-ai-collaboration-with-trusted-autonomy) is the custodian's related published methodology for autonomy, trust and oversight. Its SOC case study is distinct from these industrial fixtures.
