# Inventory: attack surface, segmentation and asset criticality

This folder represents the structural context of an industrial CPS: assets, components, process zones and communication paths. Direct names, addresses, locations and other identity fields were removed or pseudonymized.

## File guide

| File | Records | Research role |
|---|---:|---|
| `assets-Master.csv` | 94 | Asset type, zone, Purdue level, criticality and safety-impact context |
| `components_inventory_Fischertechik-smart-factory.csv` | 53 | Component categories and criticality/safety attributes |
| `Dataflows.csv` | 120 | Directed asset dependencies, protocol/port use and boundary crossings |
| `ZONES.csv` | 6 | Zone membership and Purdue-level context |
| `zones_conduits.csv` | 5 | Declared links between zones |

## Research supported

| Study | Proposed approach | Evaluation measures |
|---|---|---|
| Industrial attack-surface modelling | Construct an asset/flow graph; compare exposure by zone, level and protocol | Reachable assets, cross-zone paths, exposed high-criticality assets |
| Segmentation and conduit analysis | Compare candidate zone policies against the declared communication graph | Policy violations, reachability reduction, legitimate-flow retention |
| Crown-jewel prioritization | Combine source criticality/safety attributes with degree and betweenness baselines | Rank agreement, sensitivity to weighting assumptions, top-k coverage |
| Security monitoring placement | Compare placements at assets or conduits under an explicit observation model | Modelled path coverage, placement count and coverage of critical assets |

A suitable experiment compares a topology-only ranking with a criticality-aware ranking, documenting how much each changes the monitoring priorities. Any claim of sensor/control effectiveness needs evidence beyond this inventory.

## Connections and published article

Use this folder with [knowledge_graph](../knowledge_graph/README.md) for contextual threat reasoning and with [synthetic](../synthetic/README.md) for modelled flow-risk studies. Check join coverage and identifier namespaces first.

[P1: BRIDG-ICS](../../docs/RELATED_PUBLICATIONS.md#p1-bridg-ics) is relevant published work on integrated industrial security graphs and threat analysis. The public tables are curated release views; the article is not a certification of every released attribute or proposed study.

Counts and schemas describe a recorded inventory, not a live scan. Missing services, devices or paths must not be interpreted as proof that they do not exist. Source lineage is in [provenance](../../metadata/provenance.csv).
