#!/usr/bin/env python3
"""Replay pinned G3 unit suites and deterministic experiments; no live model required."""
import argparse, json, os, pathlib, platform, re, subprocess, sys
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source-root',type=pathlib.Path,required=True,help='Extracted snapshot directory containing G1–G4')
p.add_argument('--output',type=pathlib.Path,required=True)
p.add_argument('--dependency-dir',type=pathlib.Path,help='Optional isolated directory containing declared agent dependencies')
a=p.parse_args();root=a.source_root.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
model=root/'code/twin_reference/digital-twin/Smart-Manufacturing-Behavioural-Digital-Twin/model-driven'
results=[]
for tests in sorted((root/'code/twin_reference').rglob('tests')):
    if not list(tests.glob('test*.py')):continue
    cwd=tests.parent;env=os.environ.copy();paths=[str(cwd/'src')]
    if a.dependency_dir:paths.append(str(a.dependency_dir.resolve()))
    if cwd==model/'v0.3.0':paths.append(str(model/'v0.2.0/runner'))
    env['PYTHONPATH']=os.pathsep.join(paths);env['LANGSMITH_TRACING']='false';env['LANGCHAIN_TRACING_V2']='false'
    cmd=[sys.executable,'-m','unittest','discover','-s','tests','-v']
    run=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,timeout=90)
    text=run.stdout+run.stderr;name=str(cwd.relative_to(root)).replace('/','__')+'.log';(out/name).write_text(text)
    match=re.search(r'Ran (\d+) tests?',text)
    results.append({'suite':str(cwd.relative_to(root)),'returncode':run.returncode,'tests':int(match.group(1)) if match else 0,'log':name})
jobs=[('v0.6.12',['runner/rag_pipeline.py','--output',str(out/'v0.6.12')]),('v0.6.13',['runner/governed_tools.py','--output',str(out/'v0.6.13/report.json')]),('v0.6.14',['runner/end_to_end_agents.py','--output',str(out/'v0.6.14/report.json')])]
for profile in sorted((model/'v0.6.4/scenarios').glob('*.json')):
    jobs.append(('v0.6.4',['runner/impairment_lab.py',str(profile),'--output',str(out/'v0.6.4'/profile.stem)]))
code="import sys;from pathlib import Path;sys.path.insert(0,'runner');from reliability_eval import FixtureProvider,run;run(Path('.').resolve(),output=Path(sys.argv[1]),provider=FixtureProvider())"
jobs.append(('v0.6.11',['-c',code,str(out/'v0.6.11')]))
experiments=[]
for version,args in jobs:
    run=subprocess.run([sys.executable,*args],cwd=model/version,capture_output=True,text=True,timeout=90)
    experiments.append({'version':version,'arguments':args,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
summary={'python':sys.version,'platform':platform.platform(),'suite_count':len(results),'tests':sum(r['tests'] for r in results),'passed_suites':sum(r['returncode']==0 for r in results),'suites':results,'experiments':experiments,'boundary':'Offline unit and deterministic fixture replay only; no live model, Neo4j, or physical system replay'}
(out/'replay_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['suites','experiments']},indent=2))
raise SystemExit(0 if all(r['returncode']==0 for r in results+experiments) else 1)
