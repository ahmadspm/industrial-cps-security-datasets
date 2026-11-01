#!/usr/bin/env python3
"""Validate the curated release using only the Python standard library."""
import ast,collections,csv,gzip,hashlib,ipaddress,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
errors=[];checks={}
def table(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf-8-sig',newline='') as f:yield from csv.DictReader(f)
def paths(name):
    files=sorted((ROOT/'data/knowledge_graph').glob(name+'.csv*'))+sorted((ROOT/'data/knowledge_graph').glob(name+'_*.csv.gz'))
    return [p for p in files if p.suffix=='.gz' or not pathlib.Path(str(p)+'.gz').exists()]
nodekeys=json.loads((ROOT/'metadata/graph_node_keys.json').read_text());ids={};node_rows=0
for name,key in nodekeys.items():
    values=[]
    for p in paths(name):
        for row in table(p):values.append(row[key]);node_rows+=1
    ids[name]=set(values)
    if len(values)!=len(ids[name]):errors.append('Duplicate node identifiers: '+name)
rules=json.loads((ROOT/'metadata/graph_relation_rules.json').read_text());edge_rows=unmatched=0
for name,columns in rules.items():
    for p in paths(name):
        for row in table(p):
            edge_rows+=1
            if any(row[column] not in ids[target] for column,target in columns):unmatched+=1
if unmatched:errors.append('Unmatched released graph references: '+str(unmatched))
checks.update(graph_nodes=node_rows,graph_edges=edge_rows,unmatched_released_graph_edges=unmatched)
train=json.loads((ROOT/'data/training/fine_tuning.json').read_text());unique={json.dumps(r,sort_keys=True) for r in train}
if len(train)!=len(unique):errors.append('Training duplicates remain')
preferred=json.loads((ROOT/'data/training/release_compatible.json').read_text())
if len({r['output'] for r in preferred})!=len(preferred):errors.append('Compatible query duplicates remain')
if not preferred or any(not r.get('expected_ids') for r in preferred):errors.append('Compatible queries need nonempty reference results')
checks['release_compatible_queries']=len(preferred)
checks['unique_training_records']=len(unique)
bench={}
for p in (ROOT/'data/benchmarks').glob('*.csv*'):
    if p.suffix!='.gz' and pathlib.Path(str(p)+'.gz').exists():continue
    rows=list(table(p));groups=collections.defaultdict(set)
    for r in rows:
        key=re.sub(r'\s+',' ',r['Description'].strip()).casefold();groups[key].add(r['GT'].strip().casefold())
        if not r['GT'].strip():errors.append('Missing reference label: '+p.name)
    if any(len(v)>1 for v in groups.values()):errors.append('Ambiguous reference-description group remains: '+p.name)
    bench[p.name]=len(rows)
checks['benchmark_records']=bench
scenarios=0
for p in (ROOT/'data/agent_scenarios').glob('*.json'):
    r=json.loads(p.read_text());scenarios+=len(r['tests'])
    if len(r['tests'])!=r['test_count']:errors.append('Scenario case count mismatch')
checks['expected_decision_cases']=scenarios
def safe_value(v):
    if v is None or isinstance(v,(bool,int,float)):return True
    if isinstance(v,list):return all(safe_value(x) for x in v)
    return bool(re.fullmatch(r'state_[0-9a-f]{16}',v))
event_path=ROOT/'data/operational/event_features.jsonl.gz';count=0;trace_ids=set()
with gzip.open(event_path,'rt') as f:
    for line in f:
        row=json.loads(line);count+=1;trace_ids.add(row['trace_id'])
        if not safe_value(row['value']) or not safe_value(row['previous_value']):errors.append('Uncontrolled operational text value')
checks['operational_feature_records']=count
checks['operational_distinct_trace_ids']=len(trace_ids)
if len(trace_ids)!=27:errors.append('Released operational trace ID count changed')
ip=re.compile(r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])');allowed=ipaddress.ip_network('198.18.0.0/15');secret=re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:ghp_|github_pat_|hf_)[A-Za-z0-9_]{20,}|\bsk-[A-Za-z0-9_-]{24,}')
for p in ROOT.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in ['.git','__pycache__']):continue
    if p.suffix=='.py':
        try:ast.parse(p.read_text())
        except SyntaxError:errors.append('Python syntax error: '+str(p.relative_to(ROOT)))
    if p.suffix=='.gz':
        with gzip.open(p,'rt',errors='replace') as f:text=f.read()
    else:
        try:text=p.read_text()
        except UnicodeDecodeError:continue
    for m in ip.finditer(text):
        try:address=ipaddress.ip_address(m.group())
        except ValueError:continue
        if address not in allowed and not address.is_loopback and str(address) not in ['0.0.0.0','255.255.255.255']:errors.append('Unapproved IPv4 literal in '+str(p.relative_to(ROOT)))
    if secret.search(text):errors.append('High-confidence credential pattern in '+str(p.relative_to(ROOT)))
manifest=ROOT/'metadata/checksums.csv'
if manifest.exists():
    for row in table(manifest):
        p=ROOT/row['path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('Checksum mismatch: '+row['path'])
result={'checks':checks,'errors':sorted(set(errors)),'passed':not errors,'boundary':'Structural, duplicate, identifier-pattern and integrity checks; not semantic or physical validation'}
print(json.dumps(result,indent=2));raise SystemExit(0 if not errors else 1)
