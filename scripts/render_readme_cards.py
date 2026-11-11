#!/usr/bin/env python3
import json, os, html
from pathlib import Path
from datetime import date, timedelta
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'cards'; DATA=ROOT/'data/contributions.json'
OUT.mkdir(exist_ok=True); STATIC=os.getenv('STATIC','0')=='1'
BG='#f3f2ee'; INK='#111111'; MUTED='#77777b'; BLUE='#315bff'
SERIF="Georgia, 'Times New Roman', serif"; SANS='Arial, Helvetica, sans-serif'; MONO='ui-monospace, SFMono-Regular, Menlo, monospace'
def e(x): return html.escape(str(x))
def load(): return json.loads(DATA.read_text()) if DATA.exists() else {'total':None,'days':[]}
def start(w,h,title):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{e(title)}</title><desc id="desc">Automatically generated GitHub profile activity card.</desc><defs><linearGradient id="shine"><stop offset="0" stop-color="#315bff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#315bff" stop-opacity="0"/></linearGradient><style>
.serif{{font-family:{SERIF}}}.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}.ink{{fill:{INK}}}.muted{{fill:{MUTED}}}.blue{{fill:{BLUE}}}
.enter{{animation:enter .7s cubic-bezier(.2,.8,.2,1) both}}.rise{{transform-box:fill-box;transform-origin:center bottom;animation:rise .8s cubic-bezier(.2,.8,.2,1) both}}.tile{{transform-box:fill-box;transform-origin:center bottom;animation:tileIn .9s cubic-bezier(.18,.9,.25,1.2) both}}.sweep{{animation:sweep 5s ease-in-out infinite}}
@keyframes enter{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}@keyframes rise{{from{{transform:scaleY(.02);opacity:.35}}to{{transform:scaleY(1);opacity:1}}}}@keyframes tileIn{{0%{{opacity:0;transform:translateY(32px) rotate(2deg)}}70%{{opacity:1;transform:translateY(-4px) rotate(-.5deg)}}100%{{transform:translateY(0) rotate(0)}}}}@keyframes sweep{{0%,70%{{transform:translateX(-160%)}}100%{{transform:translateX(160%)}}}}@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important}}}}
</style></defs><rect width="{w}" height="{h}" rx="18" fill="{BG}"/>'''
def end(): return '</svg>'
def graph(d):
 days=sorted(d.get('days',[]),key=lambda x:x['date']); lookup={x['date']:x.get('count',0) for x in days}
 first=date.fromisoformat(days[0]['date']) if days else date.today()-timedelta(days=370); first-=timedelta(days=(first.weekday()+1)%7)
 cells=[]
 for c in range(53):
  for r in range(7):
   day=first+timedelta(days=c*7+r); n=lookup.get(day.isoformat(),0); level=0 if n==0 else 1 if n<=2 else 2 if n<=5 else 3 if n<=9 else 4
   color=['#e4e4e1','#cbd5ff','#9db1ff','#6485ff',BLUE][level]; attr='' if STATIC else f'class="enter" style="animation-delay:{(c*7+r)*.006:.3f}s"'
   cells.append(f'<rect x="{35+c*13}" y="{70+r*15}" width="10" height="10" rx="2" fill="{color}" {attr}/>')
 out=start(760,215,'Every day, in blue — GitHub contributions')
 out+='<text x="35" y="39" class="serif ink" font-size="27">Every day, <tspan fill="#315bff" font-style="italic">in blue</tspan></text><text x="725" y="38" text-anchor="end" class="mono muted" font-size="9" letter-spacing="1.4">REFRESHED DAILY</text>'+''.join(cells)
 for i in range(12): out+=f'<text x="{35+i*56}" y="190" class="mono muted" font-size="9">{(date.today().replace(day=1)-timedelta(days=i*30)).strftime("%b")}</text>'
 out+='<text x="565" y="190" class="mono muted" font-size="9">less</text>'
 for i,c in enumerate(['#e4e4e1','#cbd5ff','#9db1ff','#6485ff',BLUE]): out+=f'<rect x="{595+i*15}" y="180" width="11" height="11" rx="2" fill="{c}"/>'
 return out+'<text x="678" y="190" class="mono muted" font-size="9">more</text>'+end()
def monthly(d):
 days=sorted(d.get('days',[]),key=lambda x:x['date']); today=date.today(); months=[]
 for off in reversed(range(12)):
  first=(today.replace(day=1)-timedelta(days=off*30)).replace(day=1); key=first.strftime('%Y-%m'); months.append((first.strftime('%b'),sum(x.get('count',0) for x in days if x['date'].startswith(key))))
 has=bool(days); total=int(d.get('total',sum(x.get('count',0) for x in days))) if has else None; active=sum(x.get('count',0)>0 for x in days); best=max(months,key=lambda x:x[1]); counts={x['date']:x.get('count',0) for x in days}
 cur=0; day=today
 if counts.get(day.isoformat(),0)==0: day-=timedelta(days=1)
 while counts.get(day.isoformat(),0)>0: cur+=1; day-=timedelta(days=1)
 longest=run=0
 for x in days: run=run+1 if x.get('count',0)>0 else 0; longest=max(longest,run)
 busiest=max(days,key=lambda x:x.get('count',0),default={'count':0}).get('count',0)
 out=start(760,290,'The last 12 months on GitHub')+'<text x="34" y="38" class="mono muted" font-size="10" letter-spacing="1.3">THE LAST 12 MONTHS ON GITHUB</text>'
 out+=f'<text x="34" y="87" class="serif ink" font-size="39">{(format(total,",") if total is not None else "Awaiting data")} <tspan font-style="italic">{("contributions" if total is not None else "")}</tspan></text>'
 maxv=max([v for _,v in months]+[1]); base=222; bh=112; bw=34; gap=15
 for i,(label,val) in enumerate(months):
  h=max(3,bh*val/maxv); x=35+i*(bw+gap); y=base-h; color=BLUE if val==best[1] and val else INK; attr='' if STATIC else f'class="rise" style="animation-delay:{i*.07:.2f}s"'
  out+=f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{h:.1f}" rx="4" fill="{color}" {attr}/><text x="{x+bw/2}" y="244" text-anchor="middle" class="mono muted" font-size="9">{label}</text>'
  if val==best[1] and val: out+=f'<text x="{x+bw/2}" y="{y-8:.1f}" text-anchor="middle" class="mono blue" font-size="10">{val:,}</text>'
 out+='<path d="M500 28V263" stroke="#deded9"/>'
 stats=([(f'{cur} days','current streak'),(f'{longest} days','longest streak'),(f'{active} days','days with a contribution'),(str(busiest),'on the busiest day')] if days else [('—','current streak'),('—','longest streak'),('—','days with a contribution'),('—','on the busiest day')])
 for i,(v,lbl) in enumerate(stats):
  y=57+i*53; out+=f'<text x="525" y="{y}" class="serif ink" font-size="28">{e(v)}</text><text x="527" y="{y+17}" class="sans muted" font-size="11">{e(lbl)}</text>'
  if i<3: out+=f'<path d="M525 {y+28}H725" stroke="#deded9"/>'
 return out+end()
def tile(kicker,headline,body,color,fg,delay):
 attr='' if STATIC else f'class="tile" style="animation-delay:{delay}s"'
 return start(240,180,kicker)+f'''<g {attr}><rect width="240" height="180" rx="15" fill="{color}"/><text x="20" y="28" class="mono" fill="{fg}" font-size="10" letter-spacing="1.4">{kicker}</text><text x="20" y="87" class="serif" fill="{fg}" font-size="30" font-style="italic">{headline}</text><text x="20" y="119" class="sans" fill="{fg}" font-size="12">{body[0]}</text><text x="20" y="137" class="sans" fill="{fg}" font-size="12">{body[1]}</text><text x="214" y="28" class="sans" fill="{fg}" font-size="17">↗</text><rect width="240" height="180" rx="15" fill="url(#shine)" opacity=".24" class="sweep"/></g>'''+end()
def project(title,lines,meta,color,delay):
 attr='' if STATIC else f'class="enter" style="animation-delay:{delay}s"'
 return start(360,170,title)+f'''<g {attr}><rect width="360" height="170" rx="15" fill="{BG}" stroke="#deded9"/><rect x="20" y="22" width="7" height="7" rx="2" fill="{color}"/><text x="38" y="30" class="sans ink" font-size="16" font-weight="600">{title}</text><text x="20" y="69" class="sans" fill="#555" font-size="12">{lines[0]}</text><text x="20" y="87" class="sans" fill="#555" font-size="12">{lines[1]}</text><text x="20" y="143" class="mono muted" font-size="10">{meta}</text><path d="M320 24h12m-5 -5l5 5l-5 5" fill="none" stroke="{color}" stroke-width="1.4"/></g>'''+end()
def main():
 d=load(); (OUT/'contributions.svg').write_text(graph(d)); (OUT/'monthly.svg').write_text(monthly(d))
 (OUT/'build.svg').write_text(tile('BUILD','Software',['Products, apps &','useful tools',],BLUE,'#fff',.1))
 (OUT/'agents.svg').write_text(tile('AGENTS','Applied AI',['Agent workflows &','intelligent systems'],'#ef382c','#fff',.25))
 (OUT/'learn.svg').write_text(tile('LEARN','Engineering',['Fundamentals, craft','& constant learning'],'#ffc928','#151515',.4))
 (OUT/'auto.svg').write_text(project('AUTO — AI Orchestrator',['Task routing and structured','workflow orchestration.'],'Python · AI agents',BLUE,.1))
 (OUT/'campusresolve.svg').write_text(project('CampusResolve AI',['AI-assisted campus incident','triage and resolution workflows.'],'Applied AI · Product','#ef382c',.2))
 (OUT/'reprise.svg').write_text(project('RepRise',['Native Android habit tracker','built with modern Kotlin.'],'Kotlin · Android','#d6a800',.3))
if __name__=='__main__': main()
