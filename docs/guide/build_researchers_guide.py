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
for name,file in [('D','DejaVuSerif.ttf'),('DB','DejaVuSerif-Bold.ttf'),('H','DejaVuSans-Bold.ttf'),('M','DejaVuSansMono.ttf')]:
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
    c.drawRightString(W-M,32,f'{page:02d} / 24');c.drawString(M,32,'Guide v2.1 | 1 November 2026')
    c.bookmarkPage('p'+str(page));c.addOutlineEntry(t,'p'+str(page),0)
    y=H-69
    p=Paragraph(escape(t),ParagraphStyle('t',fontName='H',fontSize=21,leading=28,textColor=navy));_,h=p.wrap(CW,100);p.drawOn(c,M,y-h);y-=h+19

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

def node(cx,cy,text,w=200,h=38,role='input'):
    fills={'input':'#D9EAF8','design':'#FCE6BB','baseline':'#E2E7EC','method':'#CCEBE2','evaluation':'#E5DDF3','output':'#D0E7EE','hold':'#F8D9D3'}
    borders={'input':'#28618A','design':'#946000','baseline':'#5E6C79','method':'#176C54','evaluation':'#6A4A8A','output':'#176379','hold':'#A13D32'}
    c.setFillColor(HexColor(fills[role]));c.setStrokeColor(HexColor(borders[role]));c.roundRect(cx-w/2,cy-h/2,w,h,5,fill=1,stroke=1)
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
    node(mid,top,labels[0],260,role='input');node(mid,top-65,labels[1],260,role='design')
    node(left,top-140,labels[2],208,44,role='baseline' if page not in (19,20) else 'method');node(right,top-140,labels[3],208,44,role='method' if page not in (19,20) else 'hold')
    node(mid,top-215,labels[4],300,44,role='evaluation');node(mid,top-280,labels[5],300,38,role='output')
    edge([(mid,top-19),(mid,top-46)])
    edge([(mid,top-84),(mid,top-103),(left,top-103),(left,top-118)])
    edge([(mid,top-84),(mid,top-103),(right,top-103),(right,top-118)])
    edge([(left,top-162),(left,top-180),(mid,top-180),(mid,top-193)])
    edge([(right,top-162),(right,top-180),(mid,top-180),(mid,top-193)])
    edge([(mid,top-237),(mid,top-261)])
    y=top-310;para(caption,8)

def study(t,question,data,steps,labels,caption,claim):
    title(t)
    key=t.split('.')[0]
    context={
    '4':('Asset-centric exposure analysis','Incomplete knowledge of communication boundaries complicates the allocation of scarce monitoring resources.','Direct support for structural comparisons; measured intrusion likelihood and operational disruption require additional evidence.'),
    '5':('Explainable threat intelligence and graph learning','A plausible association between a weakness, product and technique may be unsupported or produced by leakage between training and evaluation graphs.','Direct support for typed structural inference; temporal forecasting requires dated snapshots and verified future outcomes.'),
    '6':('Evidence-grounded LLM security analytics','Fluent threat explanations may include incorrect identifiers or claims that are not entailed by retrieved evidence.','Direct support for reference-label mapping; citation faithfulness requires a separately adjudicated evidence set.'),
    '7':('Domain adaptation for security query generation','A model may memorize query templates while failing to generate semantically correct queries for unseen analytical tasks.','Conditional support: researchers must construct a disjoint evaluation set and validate query semantics.'),
    '8':('Robust detection under controlled perturbations','A detector can learn generation artifacts instead of behavior relevant to an intrusion or operational anomaly.','Suitable for controlled algorithm comparison; field detection claims require independently labeled operational incidents.'),
    '9':('Behavioral monitoring and sequence modelling','Unusual sequences can reflect legitimate operating modes, incomplete observations or faults as well as malicious activity.','Suitable for exploratory sequence analysis; attack classification is conditional on new, verified labels.'),
    '10':('Assurance of agentic security workflows','An AI agent may select nonexistent tools, exceed a risk condition or continue after a required stop.','Direct support for fixture-based policy evaluation; live tool safety and mission success are outside the fixture evidence.'),
    '11':('Human-centered evidence fusion','Combining incompatible identities or clocks can create convincing but false cross-source explanations.','Conditional support: only explicitly validated identity and temporal mappings justify integrated analyses.')}
    area,problem,suit=context[key]
    para('<b>Research area.</b> '+area+'<br/><b>Problem statement.</b> '+problem,9.4)
    para('<b>Research question.</b> '+question,9.4)
    para('<b>Materials and suitability.</b> '+data+' '+suit,9.4)
    para('<b>Experimental design.</b> '+steps,9.4)
    diagram(labels,caption)
    para('<b>Interpretation and limitations.</b> '+claim,9.2)

title("Cybersecurity Research with Industrial CPS Data")
para('A research agenda and methodological guide',16)
para('Industrial CPS Security Research Datasets | Version 2.1',11)
para('Prepared for the repository maintained by Dr Ahmad Mohsin<br/>1 November 2026',10)
sub('Abstract')
para('The growing use of machine learning, knowledge graphs and autonomous agents in industrial security creates a need for evaluations that connect computational performance to defensible operational claims. This guide characterizes the research opportunities afforded by the released dataset and distinguishes structural, synthetic, observational and expected-decision evidence. It develops research problems in exposure analysis, graph inference, grounded threat intelligence, query generation, behavioral monitoring and agent governance. For each area, the guide identifies a research question, suitable inputs, a comparison design and the additional evidence required for stronger conclusions. Recent critical-infrastructure advisories motivate the agenda; they are not represented as incidents captured in this dataset.')
sub('Scope and contribution')
para('The contribution is a methodological research agenda rather than a benchmark leaderboard. The proposed experiments have not been executed for this edition. Dataset release 1.0.0 is examined at documentation baseline b7407cb67341e546a352afb587f65e470ac4d970. The underlying data are unchanged. Article provenance and publication status are documented in the repository.')
para('<link href="https://github.com/ahmadspm/industrial-cps-security-datasets" color="#087F8C">github.com/ahmadspm/industrial-cps-security-datasets</link>',9)
para('<b>Keywords:</b> industrial cybersecurity; cyber-physical systems; knowledge graphs; adversarial machine learning; agentic AI; reproducibility.',9)

def architecture_figure():
    global y
    top=y-32; left=M+112; right=W-M-112
    node(left,top,'Human supervision<br/>HMI / operator',200,44,role='output')
    node(left,top-100,'Industrial control<br/>PLC / control logic',200,44,role='design')
    node(left,top-200,'Physical process<br/>sensors and actuators',200,44,role='input')
    node(right,top,'Security research<br/>graph / anomaly / agent models',200,44,role='method')
    node(right,top-100,'Released representations<br/>assets / flows / event features',200,44,role='input')
    node(right,top-200,'Offline experiments<br/>synthetic data / scenario fixtures',200,44,role='baseline')
    edge([(left-30,top-22),(left-30,top-78)])
    edge([(left+30,top-78),(left+30,top-22)])
    edge([(left-30,top-122),(left-30,top-178)])
    edge([(left+30,top-178),(left+30,top-122)])
    edge([(right,top-78),(right,top-22)])
    edge([(right,top-178),(right,top-122)])
    c.setDash(3,3)
    edge([(left+100,top-100),(right-100,top-100)])
    edge([(right-100,top),(left+100,top)])
    c.setDash()
    y=top-238
    para('Figure A. Conceptual CPS security research architecture. Solid arrows denote the control/measurement cycle (left) or analytical evidence flow (right). Dashed arrows denote abstraction into released records and advisory interpretation. They do not denote an implemented live connection. Original figure for this guide; conceptual context: NIST SP 800-82r3 [12] and AI/OT guidance [10].',8)

def transfer_figure():
    global y
    top=y-25; left=M+114;right=W-M-114;mid=W/2
    node(left,top,'Released industrial evidence<br/>declared scope and assumptions',210,42,role='input')
    node(right,top,'Target-sector evidence<br/>assets / dynamics / constraints',210,42,role='input')
    node(left,top-75,'Reproducible method<br/>fixed baseline and metrics',210,42,role='method')
    node(right,top-75,'Compatibility assessment<br/>semantics / labels / authority',210,42,role='design')
    node(mid,top-148,'Independent target-sector validation<br/>performance + operational constraints',320,44,role='evaluation')
    edge([(left,top-21),(left,top-54)])
    edge([(right,top-21),(right,top-54)])
    edge([(left,top-96),(left,top-112),(mid,top-112),(mid,top-126)])
    edge([(right,top-96),(right,top-112),(mid,top-112),(mid,top-126)])
    y=top-181
    para('Figure B. Evidence required for cross-sector transfer. A method and a compatibility assessment converge on independent validation. An industrial result alone does not establish a water, energy or transport outcome. Original conceptual diagram for this guide.',8)

title('Research context: CPS security architecture')
architecture_figure()
para('A cyber-physical system couples a physical process to sensing, control and supervision. Cybersecurity research must distinguish this operating loop from the analytical representations used to study it. Figure A locates the released assets, communication flows and event features within that distinction. It also separates observational evidence from offline simulations and expected-decision fixtures.')
para('The dataset supports structural and behavioral research on selected representations. It does not provide a complete operating plant or authorize a model to control equipment. The dashed advisory path therefore requires separate interpretation, validation and an explicit decision about permitted authority.')
para('[12] Stouffer et al. (2023). <i>Guide to Operational Technology (OT) Security.</i> NIST SP 800-82 Rev. 3. <link href="https://doi.org/10.6028/NIST.SP.800-82r3" color="#087F8C">doi:10.6028/NIST.SP.800-82r3</link>. Figure A is an original synthesis, not a reproduction of a NIST figure.',8.5)
para('Sector-specific physical consequences require additional process models, operating constraints and outcome evidence. This is the basis for the transfer assessment in Figure B.')

title('Contemporary security problems, 2025-2026')
sub('Loss of monitoring and control through exposed PLCs')
para('A July 2026 FBI/EPA announcement reports water-sector incidents involving internet-facing PLCs, with changes to configurations and credentials causing loss of monitoring or control [9]. This motivates research on communication boundaries, trusted configuration evidence and restoration priorities. The inventory and graph tables support an abstract comparison of exposure-reduction policies; they contain neither packet captures nor forensic records of those incidents.')
sub('Authority and reliability in AI-enabled OT')
para('The December 2025 joint guidance on secure AI integration in OT emphasizes suitability assessment, governance, oversight and lifecycle testing [10]. A research implication is that model accuracy and permission to act should be evaluated separately. The agent fixtures can test tool eligibility and stop decisions. Their expected outputs cannot establish the safety of direct process control.')
sub('Manipulated inputs and ungrounded explanations')
para('NIST 2025 adversarial machine-learning taxonomy covers attacks across the AI lifecycle [11]. For this corpus, a tractable research question concerns whether controlled corruption of graph facts or retrieved evidence changes an analytical conclusion. Such experiments require newly constructed perturbations with explicit attacker capabilities; the release does not supply a validated poisoning or prompt-injection benchmark.')
para('<b>Sources:</b> [9] FBI/EPA, 30 July 2026: <link href="https://www.fbi.gov/investigate/cyber/alerts/2026/malicious-cyber-actors-targeting-water-and-wastewater-sector-internet--facing-programmable-logic-controllers-causing-operational-disruptions" color="#087F8C">Water-sector PLC warning</link>. [10] ASD and international partners, 4 December 2025: <link href="https://www.cyber.gov.au/publication/principles-for-the-secure-integration-of-artificial-intelligence-in-operational-technology" color="#087F8C">Secure AI integration in OT</link>. [11] Vassilev et al., March 2025: <link href="https://doi.org/10.6028/NIST.AI.100-2e2025" color="#087F8C">NIST AI 100-2 E2025</link>. Accessed 1 November 2026.',8.5)
para('These connections are proposed research uses, not claims that the dataset contains contemporary campaigns. The security contribution should be stated at the level actually evaluated: topology, reference mapping, controlled robustness or fixture-level decision behavior.')

title('Potential research areas and open problems')
table([['Area / open problem','Testable question','Inputs and expected contribution'],['Exposure and segmentation','Can boundary-aware monitoring improve weighted flow coverage at the same budget?','Inventory + topology; resource-allocation method'],['Explainable graph inference','Does relation typing improve held-out link ranking without inverse-edge leakage?','Knowledge graph; auditable structural inference'],['Grounded CTI analytics','Does graph evidence reduce unsupported identifiers at matched answer coverage?','CTI benchmarks + graph; calibrated mapping'],['Security query generation','Does adaptation generalize beyond familiar query templates?','Training pairs + new disjoint test set; semantic validation'],['Behavioral anomaly analysis','Can unusual transitions be detected across held-out traces?','Operational traces; exploratory or adjudicated evaluation'],['Adversarial AI robustness','How much controlled evidence corruption changes a decision?','Derived graph/CTI variants; robustness characterization'],['Agent governance','Do policy guards reduce prohibited decisions under held-out scenario families?','Expected-decision fixtures; explicit policy evaluation'],['Human-centered triage','Does a traceable evidence chain improve reviewer accuracy and review time?','Validated joins + new analyst study; decision-support evaluation']],[CW*.25,CW*.38,CW*.37])
para('The questions are deliberately comparative. A new model name or higher score alone is insufficient: the experiment should isolate the proposed mechanism, define the independent evaluation unit and identify the practical meaning of the observed difference. No novelty claim is implied without a separate literature review.',9.4)

title('Dataset suitability and evidence gaps')
para('Suitability is assessed for a specified research claim rather than for an algorithm in isolation. Direct support means that the necessary released inputs exist for a bounded offline task. Conditional support means that labels, mappings or an evaluation set must be added. Unsupported claims require a different empirical basis.',9.5)
table([['Data family','Suitability in this release','Additional evidence for broader claims'],['Inventory','Direct: topology, boundary coverage and prioritization','Observed configurations, controls and exposure validation'],['Knowledge graph','Direct: typed relation analysis; conditional: risk inference','Adjudicated relations; time-stamped updates; measured outcomes'],['CTI benchmarks','Direct: reference-label mapping comparisons','Independent label review; evidence corpus for faithfulness'],['Training pairs','Conditional: adaptation and query generation','Template-disjoint held-out prompts; semantic oracle'],['Synthetic','Direct: controlled sensitivity experiments','Real incident labels and external operational validation'],['Operational','Direct: sequence description; conditional: intrusion detection','Attack/fault adjudication; signal meanings; physical context'],['Agent scenarios','Direct: expected-policy agreement','Actual execution traces; independent outcome and safety criteria'],['Cross-source fusion','Conditional: only validated joins','Identity/time mappings and a documented coverage audit']],[CW*.22,CW*.38,CW*.40])
para('The corpus alone is unsuitable for measuring field intrusion-detection effectiveness, certifying autonomous control, estimating sector-wide attack prevalence, proving causal physical consequences, or establishing a current vulnerability risk score. These are evidence limitations, not conclusions about the usefulness of the data.',9.5)

title('A focused study of adversarial AI robustness')
para('A defensible extension is to examine whether analytical outputs remain stable when a bounded portion of their evidence is manipulated. The independent variable is the perturbation budget; the primary outcome is the change in correctness or unsupported-claim rate relative to a clean evaluation. The threat model must specify access, knowledge and the records that an adversary can modify.',9.5)
diagram(['Frozen graph/CTI subset + independent labels','Define attacker capability; preserve clean holdout','Clean evidence:<br/>same analytical model','Perturbed evidence:<br/>bounded derived variants','Compare correctness, abstention and evidence support','Release perturbation manifest and failure analysis'],'Robustness workflow. Controlled evidence manipulation. Blue: evidence; amber: design; grey/green: comparison; purple: evaluation; teal: reporting.')
para('Researchers may remove relations, introduce type-consistent false relations, or add conflicting retrieved statements to derived copies. Each variant should record affected IDs and its construction rule. Label leakage, malformed inputs and plausible but incorrect evidence should be analyzed separately. Prompt injection requires a separately constructed textual corpus and task-specific success criteria; no such benchmark is supplied.',9.5)
para('Useful outcomes include degradation curves, false-evidence acceptance, abstention under contradiction and recovery after evidence removal. Results support a claim about the declared perturbation model, not about resistance to all adaptive adversaries.',9.5)

title('Cross-sector relevance and transfer limits')
transfer_figure()
table([['Application context','Transferable research method','Required sector-specific additions'],['Water and wastewater','Boundary analysis; change/anomaly triage','Hydraulic/process model, asset mapping, quality/pressure limits'],['Electricity and DER','Evidence-grounded prioritization; guarded recommendations','Electrical topology, grid dynamics, protection and timing constraints'],['Manufacturing','Flow coverage; sequence analysis; agent fixture evaluation','Verified station semantics, production modes and incident labels'],['Transport services','Dependency reasoning and evidence provenance','Relevant control systems, interlocks, operational and safety outcomes']],[CW*.24,CW*.35,CW*.41])
para('Cross-sector applicability is a hypothesis to test. Similar network protocols do not imply equivalent dynamics, hazards or response authority. Figure B identifies the additional evidence required to evaluate that hypothesis.',9.3)

title('Threats to validity and research interpretation')
sub('Construct validity')
para('A proxy must be distinguished from the phenomenon of interest. Coverage of declared flows measures monitoring placement, not prevention of compromise. Expected policy agreement measures consistency with an oracle, not physical safety. Unusual event sequences measure deviation, not necessarily malicious behavior.')
sub('Internal validity')
para('Duplicate descriptions, repeated attackability tables and inverse graph relations can contaminate a comparison. Preprocessing, retrieval indexing and hyperparameter selection must follow the split. For LLM studies, expected answers and direct answer-bearing records should be excluded from the evaluated input. Model pretraining contamination remains a separate uncertainty.')
sub('External validity')
para('The industrial setting, pseudonymization, synthetic assumptions and small number of independent traces restrict generalization. A large row count does not substitute for independent sites, operating modes or incidents. Transfer studies should evaluate an additional, independently curated dataset and disclose differences in sensors, protocols and labels.')
sub('Statistical conclusion validity')
para('Repeated windows from one trace are correlated. Confidence intervals should reflect grouping by trace, entity, description or scenario family. Multiple model comparisons should be distinguished from a prespecified primary analysis. Effect sizes and failure distributions are more informative than isolated best-run scores.')
para('A manuscript should acknowledge these limitations where the relevant result is interpreted, rather than relying only on a general limitations paragraph.')

title('Study protocol and figure conventions')
sub('From research problem to an assessable claim')
para('A study protocol should state the operational motivation, the hypothesized mechanism, the released evidence, the intervention or model variation, and the outcome that could refute the hypothesis. A primary endpoint and evaluation split should be frozen before tuning. The baseline should represent a credible simpler approach under the same information and resource budget.')
para('For example: under a fixed monitoring budget, a boundary-aware policy is hypothesized to cover a larger weighted proportion of declared cross-zone flows than degree ranking. A negative or negligible difference would refute the proposed benefit for this topology. The conclusion would concern the declared graph, with no claim about measured attack reduction.')
sub('Consistent meaning of workflow colours')
table([['Colour','Role in the experimental argument'],['Blue','Released evidence or frozen inputs'],['Amber','Study design, split construction or eligibility checks'],['Grey','Baseline or reference condition'],['Green','Proposed method or permitted branch'],['Coral','Held, rejected or unsupported branch'],['Purple','Common evaluation or evidence review'],['Teal','Reported outputs, uncertainty and provenance']],[CW*.24,CW*.76])
para('Each box also states its role in text so the diagrams remain interpretable in greyscale. Comparison diagrams share inputs and evaluation conditions. Decision diagrams distinguish permitted and held branches. All workflows describe proposed research procedures, rather than newly measured experimental results.',9.5)
para('Navigation: evidence inventory and loading, pp. 10-11; experimental design, p. 12; eight study protocols, pp. 13-20; metrics, p. 21; replay, p. 22; reproducibility manifest, p. 23; related articles, p. 24. Recent guidance [9-11] is linked on p. 3; OT architecture reference [12] is given on p. 2.',9.5)

title('1. Choose the evidence and the question')
table([['Folder / evidence','Release size','Research use'],['inventory / structural tables','94 master assets; 53 component records; 120 flows; 6 zones; 5 conduits','Segmentation and exposure'],['knowledge_graph / typed structure','305,167 nodes; 276,420 edges','Link prediction and graph reasoning'],['benchmarks / upstream reference labels','2,047 CTI records','CTI extraction and mapping'],['training / instruction-output examples','358 unique pairs','Query generation and adaptation'],['synthetic / generated assumptions and logs','340 attackability rows; 9,880 protocol rows','Controlled perturbations'],['operational / pseudonymized observations','14,124 events; 29 traces','Sequence and anomaly studies'],['agent_scenarios / expected fixtures','20 scenarios; 400 cases','Governed decision behavior']],[CW*.36,CW*.28,CW*.36])
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
assert page==24,page
c.save()
print(R/'RESEARCHERS_GUIDE.pdf')
