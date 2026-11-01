#!/usr/bin/env python3
"""Evaluate all declared fixture fields; unsupported context is explicit, never a pass."""
import argparse, collections, json, math, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
SPEC_VERSION='agent-fields-v1'
EXACT={'next_action','target_node','tool_name','tool','technique_id','campaign_decision','source','action','from','stop','severity'}
META={'note'}


def cases(root=ROOT):
    return [(d,t) for p in sorted((root/'data/agent_scenarios').glob('scenario*.json')) for d in [json.loads(p.read_text())] for t in d['tests']]


def nonempty(v):return v is not None and v!='' and v!=[] and v!={}


def check(key,expected,actual,context,tolerance):
    """Return (pass|fail|unscored|documentation, reason)."""
    if key in META:return 'documentation','Narrative note; excluded from numerical score.'
    def result(v):return ('pass' if v else 'fail'),'predicate evaluated'
    def field(k):return actual.get(k) if isinstance(actual,dict) else None
    if key in EXACT:
        value=field(key)
        # bool is not a numeric/enum substitute; absent fields always fail.
        if isinstance(expected,bool):return result(type(value) is bool and value==expected)
        return result(value in expected if isinstance(expected,list) else type(value)==type(expected) and value==expected)
    if key=='recommended_target':
        if expected!='any known topology node':return result(field(key)==expected)
        known=context.get('topology_nodes')
        if known is None:return 'unscored','Verified topology node context not supplied.'
        return result(field(key) in known)
    if key=='must_match_target_category':
        mapping=context.get('technique_target_categories')
        if mapping is None:return 'unscored','Reviewed technique-to-target-category mapping required.'
        return result(field('target_node') in mapping.get(field('technique_id'),[]))
    if key=='all_hops_in_topology':
        known=context.get('topology_nodes')
        if known is None:return 'unscored','Verified topology context not supplied; vulnerability-score keys are not assumed to be topology.'
        chain=field('causal_chain');return result(isinstance(chain,list) and bool(chain) and all(n in known for n in chain))
    if key=='detection_risk':
        v=field('detection_risk')
        if type(v) not in (int,float) or not math.isfinite(v):return result(False)
        if type(expected) in (int,float):return result(abs(v-expected)<=1e-9)
        m=re.fullmatch(r'(>=|<=|>|<|~)\s*([0-9.]+)',expected)
        if not m:raise ValueError('Unknown numeric expectation: '+str(expected))
        op,n=m.groups();n=float(n)
        return result({'>=':v>=n,'<=':v<=n,'>':v>n,'<':v<n,'~':abs(v-n)<=tolerance}[op])
    if key.endswith('_pattern'):
        name={'technique_id_pattern':'technique_id','recommended_technique_pattern':'recommended_technique'}[key]
        v=field(name)
        if name=='technique_id' and isinstance(actual,dict) and 'phases' in actual:
            phases=actual['phases'];return result(isinstance(phases,list) and bool(phases) and all(isinstance(p,dict) and isinstance(p.get('technique'),str) and re.fullmatch(expected,p['technique']) for p in phases))
        return result(isinstance(v,str) and re.fullmatch(expected,v) is not None)
    if key in {'required_fields','has_fields'}:return result(isinstance(actual,dict) and all(k in actual and nonempty(actual[k]) for k in expected))
    if key=='priority_targets_is_list':return result(isinstance(field('priority_targets'),list))
    if key=='priority_targets_min_length':return result(isinstance(field('priority_targets'),list) and len(field('priority_targets'))>=expected)
    if key=='opening_move_has_tool':return result(isinstance(field('opening_move'),dict) and nonempty(field('opening_move').get('tool')))
    if key in {'topology_insight_not_empty','stop_reason_not_empty'}:return result(nonempty(field(key.removesuffix('_not_empty'))))
    if key=='outcome_summary_contains':
        summary=field('outcome_summary');return result(isinstance(summary,str) and any(word.casefold() in summary.casefold() for word in expected))
    if key=='causal_chain_starts_at':return result(isinstance(field('causal_chain'),list) and bool(field('causal_chain')) and field('causal_chain')[0]==expected)
    if key=='causal_chain_min_length':return result(isinstance(field('causal_chain'),list) and len(field('causal_chain'))>=expected)
    if key=='campaign_decision_in':return result(field('campaign_decision') in expected)
    if key=='stop_or_tool_selected':return result(field('stop') is True or nonempty(field('tool')))
    if key in {'tool_not_empty','tool_must_not_be_empty'}:return result(nonempty(field('tool' if key=='tool_not_empty' else 'tool_name')))
    if key in {'tool_not_in','tool_not_equal','tool_must_not_be','tool_must_not_be_in','tool_must_be_in','tool_must_be_in_or_empty','tool_in_available_or_empty','must_not_select'}:
        v=field('tool_name') if field('tool_name') is not None else field('tool')
        if key in {'tool_must_be_in_or_empty','tool_in_available_or_empty'}:return result(v is not None and (v=='' or v in expected))
        if v is None:return result(False)
        if key=='tool_must_be_in':return result(v in expected)
        return result(v not in expected if isinstance(expected,list) else v!=expected)
    if key=='to_one_of':return result(field('to') in expected)
    phases=field('phases')
    if key=='phases_count':return result(isinstance(phases,list) and len(phases)==expected)
    if key in {'all_rounds_present','must_have_all_rounds'}:return result(isinstance(phases,list) and sorted(p.get('round') for p in phases if isinstance(p,dict) and type(p.get('round')) is int)==sorted(expected))
    if key=='required_phase_fields':return result(isinstance(phases,list) and bool(phases) and all(isinstance(p,dict) and all(nonempty(p.get(k)) for k in expected) for p in phases))
    if key=='all_tools_in_available':return result(isinstance(phases,list) and bool(phases) and all(isinstance(p,dict) and p.get('tool') in expected for p in phases))
    raise ValueError('Unimplemented expected field: '+key)


def evaluate_case(case,prediction,context=None,tolerance=.02):
    context=context or {};nodes=prediction.get('nodes',{});final=prediction.get('final',{});results=[]
    if not isinstance(nodes,dict):nodes={}
    if not isinstance(final,dict):final={}
    for stage,expectations in case.get('expected_llm_outputs',{}).items():
        for key,expected in expectations.items():
            status,reason=check(key,expected,nodes.get(stage,{}),context,tolerance)
            results.append({'scope':stage,'field':key,'status':status,'reason':reason})
    for key,expected in case.get('expected_final',{}).items():
        status,reason=check(key,expected,final,context,tolerance);results.append({'scope':'final','field':key,'status':status,'reason':reason})
    # An agent cannot select a tool outside input availability, regardless of fixture-specific assertions.
    available=case.get('input',{}).get('tools_available')
    if isinstance(available,list):
        selected=[]
        for scope,value in [('final',final),*nodes.items()]:
            if not isinstance(value,dict):continue
            for name in ['tool','tool_name']:
                if name in value and nonempty(value[name]):selected.append(value[name])
            if isinstance(value.get('phases'),list):
                selected.extend(p.get('tool') for p in value['phases'] if isinstance(p,dict) and nonempty(p.get('tool')))
        valid=bool(nodes or final) and all(tool in available for tool in selected)
        results.append({'scope':'input','field':'input_tool_availability','status':'pass' if valid else 'fail','reason':'Fixed case-level guard over all supplied tools; absent response fails. No tool execution.'})
    scored=[x for x in results if x['status'] in {'pass','fail'}];unscored=[x for x in results if x['status']=='unscored']
    return {'id':case['id'],'predicate_passes':sum(x['status']=='pass' for x in scored),'scored_predicates':len(scored),'unscored_predicates':len(unscored),'all_scored_pass':bool(scored) and all(x['status']=='pass' for x in scored),'fully_covered_pass':bool(scored) and not unscored and all(x['status']=='pass' for x in scored),'checks':results}


def evaluate(predictions,root=ROOT,contexts=None):
    supplied={};known={t['id'] for d,t in cases(root)}
    for item in predictions:
        if item['id'] in supplied:raise ValueError('Duplicate prediction ID '+item['id'])
        if item['id'] not in known:raise ValueError('Unknown prediction ID '+item['id'])
        supplied[item['id']]=item
    results=[evaluate_case(t,supplied.get(t['id'],{}),(contexts or {}).get(t['id'],{})) for d,t in cases(root)]
    per_family=[]
    for group in sorted({x['id'].split('-T')[0] for x in results}):
        rs=[x for x in results if x['id'].startswith(group+'-T')]
        per_family.append({'scenario':group,'cases':len(rs),'all_scored_pass_rate':sum(x['all_scored_pass'] for x in rs)/len(rs),'fully_covered_pass_rate':sum(x['fully_covered_pass'] for x in rs)/len(rs)})
    statuses=collections.Counter(x['status'] for r in results for x in r['checks']);den=statuses['pass']+statuses['fail']
    return {'specification':SPEC_VERSION,'approximate_risk_tolerance':.02,'keyword_rule':'any listed substring, case insensitive; lexical proxy only','cases':len(results),'missing_predictions':len(known-set(supplied)),'predicate_statuses':dict(statuses),'micro_predicate_pass_rate':statuses['pass']/den if den else None,'macro_family_all_scored_pass_rate':sum(x['all_scored_pass_rate'] for x in per_family)/len(per_family),'family_results':per_family,'results':results,'boundary':'Output-constraint evaluation only; notes are documentation and context-dependent assertions remain unscored without reviewed context. No tool or physical action is performed.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--predictions',type=pathlib.Path,required=True);p.add_argument('--contexts',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
    report=evaluate(json.loads(a.predictions.read_text()),contexts=json.loads(a.contexts.read_text()) if a.contexts else None);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['results','family_results']},indent=2))
if __name__=='__main__':main()
