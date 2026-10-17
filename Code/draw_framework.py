from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
for name,file in [("FigureRoman","Times New Roman.ttf"),("FigureBold","Times New Roman Bold.ttf"),("FigureItalic","Times New Roman Italic.ttf")]:
 pdfmetrics.registerFont(TTFont(name,"/System/Library/Fonts/Supplemental/"+file))
from pathlib import Path
# Rendering requires reportlab and a Times New Roman TTF installation.
# The supplied vector PDF is already generated and embedded-font portable.
out=Path(__file__).resolve().parents[1]/'Figures/framework_overview.pdf'
c=canvas.Canvas(str(out),pagesize=(550,365))
ink=colors.HexColor('#162632');accent=colors.HexColor('#315b73');pale=colors.HexColor('#f0f5f7')

def box(x,y,w,h,title,lines=(),size=9):
 c.setStrokeColor(accent);c.setFillColor(pale);c.setLineWidth(.8);c.roundRect(x,y,w,h,5,stroke=1,fill=1)
 c.setFillColor(ink);c.setFont('FigureBold',size+1)
 c.drawCentredString(x+w/2,y+h-15,title)
 c.setFont('FigureRoman',size)
 for i,line in enumerate(lines):c.drawCentredString(x+w/2,y+h-29-i*12,line)

def arrow(points,dashed=False):
 c.setStrokeColor(ink);c.setFillColor(ink);c.setLineWidth(.8);c.setDash(3,2) if dashed else c.setDash()
 p=c.beginPath();p.moveTo(*points[0])
 for pt in points[1:]:p.lineTo(*pt)
 c.drawPath(p);c.setDash()
 import math
 a,b=points[-2],points[-1];t=math.atan2(b[1]-a[1],b[0]-a[0]);d=5
 p=c.beginPath();p.moveTo(*b);p.lineTo(b[0]-d*math.cos(t-.45),b[1]-d*math.sin(t-.45));p.lineTo(b[0]-d*math.cos(t+.45),b[1]-d*math.sin(t+.45));p.close();c.drawPath(p,fill=1,stroke=0)
box(190,309,170,40,'Request and frozen predictor',['Confidence screen: s ≥ threshold'],9)
box(25,203,235,72,'Exposure ledger',['E = confirmed errors; P = unresolved outputs','Require E + P + 1 ≤ ε (N + 1) + B','Unresolved outcomes retain worst-case loss'],9)
box(290,203,235,72,'Verification-debt ledger',['Attach deadline d = release time + D','Require worst-case EDF feasibility F','Include active residual and waiting jobs'],9)
arrow([(275,309),(275,291),(142.5,291),(142.5,275)])
arrow([(275,291),(407.5,291),(407.5,275)])
box(215,140,120,40,'Both constraints pass?',['Logical AND'],9)
arrow([(142.5,203),(142.5,191),(245,191),(245,180)])
arrow([(407.5,203),(407.5,191),(305,191),(305,180)])
box(25,140,135,40,'Withhold output',['No release; no earned credit'],9)
box(390,140,135,40,'Release output',['N ← N+1; P ← P+1'],9)
arrow([(215,160),(160,160)]);arrow([(335,160),(390,160)])
c.setFont('FigureItalic',8);c.setFillColor(ink);c.drawCentredString(184,165,'No');c.drawCentredString(362,165,'Yes')
box(390,51,135,58,'Queue and audit server',['Choose only a deadline-','respecting priority; non-preemptive','Complete truthful audit'],8.5)
arrow([(457.5,140),(457.5,109)])
box(25,51,305,58,'Audit-completion feedback',['Correct: P ← P-1; error: P ← P-1, E ← E+1','Remove completed verification job; update active residual'],9)
arrow([(390,80),(330,80)])
arrow([(25,80),(9,80),(9,239),(25,239)],True)
arrow([(525,80),(541,80),(541,239),(525,239)],True)
c.setFont('FigureItalic',8.5);c.drawCentredString(275,25,'Deadline assumptions: immediate audit eligibility, continuous server availability, service ≤ Smax.')
c.drawCentredString(275,12,'Exposure safety needs truthful, persistent accounting; the gate does not guarantee positive coverage.')
c.save();print(out)
