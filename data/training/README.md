# Training data: cybersecurity query generation and adaptation

`fine_tuning.json` contains **358 unique instruction/output pairs**. The public file retains the first occurrence after removing 129 exact duplicates from the 487-record source. Fields are `instruction` and `output`; many outputs are graph-query examples.

## Research supported

| Study | Proposed design | Measures |
|---|---|---|
| Cybersecurity NL-to-query generation | Compare prompting, retrieval of demonstrations and parameter-efficient adaptation | Syntax/schema validity, execution accuracy in a separately supplied graph, unsupported identifiers |
| Small-model adaptation | Compare an unchanged base model with a model adapted on a controlled training subset | Task accuracy, model size, inference latency and memory use |
| Training-data quality | Compare duplicate-containing and deduplicated training under the same held-out protocol | Held-out accuracy, robustness and sensitivity to repeated examples |
| Explainable query construction | Require generated queries to cite allowed graph entities/relationships | Evidence coverage, invalid relationship rate and reviewer agreement |

Use a separately held-out task set and prevent instruction/entity/description leakage. The original duplicate-containing file is retained only in private provenance storage; it is not another public split. Any new development/test partition must be documented. The repository does not assert a historical held-out partition for these 358 pairs.

Cypher validity alone is insufficient: a query can be syntactically valid yet address the wrong entities or return unsupported results. Execution-based evaluation requires the appropriate schema and graph instance, and safety/authorization controls if any database is used.

## Source and author research

The pairs originate from the pinned G2 project identified in [source metadata](../../metadata/sources.csv). [P2: NeuroGraph](../../docs/RELATED_PUBLICATIONS.md#p2-neurograph) is the custodian's associated co-authored article on graph-grounded neuro-symbolic reasoning and query generation. The public deduplicated file is a transformed release view; exact equivalence to the paper's complete training configuration is not asserted.

[P1: BRIDG-ICS](../../docs/RELATED_PUBLICATIONS.md#p1-bridg-ics) supplies related graph/threat-analysis context. [T1: CTIBench](../../docs/RELATED_PUBLICATIONS.md#t1-ctibench--third-party-benchmark-source) is an external evaluation dataset source and is not the custodian's article. Evaluation needs a defensible separation from training.
