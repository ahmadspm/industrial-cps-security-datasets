"""Deterministic comparisons, explicitly not model inference."""
import json,pathlib
from agent_evaluator import cases,evaluate
from connected_evaluator import evaluate as connected
ROOT=pathlib.Path(__file__).resolve().parents[1]

def run():
    result={'kind':'deterministic_baselines_not_LLM_results','agents':{},'connected':{}}
    for name,stop in [('always_stop',True),('always_continue',False)]:
        ps=[{'id':t['id'],'nodes':{},'final':{'stop':stop}} for _,t in cases()]
        r=evaluate(ps);result['agents'][name]={k:v for k,v in r.items() if k!='results'}
    refs=json.loads((ROOT/'evaluation/connected_reference.json').read_text())
    abstain=[{'id':r['id'],'cve_ids':[],'decision':'abstain','confirmed_vulnerable':False,'action_authorized':False} for r in refs]
    r=connected(abstain);result['connected']['always_abstain']={k:v for k,v in r.items() if k!='results'}
    # This is a deterministic reference-table retriever, not an independent ground-truth validation.
    from run_connected import retrieve
    predictions=retrieve(ROOT);r=connected(predictions);result['connected']['reference_table_retriever']={k:v for k,v in r.items() if k!='results'}
    empty=evaluate([])
    catalog={}
    for case in empty['results']:
        for item in case['checks']:
            key=item['scope']+'.'+item['field'];entry=catalog.setdefault(key,{'occurrences':0,'status_without_output_or_context':item['status']});entry['occurrences']+=1
    (ROOT/'reports/agent_predicate_coverage.json').write_text(json.dumps({'specification':empty['specification'],'cases':empty['cases'],'predicates':catalog,'missing_output_policy':'Machine-scored assertions fail; missing context is unscored; narrative notes are documentation.'},indent=2,sort_keys=True)+'\n')
    (ROOT/'reports/evaluation_baselines.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'agents':list(result['agents']),'connected':{k:v['overall'] for k,v in result['connected'].items()}},indent=2))
if __name__=='__main__':run()
