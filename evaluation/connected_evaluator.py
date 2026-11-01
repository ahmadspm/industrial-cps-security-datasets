"""Score linked-CVE retrieval and explicit boundaries against source-derived references."""
import argparse,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]

def evaluate(predictions,root=ROOT):
    expected=json.loads((root/'evaluation/connected_reference.json').read_text());known={x['id'] for x in expected};byid={}
    for row in predictions:
        if row['id'] in byid or row['id'] not in known:raise ValueError('Duplicate or unknown prediction ID')
        byid[row['id']]=row
    rows=[]
    for ref in expected:
        p=byid.get(ref['id'],{});ids=p.get('cve_ids');valid=isinstance(ids,list) and all(isinstance(i,str) for i in ids) and len(ids)==len(set(ids))
        got=set(ids) if valid else set();gold=set(ref['cve_ids']);boundaries=p.get('confirmed_vulnerable') is False and p.get('action_authorized') is False
        rows.append({'id':ref['id'],'has_reference_links':bool(gold),'missing_prediction':ref['id'] not in byid,'valid_id_list':valid,'exact_cve_match':valid and got==gold,'correct_decision':p.get('decision')==ref['decision'],'correct_boundaries':boundaries,'unsupported_ids':len(got-gold),'reference_ids':len(gold),'retrieved_reference_ids':len(got&gold),'all_pass':valid and got==gold and boundaries and p.get('decision')==ref['decision']})
    def summary(rs):return {'cases':len(rs),'exact_cve_match_rate':sum(x['exact_cve_match'] for x in rs)/len(rs) if rs else None,'all_pass_rate':sum(x['all_pass'] for x in rs)/len(rs) if rs else None,'unsupported_id_count':sum(x['unsupported_ids'] for x in rs)}
    return {'overall':summary(rows),'linked_cases':summary([x for x in rows if x['has_reference_links']]),'no_link_cases':summary([x for x in rows if not x['has_reference_links']]),'missing_predictions':sum(x['missing_prediction'] for x in rows),'results':rows,'boundary':'Agreement with released mappings; physical applicability and independent expert review remain unverified.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--predictions',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();r=evaluate(json.loads(a.predictions.read_text()));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['overall'],indent=2))
