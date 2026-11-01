#!/usr/bin/env python3
"""Deterministic, standard-library baselines. No model or network calls."""
import argparse, collections, csv, gzip, hashlib, json, pathlib

def partition(key):
    return ("test" if int(hashlib.sha256(("cps-starter-v1:"+key).encode()).hexdigest(),16)%5==0 else "train")

def run(root):
    splits={}; report={"protocol":"cps-starter-v1", "split_rule":"SHA256(cps-starter-v1:<group>) modulo 5; 0=test", "scope":"Exploratory baselines; no physical security or attack detection claims"}
    with gzip.open(root/'data/operational/event_features.jsonl.gz','rt') as f:
        events=[json.loads(line) for line in f]
    groups={e['trace_id'] for e in events}; splits['operational']={k:partition(k) for k in sorted(groups)}
    train=[e for e in events if partition(e['trace_id'])=='train']; test=[e for e in events if partition(e['trace_id'])=='test']
    counts=collections.Counter(e['event_class'] for e in train)
    def score(e): return 1-counts[e['event_class']]/len(train)
    threshold=sorted(map(score,train))[int(.95*(len(train)-1))]
    report['anomaly']={"train_traces":sum(v=='train' for v in splits['operational'].values()),"test_traces":sum(v=='test' for v in splits['operational'].values()),"train_events":len(train),"test_events":len(test),"threshold_train_p95":threshold,"test_flag_rate":sum(score(e)>threshold for e in test)/len(test),"unseen_event_class_rate":sum(e['event_class'] not in counts for e in test)/len(test),"interpretation":"Event rarity flags, not attack precision/recall. No verified attack labels."}
    p=root/'data/knowledge_graph/HAS_CWE.csv.gz'
    with (gzip.open(p,'rt') if p.exists() else (root/'data/knowledge_graph/HAS_CWE.csv').open()) as f: edges=list(csv.DictReader(f))
    targets=collections.defaultdict(set)
    for e in edges: targets[e['cve_id']].add(e['cwe_id'])
    splits['graph']={k:partition(k) for k in sorted(targets)}
    popularity=collections.Counter(cwe for cve,values in targets.items() if partition(cve)=='train' for cwe in values)
    ranking=sorted(popularity,key=lambda k:(-popularity[k],k))
    held=[v for k,v in targets.items() if partition(k)=='test']
    report['graph']={"task":"Predict source-reference CWE membership for held-out CVE groups using training-only CWE popularity", "train_cves":sum(v=='train' for v in splits['graph'].values()),"test_cves":len(held),"hit_at_1":sum(bool(v & set(ranking[:1])) for v in held)/len(held),"hit_at_5":sum(bool(v & set(ranking[:5])) for v in held)/len(held),"mrr":sum(1/min([i+1 for i,k in enumerate(ranking) if k in v],default=float('inf')) for v in held)/len(held),"interpretation":"Frequency baseline against upstream mappings, not validated exploitation. No other graph relations are supplied to the predictor."}
    cases=[]
    for p in sorted((root/'data/agent_scenarios').glob('scenario*.json')):
        doc=json.loads(p.read_text()); group=doc['scenario_id']; splits.setdefault('agents',{})[group]=('test' if group in {'SC-02','SC-06','SC-14','SC-18'} else 'train')
        for case in doc['tests']:
            expected=case.get('expected_final',{}).get('stop')
            if isinstance(expected,bool):cases.append((group,case['id'],expected))
    # Constant-stop predictor is a declared non-learning baseline; expected fields are read only for scoring.
    held=[c for c in cases if splits['agents'][c[0]]=='test']
    positives=sum(c[2] for c in held)
    report['agents']={"predictor":"always stop", "split_rule":"Held-out families SC-02, SC-06, SC-14, SC-18; explicit selection includes stop and continue families", "excluded_cases_without_boolean_stop":400-len(cases), "test_cases_with_boolean_stop":len(held),"test_stop_prevalence":positives/len(held),"stop_agreement":positives/len(held),"continue_recall":0.0,"interpretation":"Only explicit boolean expected_final.stop is scored. This is a constant decision baseline, not an executed agent or a safety result."}
    return report,splits

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
    report,splits=run(a.root);a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (a.output/'splits.json.gz').write_bytes(gzip.compress((json.dumps(splits,sort_keys=True)+'\n').encode(),mtime=0))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
