"""Execute the connected task from source tables without reading reference answers."""
import csv,gzip,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]

def retrieve(root=ROOT):
    links={}
    with gzip.open(root/'data/knowledge_graph/HAS_VULNERABILITY.csv.gz','rt') as f:
        for row in csv.DictReader(f):links.setdefault(row['product_id'],set()).add(row['cve_id'])
    questions=json.loads((root/'evaluation/connected_questions.json').read_text())
    return [{'id':q['id'],'cve_ids':sorted(links.get(q['asset_id'],set())),'decision':'review_required' if links.get(q['asset_id']) else 'abstain','confirmed_vulnerable':False,'action_authorized':False} for q in questions]
if __name__=='__main__':print(json.dumps(retrieve(),indent=2))
