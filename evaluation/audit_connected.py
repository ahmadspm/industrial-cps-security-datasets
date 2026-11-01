"""Second implementation: source-level checks of generated evidence. Not human sign-off."""
import csv,gzip,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]

def audit(root=ROOT):
    expected=json.loads((root/'evaluation/connected_reference.json').read_text());questions=json.loads((root/'evaluation/connected_questions.json').read_text());assert len({q['id'] for q in questions})==len(questions)==len(expected)==94
    with (root/'data/inventory/assets-Master.csv').open() as f:assets={r['asset_id'] for r in csv.DictReader(f)}
    with (root/'data/knowledge_graph/product_node.csv').open() as f:products={r['product_id'] for r in csv.DictReader(f)}
    assert assets<=products
    tables={}
    for q in questions:
        for e in q['evidence']:
            path=e['file']
            if path not in tables:
                with (gzip.open(root/path,'rt') if path.endswith('.gz') else (root/path).open()) as f:
                    reader=csv.DictReader(f);cols=reader.fieldnames
                    tables[path]={(r[cols[0]],r[cols[1]]) for r in reader}
            assert (e['source'],e['target']) in tables[path],e
    with gzip.open(root/'data/knowledge_graph/HAS_VULNERABILITY.csv.gz','rt') as f:pairs={(r['product_id'],r['cve_id']) for r in csv.DictReader(f)}
    byid={q['id']:q for q in questions}
    for answer in expected:
        q=byid[answer['id']];assert q['asset_id'] in assets
        actual=sorted(cve for asset,cve in pairs if asset==q['asset_id'])
        assert answer['cve_ids']==actual
        assert answer['decision']==('review_required' if actual else 'abstain')
        assert answer['confirmed_vulnerable'] is False and answer['action_authorized'] is False
    return {'status':'passed','cases_checked':len(expected),'checks':['inventory-to-product identity','every evidence pair exists in named source table','all linked CVEs included','no unsupported confirmation or action permission'],'method':'Separate source-table implementation; shares source data with generator and is not an independent scientific review.','human_review':'pending','input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['evaluation/connected_questions.json','evaluation/connected_reference.json']}}
if __name__=='__main__':
    r=audit();(ROOT/'reports/connected_source_audit.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,indent=2))
