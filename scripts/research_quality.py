#!/usr/bin/env python3
"""Build reproducible compatibility, connectivity, joins, trace and connected-task artifacts."""
import argparse, collections, csv, gzip, hashlib, json, pathlib, re, statistics
ROOT=pathlib.Path(__file__).resolve().parents[1]
LABELS={'CVE':'cve_node','CWE':'cwe_node','CAPEC':'capec_node','Technique':'technique_node','Group':'group_node','Malware':'malware_node','Mitigation':'mitigation_node','Product':'product_node','CWEMitigation':'cweMitigation_node','CWEConsequence':'cweConsequence_node','Zone':'zone_node'}

def paths(root,name):
    base=root/'data/knowledge_graph'
    ps=sorted(base.glob(name+'.csv*'))+sorted(base.glob(name+'_*.csv.gz'))
    return [p for p in ps if p.suffix=='.gz' or not pathlib.Path(str(p)+'.gz').exists()]

def table(p):
    with (gzip.open(p,'rt',newline='') if p.suffix=='.gz' else p.open(newline='')) as f:return list(csv.DictReader(f))

def dump(p,value):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def csvout(p,rows,fields):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def dataset(root):
    keys=json.loads((root/'metadata/graph_node_keys.json').read_text());rules=json.loads((root/'metadata/graph_relation_rules.json').read_text())
    nodes={n:{row[k]:row for p in paths(root,n) for row in table(p)} for n,k in keys.items()}
    edges={n:[row for p in paths(root,n) for row in table(p)] for n in rules}
    return keys,rules,nodes,edges

def compile_query(query,keys,rules,nodes,edges):
    """Conservative exact-ID grammar. Not a general Cypher parser or Neo4j execution."""
    q=' '.join(query.strip().rstrip(';').split())
    m=re.fullmatch(r'MATCH (.+?) WHERE toLower\((\w+)\.(\w+)\) CONTAINS toLower\(([\'\"])(.*?)\4\) RETURN (\w+)(?: LIMIT (\d+))?',q)
    if not m:raise ValueError('outside_supported_query_grammar')
    pattern,where_var,prop,_,literal,returned,limit=m.groups()
    node_tokens=list(re.finditer(r'\((\w+):(\w+)\)',pattern))
    if not node_tokens or pattern[:node_tokens[0].start()] or pattern[node_tokens[-1].end():]:raise ValueError('unrecognized_pattern')
    if len({n.group(1) for n in node_tokens})!=len(node_tokens):raise ValueError('reused_variables')
    bindings={n.group(1):LABELS.get(n.group(2)) for n in node_tokens}
    if any(v is None for v in bindings.values()):raise ValueError('unsupported_label')
    if where_var not in bindings or returned not in bindings:raise ValueError('unbound_variable')
    key=keys[bindings[where_var]]
    aliases={'cwe_node':'cwe_id','capec_node':'capec_id','technique_node':'technique_id','mitigation_node':'mitigation_id','group_node':'group_id','malware_node':'malware_id'}
    if prop not in {key,aliases.get(bindings[where_var])}:raise ValueError('missing_or_nonidentifier_property')
    # Legacy property names may be normalized only when the literal exactly identifies an existing node.
    if literal not in nodes[bindings[where_var]]:raise ValueError('identifier_absent_from_release')
    if bindings[where_var]=='product_node' and not literal.startswith('entity_'):raise ValueError('unsupported_product_identity')
    normalized=pattern;joins=[]
    for left,right in zip(node_tokens,node_tokens[1:]):
        between=pattern[left.end():right.start()];rm=re.fullmatch(r'(-|<-)\[:(\w+)\](->|-)',between)
        if not rm:raise ValueError('unsupported_relationship_pattern')
        before,rel,after=rm.groups()
        if rel not in rules:raise ValueError('relationship_absent:'+rel)
        cols=rules[rel];types=[bindings[left.group(1)],bindings[right.group(1)]]
        if len(cols)!=2:raise ValueError('nonbinary_relation')
        directed=before=='-' and after=='->';reverse=before=='<-' and after=='-'
        if not directed and not reverse:raise ValueError('undirected_relation_outside_grammar')
        expected=[cols[0][1],cols[1][1]] if directed else [cols[1][1],cols[0][1]]
        # HAS_CAPEC is stored CAPEC -> CWE. Normalize only this documented reversed legacy pattern.
        if types!=expected:
            if rel=='HAS_CAPEC' and types==expected[::-1]:
                directed=not directed;reverse=not reverse
                normalized=normalized.replace(between,('-[:'+rel+']->') if directed else ('<-[:'+rel+']-'),1)
            else:raise ValueError('relationship_endpoint_type_mismatch:'+rel)
        joins.append((left.group(1),right.group(1),rel,directed))
    current=[{where_var:literal}]
    pending=joins[:]
    # Enumerate a bounded path from the constrained identifier; all supported patterns are short chains.
    while pending:
        progress=False
        for join in pending[:]:
            a,b,rel,directed=join;cols=rules[rel];ca,cb=(cols[0][0],cols[1][0]) if directed else (cols[1][0],cols[0][0])
            if not current or a in current[0] or b in current[0]:
                new=[]
                index=collections.defaultdict(list)
                known=a if current and a in current[0] else b
                kc=ca if known==a else cb
                for edge in edges[rel]:index[edge[kc]].append(edge)
                for binding in current:
                    for edge in index.get(binding.get(known),[]):
                        if (a not in binding or binding[a]==edge[ca]) and (b not in binding or binding[b]==edge[cb]):new.append({**binding,a:edge[ca],b:edge[cb]})
                current=new;pending.remove(join);progress=True
        if not progress:raise ValueError('disconnected_pattern')
    answers=sorted({b[returned] for b in current if returned in b})
    # Canonical new instruction makes the exact-ID semantics explicit; source instruction remains in audit.
    out=f"MATCH {normalized} WHERE {where_var}.{key} = '{literal}' RETURN DISTINCT {returned}.{keys[bindings[returned]]} AS id ORDER BY id"
    if limit:out+=' LIMIT '+limit;answers=answers[:int(limit)]
    return {'query':out,'answers':answers,'identifier':literal,'return_type':bindings[returned]}

def build(root):
    keys,rules,nodes,edges=dataset(root);reports=root/'reports';reports.mkdir(exist_ok=True)
    # Compatibility audit preserves the legacy file byte-for-byte.
    source=root/'data/training/fine_tuning.json';legacy=json.loads(source.read_text());compatible=[];audit=[];seen=set()
    for ordinal,record in enumerate(legacy,1):
        accepted=0;issues=[]
        for qi,q in enumerate(re.split(r'\s*---\s*',record['output']),1):
            try:
                item=compile_query(q,keys,rules,nodes,edges)
                if not item['answers']:raise ValueError('no_supported_result_in_snapshot')
                instruction=f"Using the released graph, return sorted distinct {item['return_type']} identifiers for {item['identifier']} following this typed path: "+item['query'].split(' WHERE ')[0][6:]+'.'
                signature=item['query']
                if signature not in seen:
                    compatible.append({'instruction':instruction,'output':item['query'],'expected_ids':item['answers'],'source_record_ordinal':ordinal,'source_query_ordinal':qi,'split_group':item['identifier']});seen.add(signature)
                accepted+=1
            except ValueError as e:issues.append({'query_ordinal':qi,'reason':str(e)})
        audit.append({'source_record_ordinal':ordinal,'accepted_queries':accepted,'issues':issues})
    dump(root/'data/training/release_compatible.json',compatible)
    dump(reports/'training_compatibility.json',{'legacy_records':len(legacy),'legacy_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'compatible_unique_queries':len(compatible),'source_records_with_accepted_query':sum(x['accepted_queries']>0 for x in audit),'validation':'Restricted exact-ID grammar, property/type/direction checks and reference-table evaluation. Engine-specific execution is outside this check.','transformations':['canonical identifier property','exact identifier equality instead of substring matching','documented HAS_CAPEC direction correction','new instruction describes retained query, not removed alternatives','deterministic DISTINCT/ORDER BY and source LIMIT','exclude unsupported, empty-result and duplicate queries'],'records':audit})
    # Connectivity by typed node identity, including isolated nodes.
    ids={(n,k):i for i,(n,k) in enumerate((n,k) for n,values in nodes.items() for k in values)}
    def graphstats(include_synthetic):
        parent=list(range(len(ids)));size=[1]*len(ids);incident=collections.defaultdict(set);total=0
        def find(i):
            while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
            return i
        for rel,rs in edges.items():
            if not include_synthetic and rel in {'ATTACKABLE','ATTACKABLE2'}:continue
            (ca,na),(cb,nb)=rules[rel]
            for row in rs:
                a=(na,row[ca]);b=(nb,row[cb]);incident[na].add(row[ca]);incident[nb].add(row[cb]);total+=1
                x,y=find(ids[a]),find(ids[b])
                if x!=y:
                    if size[x]<size[y]:x,y=y,x
                    parent[y]=x;size[x]+=size[y]
        components=collections.Counter(find(i) for i in range(len(ids)))
        return {'nodes':len(ids),'edge_rows':total,'weak_components':len(components),'largest_component_nodes':max(components.values()),'isolated_nodes':sum(len(v)-len(incident[n]) for n,v in nodes.items()),'by_type':[{'node_table':n,'nodes':len(v),'incident_nodes':len(incident[n]),'isolated_nodes':len(v)-len(incident[n])} for n,v in nodes.items()]}
    full=graphstats(True);reference=graphstats(False)
    dump(reports/'graph_connectivity.json',{'definition':'Weak connectivity uses undirected projection of declared typed endpoints; row count is not unique endpoint-pair count. Typed identities are not merged across node tables.','all_declared_edges':full,'without_synthetic_attackability':reference,'relations':[{'relation':n,'rows':len(es),'evidence_class':'SYNTHETIC_EDGE' if n in {'ATTACKABLE','ATTACKABLE2'} else 'SOURCE_DERIVED_REFERENCE'} for n,es in edges.items()]})
    csvout(reports/'graph_nodes.csv',full['by_type'],['node_table','nodes','incident_nodes','isolated_nodes'])
    inventory=table(root/'data/inventory/assets-Master.csv');assets={x['asset_id'] for x in inventory};flows=table(root/'data/inventory/Dataflows.csv')
    components=table(root/'data/inventory/components_inventory_Fischertechik-smart-factory.csv')
    joins=[]
    def join(name,left,right,meaning):
        joins.append({'join':name,'left_distinct':len(left),'matched_distinct':len(left&right),'coverage':len(left&right)/len(left) if left else None,'interpretation':meaning})
    join('inventory.asset_id -> product_node.product_id',assets,set(nodes['product_node']),'Exact release-key equality; graph products are the matching namespace, not host nodes.')
    join('inventory.asset_id -> host_node.id',assets,set(nodes['host_node']),'Different namespace; zero overlap is not failed product coverage.')
    join('dataflow endpoints -> inventory.asset_id',{x[k] for x in flows for k in ['src_asset_id','dst_asset_id']},assets,'Endpoint identity coverage, not measured physical communication.')
    join('dataflow endpoints -> product_node.product_id',{x[k] for x in flows for k in ['src_asset_id','dst_asset_id']},set(nodes['product_node']),'Exact release keys.')
    compkey='machine_id' if components and 'machine_id' in components[0] else 'asset_id'
    if components and compkey in components[0]:join('component inventory -> component_node.machine_id',{x[compkey] for x in components},set(nodes['component_node']),'Exact release keys; inspect component schema before physical interpretation.')
    dump(reports/'join_coverage.json',{'joins':joins,'unsupported_joins':['Operational signal IDs have no released equipment/units crosswalk.','Agent scenario target names have no verified mapping to inventory pseudonyms.'],'correction':'The previous host-ID comparison did not test the valid inventory-to-product join.'})
    csvout(root/'metadata/asset_graph_crosswalk.csv',[{'asset_id':a,'graph_node_table':'product_node','graph_id':a,'basis':'exact_release_identifier'} for a in sorted(assets&set(nodes['product_node']))],['asset_id','graph_node_table','graph_id','basis'])
    # Trace metadata: only computed observations and explicitly unknown collection semantics.
    traces=collections.defaultdict(list)
    with gzip.open(root/'data/operational/event_features.jsonl.gz','rt') as f:
        for line in f:row=json.loads(line);traces[row['trace_id']].append(row)
    trace_rows=[]
    for tid,es in sorted(traces.items()):
        times=[e['relative_seconds'] for e in es if isinstance(e.get('relative_seconds'),(float,int))];diff=[b-a for a,b in zip(times,times[1:])];ordered=sorted(diff)
        trace_rows.append({'trace_id':tid,'event_count':len(es),'duration_seconds':max(times)-min(times) if times else None,'distinct_signals':len({e['signal_id'] for e in es}),'event_classes':len({e['event_class'] for e in es}),'null_values':sum(e['value'] is None for e in es),'null_ok':sum(e['ok'] is None for e in es),'negative_time_steps':sum(d<0 for d in diff),'duplicate_time_steps':sum(d==0 for d in diff),'median_event_interval_seconds':statistics.median(ordered) if ordered else None,'short_trace':len(es)<3,'collection_mode':'not_documented_in_public_source','physical_process':'not_documented','signal_units':'not_available','attack_labels':'not_available','time_basis':'relative_per_trace','interval_interpretation':'event spacing; not a uniform sensor sampling period'})
    csvout(root/'metadata/trace_manifest.csv',trace_rows,list(trace_rows[0]))
    dump(root/'metadata/operational_semantics.json',{'schema_version':'1.0','source':'data/operational/event_features.jsonl.gz','trace_count':len(traces),'event_count':sum(map(len,traces.values())),'collection':{'site':'not_disclosed','collection_mode':'not_verified','absolute_dates':'not_released','process_mapping':'not_available','clock_synchronization':'not_verified'},'fields':{'trace_id':'Release-local sequence group; one source-file group is not necessarily one independent physical experiment.','relative_seconds':'Elapsed time from first parseable source timestamp within trace.','signal_id':'Pseudonym; equality is preserved, physical quantity and units are not supplied.','event_class':'Pseudonymous event category; no attack meaning is inferred.','value':'Typed observed value/state token; unit/range and physical interpretation unknown.','previous_value':'Supplied previous value, not assumed to reconstruct every state transition.','ok':'Source boolean when present; not an attack label.','record_index':'Ordinal in source file; gaps are not automatically packet loss.'},'annotation_scope':'No expert process/attack annotation added. Short traces are flagged, not deleted.'})
    # Connected task: real released joins, no invented vulnerability confirmation or policy permission.
    hv=collections.defaultdict(set);cw=collections.defaultdict(set);mit=collections.defaultdict(set)
    for e in edges['HAS_VULNERABILITY']:hv[e['product_id']].add(e['cve_id'])
    for e in edges['HAS_CWE']:cw[e['cve_id']].add(e['cwe_id'])
    for e in edges['HAS_CWE_MITIGATION']:mit[e['cwe_id']].add(e['id'])
    questions=[];answers=[];packet=[]
    for i,a in enumerate(sorted(assets),1):
        cid=f'CONNECTED-{i:03d}';evidence=[]
        for cve in sorted(hv[a]):
            evidence.append({'relation':'HAS_VULNERABILITY','source':a,'target':cve,'file':'data/knowledge_graph/HAS_VULNERABILITY.csv.gz'})
            for cwe in sorted(cw[cve]):
                evidence.append({'relation':'HAS_CWE','source':cve,'target':cwe,'file':'data/knowledge_graph/HAS_CWE.csv.gz' if (root/'data/knowledge_graph/HAS_CWE.csv.gz').exists() else 'data/knowledge_graph/HAS_CWE.csv'})
                for m in sorted(mit[cwe]):evidence.append({'relation':'HAS_CWE_MITIGATION','source':cwe,'target':m,'file':'data/knowledge_graph/HAS_CWE_MITIGATION.csv'})
        evidence=list({json.dumps(e,sort_keys=True):e for e in evidence}.values())
        questions.append({'id':cid,'asset_id':a,'question':'Return released CVE identifiers linked to this inventory asset. State whether independent vulnerability confirmation or operational action permission is established. If no link exists, abstain.','evidence':evidence})
        answers.append({'id':cid,'cve_ids':sorted(hv[a]),'decision':'review_required' if hv[a] else 'abstain','confirmed_vulnerable':False,'action_authorized':False,'evidence':evidence})
        packet.append({'case_id':cid,'asset_id':a,'expected_cve_ids':'|'.join(sorted(hv[a])),'reviewer_id':'','review_conclusion':'','join_correct':'','source_mapping_supported':'','physical_applicability_verified':'','action_permission_justified':'','comments':''})
    dump(root/'evaluation/connected_questions.json',questions);dump(root/'evaluation/connected_reference.json',answers)
    review_path=root/'evaluation/review_template.csv'
    if review_path.exists():
        old={x['case_id']:x for x in table(review_path)}
        for row in packet:
            previous=old.get(row['case_id'],{})
            for key in ['reviewer_id','review_conclusion','join_correct','source_mapping_supported','physical_applicability_verified','action_permission_justified','comments']:
                if previous.get(key):row[key]=previous[key]
            if previous and previous.get('expected_cve_ids')!=row['expected_cve_ids']:row['review_conclusion']='source_reference_changed'
    csvout(review_path,packet,list(packet[0]))
    report={'task':'inventory -> product -> source-linked CVE -> CWE -> mitigation identifier evidence','cases':len(questions),'assets_with_cve_links':sum(bool(hv[a]) for a in assets),'asset_cve_edge_rows':sum(len(hv[a]) for a in assets),'cases_with_cwe_evidence':sum(any(e['relation']=='HAS_CWE' for e in q['evidence']) for q in questions),'reference_basis':'Released source-table associations; automated consistency checks do not establish physical applicability or expert endorsement.','boundary':'Source mapping is not proof that the physical asset is vulnerable. Mitigation nodes are identifiers only; no actionable control recommendation is inferred.'}
    dump(reports/'connected_task.json',report)
    print(json.dumps({'compatible_queries':len(compatible),'inventory_products':len(assets&set(nodes['product_node'])),'trace_count':len(traces),'connected':report},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=pathlib.Path,default=ROOT);a=p.parse_args();build(a.root)
