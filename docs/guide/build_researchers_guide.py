"""Build the root researcher guide: Python 3, reportlab, DejaVu fonts."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
R=Path(__file__).resolve().parents[2]
for name,file in [('D','DejaVuSans.ttf'),('DB','DejaVuSans-Bold.ttf'),('M','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
W,H=A4; M=45; CW=W-2*M
navy=HexColor('#133047'); teal=HexColor('#087F8C'); pale=HexColor('#EAF4F5'); gray=HexColor('#526575')
c=canvas.Canvas(str(R/'RESEARCHERS_GUIDE.pdf'),pagesize=A4,invariant=1)
c.setTitle('Researcher\'s Guide - Industrial CPS Security Research Datasets')
c.setAuthor('Dr Ahmad Mohsin | Industrial CPS Security Research Datasets')
style=ParagraphStyle('body',fontName='D',fontSize=10,leading=15,textColor=navy,spaceAfter=8)
y=0; page=0

def para(text,size=10):
    global y
    s=ParagraphStyle('p',parent=style,fontSize=size,leading=size*1.5)
    p=Paragraph(text,s); _,h=p.wrap(CW,900); assert y-h>55,(page,y,h,text[:60]);p.drawOn(c,M,y-h);y-=h+9

def title(t):
    global y,page
    if page: c.showPage()
    page+=1;c.setFillColor(teal);c.rect(0,H-10,W,10,fill=1,stroke=0)
    c.setFont('D',8);c.setFillColor(gray);c.drawString(M,H-35,'INDUSTRIAL CPS SECURITY  /  RESEARCH METHODS')
    c.drawRightString(W-M,32,f'{page:02d} / 16');c.drawString(M,32,'Guide v1.0 | 1 November 2026')
    c.bookmarkPage('p'+str(page));c.addOutlineEntry(t,'p'+str(page),0)
    y=H-69
    p=Paragraph(escape(t),ParagraphStyle('t',fontName='DB',fontSize=22,leading=28,textColor=navy));_,h=p.wrap(CW,100);p.drawOn(c,M,y-h);y-=h+19

def sub(t): para('<b>'+t+'</b>',12)
def bullets(items):
    for item in items: para('• '+item)
def code(t):
    global y
    lines=t.splitlines();h=len(lines)*12+20
    assert y-h>55,(page,y,h)
    c.setFillColor(pale);c.roundRect(M,y-h,CW,h,5,fill=1,stroke=0);c.setFillColor(navy);c.setFont('M',7.4)
    for i,l in enumerate(lines):
        assert pdfmetrics.stringWidth(l,'M',7.4)<CW-20,l
        c.drawString(M+10,y-16-i*12,l)
    y-=h+12

def table(rows,widths=None):
    global y
    ts=ParagraphStyle('cell',parent=style,fontSize=8.6,leading=12)
    data=[[Paragraph(str(v),ts) for v in r] for r in rows]
    t=Table(data,colWidths=widths or [CW/len(rows[0])]*len(rows[0]))
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),pale),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,0),1,teal),('LINEBELOW',(0,1),(-1,-1),.3,HexColor('#CCD9DE'))]))
    _,h=t.wrap(CW,900);assert y-h>55,(page,y,h);t.drawOn(c,M,y-h);y-=h+12

def node(cx,cy,text,w=200,h=38):
    c.setFillColor(pale);c.setStrokeColor(teal);c.roundRect(cx-w/2,cy-h/2,w,h,5,fill=1,stroke=1)
    p=Paragraph(text,ParagraphStyle('n',fontName='D',fontSize=9,leading=12,alignment=1,textColor=navy));_,ph=p.wrap(w-12,h);p.drawOn(c,cx-w/2+6,cy-ph/2)
def edge(points,label=None):
    c.setStrokeColor(teal);c.setLineWidth(1.1);p=c.beginPath();p.moveTo(*points[0])
    for x,z in points[1:]:p.lineTo(x,z)
    c.drawPath(p)
    x,z=points[-1];a,b=points[-2];import math
    ang=math.atan2(z-b,x-a);p=c.beginPath();p.moveTo(x,z)
    for delta in [-.45,.45]:p.lineTo(x-6*math.cos(ang+delta),z-6*math.sin(ang+delta));p.moveTo(x,z)
    c.drawPath(p)
    if label:c.setFont('D',7.5);c.setFillColor(gray);c.drawString(points[1][0]+4,points[1][1]+5,label)
def diagram(labels,caption):
    global y
    # A branching comparison, with shared inputs and common evaluation.
    top=y-24; mid=W/2; left=M+115;right=W-M-115
    node(mid,top,labels[0],260);node(mid,top-65,labels[1],260)
    node(left,top-140,labels[2],208,44);node(right,top-140,labels[3],208,44)
    node(mid,top-215,labels[4],300,44);node(mid,top-280,labels[5],300,38)
    edge([(mid,top-19),(mid,top-46)])
    edge([(mid,top-84),(mid,top-103),(left,top-103),(left,top-118)])
    edge([(mid,top-84),(mid,top-103),(right,top-103),(right,top-118)])
    edge([(left,top-162),(left,top-180),(mid,top-180),(mid,top-193)])
    edge([(right,top-162),(right,top-180),(mid,top-180),(mid,top-193)])
    edge([(mid,top-237),(mid,top-261)])
    y=top-310;para(caption,8)

def study(t,question,data,steps,labels,caption,claim):
    title(t);para('<b>Research question.</b> '+question);para('<b>Evidence.</b> '+data)
    para('<b>Design.</b> '+steps);diagram(labels,caption);para('<b>Report.</b> '+claim)

title('Researcher\'s Guide')
para('Industrial CPS Security Research Datasets',18)
para('Practical study designs, reproducible evaluation and nine workflow diagrams for cybersecurity research.',13)
y-=25
sub('Purpose and audience')
para('For researchers studying industrial cyber-physical systems, cyber threat intelligence, knowledge graphs, digital twins and governed AI agents. This manual explains how to form an experiment from the released files and how to keep its conclusions within the available evidence.')
sub('Release examined')
para('Dataset release 1.0.0. Documentation baseline: commit <font face="M" size="8">70804c6d92e4c45ed673ba4d64e6a00a9103c0ea</font>. Guide prepared 1 November 2026 for the repository maintained by Dr Ahmad Mohsin. Freeze the actual commit used in each experiment; later documentation commits may follow this baseline.')
para('<link href="https://github.com/ahmadspm/industrial-cps-security-datasets" color="#087F8C">github.com/ahmadspm/industrial-cps-security-datasets</link>')
sub('How to read the workflows')
para('The diagrams are proposed offline research designs, not results or assertions that every component is implemented. Each compares a baseline with a proposed method or routes evidence through a decision gate. No performance numbers are invented in this guide.')
para('Start with pages 2-4; choose a study on pages 5-12; use pages 13-15 to evaluate and report it. References and article links appear on page 16.')

title('1. Choose the evidence and the question')
table([['Folder / evidence','Release size','Research use / page'],['inventory / structural tables','94 master assets; 53 component records; 120 flows; 6 zones; 5 conduits','Segmentation and exposure / 5'],['knowledge_graph / typed structure','305,167 nodes; 276,420 edges','Link prediction and graph reasoning / 6'],['benchmarks / upstream reference labels','2,047 CTI records','CTI extraction and mapping / 7'],['training / instruction-output examples','358 unique pairs','Query generation and adaptation / 8'],['synthetic / generated assumptions and logs','340 attackability rows; 9,880 protocol rows','Controlled perturbations / 9'],['operational / pseudonymized observations','14,124 events; 29 traces','Sequence and anomaly studies / 10'],['agent_scenarios / expected fixtures','20 scenarios; 400 cases','Governed decision behavior / 11']],[CW*.36,CW*.28,CW*.36])
para('Folder counts are not independent evidence units. Some attackability tables are repeated in the graph and synthetic folders; do not count the same rows as independent replications.')
sub('Evidence classes matter')
para('An observed event is not automatically an attack. A synthetic risk score is an assumption, not a measured compromise probability. A reference answer is not a newly adjudicated label. An expected agent output is a test oracle, not a successful tool execution. Graph referential integrity is not semantic truth.')
para('Read data/README.md, the selected folder README, docs/SCHEMAS.md, docs/DATASET_CARD.md and metadata/licenses.csv before selecting features. Use metadata/provenance.csv and metadata/research_file_map.csv to trace inputs and related research.')

title('2. Obtain, freeze and load the release')
code('git clone https://github.com/ahmadspm/industrial-cps-security-datasets.git\ncd industrial-cps-security-datasets\ngit rev-parse HEAD\npython scripts/validate_release.py')
para('Record the full commit, Python version and file SHA-256 values from metadata/checksums.csv. Run the validator from the repository root. Work in a separate output directory and retain the original compressed inputs unchanged.')
sub('CSV and compressed CSV: standard-library loader')
code('from pathlib import Path\nimport csv, gzip, json\n\ndef rows(path):\n    path = Path(path)\n    opener = gzip.open if path.suffix == ".gz" else open\n    with opener(path, "rt", encoding="utf-8-sig", newline="") as f:\n        yield from csv.DictReader(f)\n\nflows = list(rows("data/inventory/Dataflows.csv"))\ncves = rows("data/knowledge_graph/cve_node_000.csv.gz")\nfirst_cve = next(cves)\nwith gzip.open("data/operational/event_features.jsonl.gz",\n               "rt", encoding="utf-8") as f:\n    first_event = json.loads(next(f))\nwith open("data/training/fine_tuning.json", encoding="utf-8") as f:\n    instruction_pairs = json.load(f)')
para('CSV values load as strings. Convert numeric and boolean columns explicitly from the schema; distinguish missing values from zero. Stream all 15 CVE shards for the full CVE table. Do not load a plain CSV sibling in addition to its compressed release file.')
para('No database service is needed to inspect the data. A graph store, embedding model or LLM is a researcher-selected addition and must be versioned separately.')

title('3. Design an experiment before fitting')
para('Specify one primary question, unit of analysis, eligibility criteria and testable outcome. Select a baseline before inspecting held-out results. Separate data quality checks from the security hypothesis.')
diagram(['Freeze commit, schema and research question','Audit labels, groups and duplicate overlap','Verified target available:<br/>supervised comparison','No verified target:<br/>exploratory or controlled study','Fit on training only; lock evaluation protocol','Report uncertainty, provenance and limitations'],'Workflow 1. Evidence quality determines which evaluation claims are supportable.')
para('Use group-based splits when records share a description, flow, trace, entity or scenario template. Keep related versions and inverse graph facts on the same side of the split. Record exclusions and split identifiers before tuning. Fit transformations only on training data [8].')
para('Use MITRE ATT&amp;CK for ICS as a vocabulary for analyst-reviewed mappings [7]. A technique association does not itself establish that an attack occurred. NIST CSF 2.0 can organize research outcomes; this dataset does not establish compliance [6].')

study('4. Inventory: segmentation and exposure','Can a graph-aware monitoring policy cover important cross-zone flows more efficiently than a simple priority rule?','Use Dataflows.csv with assets-Master.csv, ZONES.csv and zones_conduits.csv. Treat the separate 53-record component inventory as a source requiring explicit mapping.','Check asset/zone keys and join coverage; retain unmatched rows in an audit. Construct a directed asset-flow graph. Declare protocol/port and zone rules. Compare policies under equal sensor or intervention budgets.',['120 declared flows + asset/zone tables','Validate joins; define budget and coverage target','Baseline:<br/>criticality or degree ranking','Proposed:<br/>boundary-aware graph selection','Compare covered flows, cost and uncovered assets','Sensitivity analysis across budgets and missing joins'],'Workflow 2. A shared topology and budget enable a fair monitoring comparison.','Give cross-zone flow coverage, weighted coverage, selected locations and sensitivity to criticality weights. Reachability reflects declared connectivity, not proven exploitability. Removed identities and addresses cannot support deployment-specific claims.')

study('5. Knowledge graph: inference and prioritization','Does a typed graph method recover held-out relations better than a relation-frequency baseline?','Use node and edge CSV/CSV.GZ files with metadata/graph_node_keys.json and graph_relation_rules.json. The release contains 291,577 CVE rows across 15 shards.','Select one relation and a transductive or entity-disjoint task. Split before creating inverse edges, embeddings or derived features. Remove held-out facts and equivalent inverse/derived facts from training. Use type-correct candidates; document negative sampling.',['Typed nodes + declared relation rules','Freeze relation split; remove leakage paths','Baseline:<br/>type-constrained frequency','Proposed:<br/>typed graph model','Evaluate identical candidate sets and filtered ranks','Audit false links and unsupported risk assumptions'],'Workflow 3. Split construction precedes graph feature generation.','Report MRR and Hits@k with candidate counts, or precision/recall on a defined labeled task. Unknown edges are not verified negatives. Zero unmatched endpoints confirms structure only. CVSS/EPSS/KEV attributes are historical snapshots; they are not current risk advice. The graph lacks a full narrative corpus.')

study('6. CTI benchmarks: grounded answers','Does graph grounding improve technique or weakness mapping over the same model without retrieval?','Use 60 CTI-ATE, 996 CTI-RCM and 991 CTI-RCM-2021 records. GT is an upstream reference label. CTIBench is external work by Alam et al. [5], not authored by this repository maintainer.','Use metadata/benchmark_split_groups.csv to keep related descriptions together across files. Hide GT and any direct answer-bearing path from the model input and retrieval index. Freeze prompts and retrieval budget. Normalize output to declared identifier sets; score abstentions explicitly.',['Grouped CTI prompts; hidden reference answers','Freeze model, prompts and allowed evidence','Baseline:<br/>same LLM without retrieval','Proposed:<br/>graph-grounded LLM','Score mapping + evidence support + invalid outputs','Review disagreements; report coverage and abstention'],'Workflow 4. Retrieval gains must be measured independently from answer leakage.','Report exact-set match and micro/macro label precision, recall and F1 as appropriate to the GT representation. Distinguish parsing failures, wrong mappings and unsupported claims. Thirteen records from five conflicting-description groups were excluded during release preparation. Evaluate retained labels rather than assuming universal correctness. CTIBench terms include noncommercial/share-alike conditions.')

study('7. Training pairs: query generation','Can instruction tuning improve schema-valid, semantically correct query generation on unseen query families?','fine_tuning.json contains 358 unique instruction/output pairs after removal of 129 exact duplicates. These are development examples, not an official held-out benchmark.','Group near-duplicate instructions and query templates. Create train/dev/test groups and publish IDs. Reserve the test set before prompt engineering or adaptation. Compare a fixed base model with the adapted model on the same held-out prompts. Validate queries in a read-only sandbox if execution is part of the task.',['358 instruction/output pairs','Group templates; freeze train/dev/test IDs','Baseline:<br/>fixed model and prompt','Proposed:<br/>adapted model, train split only','Parse, check schema, then compare query semantics','Publish errors, split IDs and model configuration'],'Workflow 5. Template separation reduces memorization-based evaluation.','Report syntactic validity, schema validity, execution success and semantic correctness separately. Textual exact match alone may reject equivalent queries. The release does not supply a ready-made hosted database or tuning pipeline. State any external examples, compute budget and model license; test contamination remains a limitation.')

study('8. Synthetic data: controlled anomaly studies','How robust is an anomaly detector to documented timing or volume perturbations under different protocols?','Use 9,880 generated protocol rows and 340 attackability rows. Protocols include OPC UA, Modbus TCP, MQTT/MQTTS, HTTPS, SSH, RDP, S7comm and EtherNet/IP.','Inspect protocol-specific fields before harmonizing. Split by flow or generation/scenario group where supported. Add perturbations to a derived copy with a recorded seed and explicit injection labels. Keep training and test generation groups disjoint. Compare equal-threshold-budget methods.',['Generated protocol records; declared assumptions','Group split; log injection rule and seed','Baseline:<br/>fixed threshold or robust statistic','Proposed:<br/>multivariate anomaly detector','Evaluate derived injection labels; vary severity','Report protocol sensitivity and synthetic-only scope'],'Workflow 6. Labels introduced by the experiment stay separate from released values.','Give precision/recall, PR-AUC and false alarms per declared unit for the controlled task. Status/result fields are not universal malicious labels. ATTACKABLE controlStrength, pExploit, attackCost_min and riskWeight are synthetic assumptions, not empirical compromise outcomes. Test whether a model merely reconstructs the formula used to create its target.')

study('9. Operational traces: sequence research','Can a sequence model identify unusual transitions more consistently than a local transition-frequency baseline?','event_features.jsonl.gz contains 14,124 records in 29 traces. Fields include trace_id, record_index, relative_seconds, event_class, signal_id, value, previous_value and ok.','Order within each trace using record_index and relative time; inspect missing or repeated times. Split whole traces before creating windows. Fit encoders and thresholds on training traces only. If no independent attack labels exist, use descriptive anomaly analysis or separately labeled controlled perturbations.',['29 pseudonymized event traces','Whole-trace split; train-only windows and encoding','Baseline:<br/>transition count or robust threshold','Proposed:<br/>sequence anomaly model','Label gate: verified attacks or exploratory scores?','Report trace-level uncertainty and analyst review'],'Workflow 7. Trace boundaries and label availability constrain inference.','Report unusual-transition rates and review agreement for exploratory studies; use attack metrics only with justified labels. The ok field is not an attack label. Relative clocks are per trace. String values are state_ pseudonyms; units and original signal semantics may be unavailable. Do not infer physical meaning or align cross-trace clocks without evidence.')

study('10. Agent scenarios: governed decisions','Does a policy guard reduce invalid tool selections and missed stop conditions relative to an unguarded decision policy?','Use 400 expected cases across 20 JSON scenarios. Each provides inputs and expected outputs/final decisions. These fixtures are distinct from the historical twin replay suites.','Build a local fixture evaluator that reads tests and records actual outputs. Keep expected fields out of model prompts. Group by scenario family for held-out testing where feasible. Route proposals through tool-catalog, risk and stop checks before any simulated execution. Use deterministic mock tools for comparison.',['Scenario inputs; expected fields hidden','Generate proposal; validate catalog, risk and stop rule','Policy allows:<br/>execute local mock action','Policy rejects:<br/>hold, stop or abstain','Compare actual outputs with expected decisions','Audit invalid tools, stop failures and loop behavior'],'Workflow 8. The decision gate produces auditable allow/hold outcomes.','Report case-level agreement, unsafe-decision rate, stop-condition recall, invalid-tool rate and bounded termination. Specify denominators and oracle limitations. Relevant fixtures cover unavailable tools, hallucinated tools, risk thresholds, loop guards and simulation-only eligibility. Expected outputs are policy references, not evidence of live attacks or operational safety certification.')

study('11. Integrated study: evidence to review','Can traceable evidence improve analyst prioritization compared with an inventory-only ranking?','Combine only demonstrably compatible inventory keys, graph relations and event identifiers. Different sources may not share identities or clocks.','Create a mapping table with source keys, mapping rationale and confidence. Measure join coverage and unresolved records before fusion. Require supported joins for each evidence chain; retain unresolved records for review rather than guessing. Compare the same analyst tasks and time budget.',['Inventory + graph + observation candidates','Check identity/time mapping and evidence provenance','Supported joins:<br/>assemble cited evidence chain','Unsupported joins:<br/>isolate and request review','Human review with inventory-only comparison','Publish join coverage, decision quality and audit trail'],'Workflow 9. Evidence joins are an eligibility gate, not an assumption.','Report supported-join coverage, unsupported-claim rate, analyst agreement and review time with the study protocol. Blind reviewers to method where practical. Do not interpret a connected path as a confirmed attack chain. Explain how pseudonymization and missing semantics affect causal interpretation.')

title('12. Metrics, uncertainty and fair comparisons')
table([['Task','Primary measures','Essential denominator / caveat'],['Label mapping','Exact set match; micro/macro F1','All eligible prompts; disclose parse failures and abstentions'],['Graph ranking','MRR; Hits@k','Candidate set size; filtered-known-fact rule; unknown negatives'],['Anomaly detection','PR-AUC; precision/recall; false alarms','Verified or injected labels; alarms per trace/time unit'],['Inventory optimization','Coverage; cost; uncovered critical flows','Fixed budget and declared weights; unmatched joins'],['Query generation','Syntax, schema and semantic validity','All test prompts; distinguish equivalent queries'],['Agent decisions','Agreement; invalid-tool and stop-failure rates','All eligible cases; independent failures may overlap']],[CW*.24,CW*.32,CW*.44])
para('Define TP, FP and FN for the chosen positive unit. Precision = TP/(TP+FP); recall = TP/(TP+FN); F1 = 2PR/(P+R). State how zero denominators are handled. Accuracy alone can obscure rare-event failure.')
para('Use identical splits, candidate sets, prompts and resource budgets across methods. Report multiple seeds for stochastic training. Bootstrap or summarize at the independent unit, such as trace, description group or scenario family; row-level resampling can understate uncertainty.')
para('Use ablations that answer a question: remove graph evidence, remove policy guards, or replace a learned detector with a simple threshold. Report confidence intervals with method and sample size, practical effect size, failure cases and computational cost. Small numbers of independent groups limit generalization.')

title('13. Replay the reference experiments')
para('The release includes curated historical code under code/twin_reference and an offline orchestration script. Replaying this code checks reproducibility of its included fixtures. It does not train every proposed model in this guide or reproduce every paper claim.')
code('python -m venv .venv\n# Activate this environment using your platform convention.\npython -m pip install -r code/requirements-replay.txt\npython scripts/replay_offline.py --help\npython scripts/replay_offline.py --source-root . --output replay_output')
para('Use a clean environment and retain the installed package versions. Inspect scripts/replay_offline.py and docs/VALIDATION.md for the dependency-directory option and current execution behavior. Keep replay_output outside the published source manifest.')
sub('Interpret the recorded baseline correctly')
para('validation/replay_summary.json records the prior release replay: 24 suites, 285 tests and 10 deterministic experiments. These are recorded validation results for the curated code, not a fresh model benchmark or a pass count for the 400 agent-scenario cases. A new run must report its own result and environment.')
sub('What to retain from a new run')
bullets(['Exact repository commit, input checksums, command line and dependency versions.','Per-suite exit status, test totals, experiment outputs and failure logs.','Any local patches, model/provider configuration, seeds and elapsed time.','A comparison of expected versus actual outputs; explain deviations without overwriting the reference result.'])
para('Offline fixtures do not require physical equipment, model weights, a hosted graph database or live network actions. If a separate study introduces those components, describe them as additional experimental infrastructure and report the authorization and isolation appropriate to that study.')

title('14. Prepare a reusable research package')
sub('Minimal experiment manifest - fill in actual values')
code('study_id: your-study-id\ndataset_commit: FULL_COMMIT_SHA\ninput_paths: [SELECTED_RELEASE_FILES]\ninput_sha256_manifest: metadata/checksums.csv\nquestion: PREDECLARED_QUESTION\nunit_of_analysis: trace_or_group_or_entity\nlabel_source: reference_or_adjudicated_or_injected_or_none\nsplit_ids: path/to/frozen_split_ids.json\nseed: YOUR_SEED\nbaseline: VERSION_AND_CONFIGURATION\nmethod: VERSION_AND_CONFIGURATION\nfit_scope: training_only\nprimary_metric: METRIC_AND_DENOMINATOR\nuncertainty: METHOD_AND_RESAMPLING_UNIT\noutputs: path/to/results\nexclusions_and_limitations: path/to/audit.md')
sub('Before submission or release')
para('State the cybersecurity question and threat assumptions; describe the exact subset and independent sample count; publish group splits and exclusions; separate observations from synthetic or expected values; include baselines and ablations; report all eligible outcomes, uncertainty and failures; and disclose external enrichment, model versions and compute.')
para('Cite this dataset using CITATION.cff and cite the relevant original works [1-5]. Read LICENSE, LICENSE-CODE, THIRD_PARTY_NOTICES.md and metadata/licenses.csv: the compilation, code and third-party subsets have different terms. CTIBench is CC BY-NC-SA 4.0; a top-level badge does not override subset conditions.')
para('Keep pseudonymized identifiers as released. Do not restore private identities or publish unreviewed source material. Share derived labels with their creation protocol and clear provenance. A public dataset paper should describe collection, curation, schema, permitted uses, quality checks and limitations separately from a method paper\'s performance claims.')

title('15. Articles and methodological references')
para('Article attribution and publication status follow docs/RELATED_PUBLICATIONS.md. A related article is context for a research theme, not proof that this curated subset reproduces its results.',9)
refs=[
('[1] BRIDG-ICS: AI-grounded knowledge graphs for intelligent threat analytics in Industry 5.0 cyber-physical systems','Nandiya et al. (2026). Cybersecurity 9, article 167. Published journal article.','https://doi.org/10.1186/s42400-026-00597-0'),
('[2] NeuroGraph: An AI Graph-Driven Neuro-Symbolic Framework for Explainable Threat Reasoning in Advanced Manufacturing','Nandiya et al. (2026). Preprint arXiv:2609.00604. Author reports acceptance in International Journal of Information Security; final journal DOI not supplied.','https://arxiv.org/abs/2609.00604'),
('[3] A Unified Framework for Human-AI Collaboration in Security Operations Centers with Trusted Autonomy','Mohsin et al. (2026). ACM Transactions on Internet Technology. Journal DOI below; preprint arXiv:2505.23397.','https://doi.org/10.1145/3837073'),
('[4] HySecTwin: A Knowledge-Driven Digital Twin Framework Augmented with Hybrid Reasoning for Cyber-Physical Systems','Holmes et al. (2026). Preprint arXiv:2605.11682. Related project: HybridSec-Digital-Twin-CSP-Modelling, ahmadspm on GitHub.','https://arxiv.org/abs/2605.11682'),
('[4a] Autonomous Cyber-Physical Security Assessment in Smart Manufacturing with a Behavioural Digital Twin and Agentic AI','Nandiya, Mohsin, Lohmann, Ekelhart, Sarker and Janicke (n.d.). Author-supplied manuscript; no public article URL or final publication metadata supplied.','https://github.com/ahmadspm/industrial-cps-security-datasets/blob/main/docs/RELATED_PUBLICATIONS.md'),
('[5] CTIBench: A benchmark for evaluating LLMs in cyber threat intelligence','Alam, Bhusal, Nguyen and Rastogi (2024). NeurIPS 37, 50805-50825. External benchmark; not authored by the maintainer.','https://doi.org/10.52202/079017-1607'),
('[6] The NIST Cybersecurity Framework (CSF) 2.0','NIST (2024). CSWP 29. Outcome vocabulary for framing research; not an evaluation certificate.','https://doi.org/10.6028/NIST.CSWP.29'),
('[7] ATT&CK for ICS matrix','MITRE. Technique and tactic vocabulary. Accessed 1 November 2026; preserve the version used for mappings.','https://attack.mitre.org/matrices/ics/'),
('[8] Common pitfalls and recommended practices','scikit-learn documentation. Train/test separation and leakage prevention. Accessed 1 November 2026.','https://scikit-learn.org/stable/common_pitfalls.html')]
for label,desc,url in refs:
    para('<b>'+escape(label)+'</b><br/>'+escape(desc)+'<br/><link href="'+url+'" color="#087F8C">'+escape(url)+'</link>',8.1)
assert page==16,page
c.save()
print(R/'RESEARCHERS_GUIDE.pdf')
