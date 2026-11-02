#!/usr/bin/env python3
"""Draw the same left-to-right workflows as SVG for GitHub and PDF for the guide."""
import pathlib,html,math,os,reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
FONT="WorkflowSans"
font_path=pathlib.Path(os.environ.get("WORKFLOW_FONT",str(pathlib.Path(reportlab.__file__).parent/"fonts/Vera.ttf")))
pdfmetrics.registerFont(TTFont(FONT,str(font_path)))
ROOT=pathlib.Path(__file__).resolve().parents[1]
W,H=1000,280;NW,NH=160,76
PALETTE={'input':('#D9EAF8','#245A81'),'design':('#FCE6BB','#A36A13'),'baseline':('#EEEEEE','#687580'),'method':('#CCEBE2','#287759'),'hold':('#F8D9D3','#A84838'),'evaluation':('#E5DDF3','#70528D'),'output':('#D1EBED','#087F8C')}
# Node positions, roles and lines are shared by both vector renderers.
CHARTS={
'workflow-a':{
 'title':'Asset-aware threat-evidence retrieval',
 'nodes':{'a':(20,95,'input',['Inventory + graph','verified asset join']), 'b':(220,95,'design',['CVE links','available?']), 'c':(420,25,'method',['Retrieve supported','CVE / CWE links']), 'd':(420,175,'hold',['Abstain','no supported link']), 'e':(620,25,'evaluation',['Assess evidence','and limitations']), 'f':(820,95,'output',['Retrieval scores','and uncertainty'])},
 'edges':[('a','b',[]),('b','c',[(400,133),(400,63)]),('b','d',[(400,133),(400,213)]),('c','e',[]),('e','f',[(800,63),(800,133)]),('d','f',[(800,213),(800,133)])],
 'annotations':[(397,86,'Yes'),(397,189,'No')]},
'workflow-b':{
 'title':'Reliable cybersecurity query generation',
 'nodes':{'a':(20,25,'input',['Compatible','training queries']), 'b':(20,175,'input',['New frozen','test questions']), 'c':(220,25,'design',['Development','split and protocol']), 'd':(420,25,'baseline',['Fixed base','model']), 'e':(420,175,'method',['Adapted','model']), 'f':(620,95,'evaluation',['Schema / engine','and result checks']), 'g':(820,95,'output',['Correctness, coverage','and failures'])},
 'edges':[('a','c',[]),('c','d',[]),('c','e',[(400,63),(400,213)]),('d','f',[(600,63),(600,133)]),('e','f',[(600,213),(600,133)]),('b','f',[(200,213),(200,265),(600,265),(600,133)]),('f','g',[])], 'annotations':[]},
'workflow-c':{
 'title':'Governed evidence-grounded agent reasoning',
 'nodes':{'a':(20,25,'input',['Scenario inputs','and declared policy']), 'b':(20,175,'input',['Optional','graph evidence']), 'c':(220,175,'design',['Verified entity','mapping only']), 'd':(420,25,'baseline',['Model-only','decision agent']), 'e':(420,175,'method',['Agent with evidence','and policy checks']), 'f':(620,95,'evaluation',['Held-out family','constraint scoring']), 'g':(820,95,'output',['Decision quality','and evidence support'])},
 'edges':[('a','d',[]),('a','e',[(200,63),(200,140),(400,140),(400,213)]),('b','c',[]),('c','e',[]),('d','f',[(600,63),(600,133)]),('e','f',[(600,213),(600,133)]),('f','g',[])], 'annotations':[]},
'workflow-d':{
 'title':'Exploratory event-sequence analysis',
 'nodes':{'a':(20,95,'input',['Operational traces','and trace metadata']), 'b':(220,95,'design',['Whole-trace split','and train-only fit']), 'c':(420,25,'baseline',['Transition / rarity','baseline']), 'd':(420,175,'method',['Candidate','sequence model']), 'e':(620,95,'design',['Verified labels','or injected events?']), 'f':(820,25,'evaluation',['Declared-task','metrics']), 'g':(820,175,'output',['Exploratory flags','and sequence statistics'])},
 'edges':[('a','b',[]),('b','c',[(400,133),(400,63)]),('b','d',[(400,133),(400,213)]),('c','e',[(600,63),(600,133)]),('d','e',[(600,213),(600,133)]),('e','f',[(800,133),(800,63)]),('e','g',[(800,133),(800,213)])],
 'annotations':[(797,86,'Yes'),(797,189,'No')]}}

def draw(name,spec):
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="280" viewBox="0 0 1000 280" role="img" aria-labelledby="title">','<title id="title">'+html.escape(spec['title'])+'</title>','<rect width="1000" height="280" fill="white"/>']
    out=ROOT/'docs/guide/workflows'/f'{name}.pdf';c=canvas.Canvas(str(out),pagesize=(W,H),invariant=1);c.setTitle(spec['title']);c.setAuthor('Dr Ahmad Mohsin');c.setFillColor(HexColor('#FFFFFF'));c.rect(0,0,W,H,fill=1,stroke=0)
    for source,target,via in spec['edges']:
        x,y,_,_=spec['nodes'][source];tx,ty,_,_=spec['nodes'][target]
        pts=[(x+NW,y+NH/2),*via,(tx,ty+NH/2)]
        # Edges are drawn behind boxes. Avoid duplicate points before calculating arrowheads.
        pts=[p for i,p in enumerate(pts) if i==0 or p!=pts[i-1]]
        svg.append('<polyline points="'+' '.join(f'{a},{b}' for a,b in pts)+'" fill="none" stroke="#42677D" stroke-width="2"/>')
        p=c.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
        for a,b in pts[1:]:p.lineTo(a,H-b)
        c.setStrokeColor(HexColor('#42677D'));c.setLineWidth(2);c.drawPath(p)
        (px,py),(qx,qy)=pts[-2:];angle=math.atan2(qy-py,qx-px);a=(qx-9*math.cos(angle)+4*math.sin(angle),qy-9*math.sin(angle)-4*math.cos(angle));b=(qx-9*math.cos(angle)-4*math.sin(angle),qy-9*math.sin(angle)+4*math.cos(angle))
        svg.append(f'<polygon points="{qx},{qy} {a[0]},{a[1]} {b[0]},{b[1]}" fill="#42677D"/>')
        p=c.beginPath();p.moveTo(qx,H-qy);p.lineTo(a[0],H-a[1]);p.lineTo(b[0],H-b[1]);p.close();c.setFillColor(HexColor('#42677D'));c.drawPath(p,fill=1,stroke=0)
    for x,y,role,lines in spec['nodes'].values():
        fill,stroke=PALETTE[role];svg.append(f'<rect x="{x}" y="{y}" width="{NW}" height="{NH}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke));c.setLineWidth(1.5);c.roundRect(x,H-y-NH,NW,NH,7,fill=1,stroke=1)
        wrapped=[]
        for line in lines:
            current=''
            for word in line.split():
                candidate=(current+' '+word).strip()
                if current and pdfmetrics.stringWidth(candidate,FONT,17)>NW-14:wrapped.append(current);current=word
                else:current=candidate
            if current:wrapped.append(current)
        lines=wrapped
        first=y+NH/2-(len(lines)-1)*10+6
        for i,line in enumerate(lines):
            yy=first+i*20;svg.append(f'<text x="{x+NW/2}" y="{yy}" text-anchor="middle" font-family="Bitstream Vera Sans, DejaVu Sans, Arial, sans-serif" font-size="17" fill="#17344A">{html.escape(line)}</text>')
            c.setFillColor(HexColor('#17344A'));c.setFont(FONT,17);c.drawCentredString(x+NW/2,H-yy,line)
    for x,y,label in spec['annotations']:
        svg.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#17344A" stroke="white" stroke-width="4" paint-order="stroke">{label}</text>')
        c.setFillColor(HexColor('#FFFFFF'));c.rect(x-13,H-y-3,26,16,fill=1,stroke=0);c.setFillColor(HexColor('#17344A'));c.setFont(FONT,13);c.drawCentredString(x,H-y,label)
    c.showPage();c.save();svg.append('</svg>');(ROOT/'assets/workflows'/f'{name}.svg').write_text('\n'.join(svg)+'\n')

if __name__=='__main__':
    (ROOT/'assets/workflows').mkdir(parents=True,exist_ok=True);(ROOT/'docs/guide/workflows').mkdir(parents=True,exist_ok=True)
    for name,spec in CHARTS.items():draw(name,spec)
    print('Built four shared left-to-right workflows as SVG and PDF.')
