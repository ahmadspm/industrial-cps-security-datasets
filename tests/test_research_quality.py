import collections,copy,importlib.util,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'evaluation')]
from research_quality import dataset,compile_query
from agent_evaluator import check,cases,evaluate,evaluate_case
from connected_evaluator import evaluate as connected
from run_connected import retrieve
from audit_connected import audit

class ResearchQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.keys,cls.rules,cls.nodes,cls.edges=dataset(ROOT)
    def test_compatible_queries_recompute_expected_results(self):
        records=json.loads((ROOT/'data/training/release_compatible.json').read_text())
        self.assertTrue(records)
        # Reverse canonical exact-ID syntax to the restricted source grammar to independently exercise traversal.
        import re
        for row in records:
            q=row['output'];m=re.fullmatch(r"MATCH (.+) WHERE (\w+)\.(\w+) = '([^']+)' RETURN DISTINCT (\w+)\.\w+ AS id ORDER BY id( LIMIT \d+)?",q)
            self.assertIsNotNone(m)
            pattern,var,prop,identifier,returned,limit=m.groups()
            source=f"MATCH {pattern} WHERE toLower({var}.{prop}) CONTAINS toLower('{identifier}') RETURN {returned}"+(limit or '')
            result=compile_query(source,self.keys,self.rules,self.nodes,self.edges)
            self.assertEqual(result['answers'],row['expected_ids'])
    def test_unsupported_relation_not_invented(self):
        q="MATCH (cve:CVE)-[:HAS_POSSIBLE_CWE]->(cwe:CWE) WHERE toLower(cve.cve_id) CONTAINS toLower('CVE-2024-10048') RETURN cwe"
        with self.assertRaisesRegex(ValueError,'relationship_absent'):compile_query(q,self.keys,self.rules,self.nodes,self.edges)
    def test_missing_identifier_excluded(self):
        q="MATCH (cve:CVE) WHERE toLower(cve.cve_id) CONTAINS toLower('CVE-9999-99999') RETURN cve"
        with self.assertRaisesRegex(ValueError,'identifier_absent'):compile_query(q,self.keys,self.rules,self.nodes,self.edges)
    def test_all_400_agent_cases_accounted_for(self):
        r=evaluate([])
        self.assertEqual(r['cases'],400);self.assertEqual(r['missing_predictions'],400)
        self.assertEqual(sum(x['fully_covered_pass'] for x in r['results']),0)
        self.assertEqual(len(r['family_results']),20)
    def test_missing_forbidden_tool_is_not_pass(self):
        self.assertEqual(check('tool_must_not_be','GhostTool',{}, {},.02)[0],'fail')
    def test_risk_tolerance_and_boolean_type(self):
        self.assertEqual(check('detection_risk','~0.72',{'detection_risk':.73},{},.02)[0],'pass')
        self.assertEqual(check('detection_risk','~0.72',{'detection_risk':.80},{},.02)[0],'fail')
        self.assertEqual(check('detection_risk','>= 0.86',{'detection_risk':True},{},.02)[0],'fail')
        self.assertEqual(check('stop',True,{'stop':1},{},.02)[0],'fail')
    def test_context_checks_never_silently_pass(self):
        self.assertEqual(check('all_hops_in_topology',True,{'causal_chain':['A']},{},.02)[0],'unscored')
        self.assertEqual(check('all_hops_in_topology',True,{'causal_chain':['X']},{'topology_nodes':['A']},.02)[0],'fail')
        self.assertEqual(check('must_match_target_category',True,{}, {},.02)[0],'unscored')
    def test_tool_availability_enforced(self):
        t=next(t for _,t in cases() if isinstance(t['input'].get('tools_available'),list))
        r=evaluate_case(t,{'final':{'tool':'GhostTool'}})
        self.assertTrue(any(x['field']=='input_tool_availability' and x['status']=='fail' for x in r['checks']))
    def test_plan_fields_and_rounds(self):
        p={'phases':[{'round':1,'tool':'A','target':'X','technique':'T0800','purpose':'observe'},{'round':2,'tool':'A','target':'X','technique':'T0800','purpose':'observe'}]}
        for k,v in [('required_phase_fields',['round','tool','target','technique','purpose']),('must_have_all_rounds',[1,2]),('all_tools_in_available',['A']),('technique_id_pattern',r'^T\d{4}(\.\d+)*$')]:self.assertEqual(check(k,v,p,{},.02)[0],'pass')
        p['phases'][0]['tool']='B';self.assertEqual(check('all_tools_in_available',['A'],p,{},.02)[0],'fail')
    def test_duplicate_and_unknown_prediction_ids_rejected(self):
        tid=cases()[0][1]['id']
        with self.assertRaises(ValueError):evaluate([{'id':tid},{'id':tid}])
        with self.assertRaises(ValueError):evaluate([{'id':'invalid'}])
    def test_connected_retriever_and_adversarial_boundary(self):
        ps=retrieve(ROOT);self.assertEqual(connected(ps)['overall']['all_pass_rate'],1)
        ps[0]['action_authorized']=True
        self.assertLess(connected(ps)['overall']['all_pass_rate'],1)
        ps[0]['cve_ids']=['CVE-9999-99999'];self.assertGreater(connected(ps)['overall']['unsupported_id_count'],0)
    def test_separate_connected_source_audit(self):self.assertEqual(audit()['status'],'passed')
    def test_malformed_stage_containers_fail_cleanly(self):
        t=cases()[0][1]
        result=evaluate_case(t,{'nodes':[],'final':None})
        self.assertFalse(result['all_scored_pass'])
    def test_unknown_predicate_raises(self):
        with self.assertRaises(ValueError):check('new_unimplemented_constraint',True,{}, {},.02)
    def test_manifest_matches_trace_rows(self):
        import csv,gzip
        with (ROOT/'metadata/trace_manifest.csv').open() as f:manifest=list(csv.DictReader(f))
        with gzip.open(ROOT/'data/operational/event_features.jsonl.gz','rt') as f:counts=collections.Counter(json.loads(l)['trace_id'] for l in f)
        self.assertEqual({r['trace_id']:int(r['event_count']) for r in manifest},dict(counts))

if __name__=='__main__':unittest.main()
