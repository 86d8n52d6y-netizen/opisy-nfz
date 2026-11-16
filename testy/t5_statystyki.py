# T5 – statystyki: wszystkie tabele i kafelki porównane z niezależnym liczeniem w Pythonie (Decimal + datetime),
#      zgodność dni / tygodni / miesięcy, zakresy dat, wpisy anonimowe, obie podstawy „zarobku z punktów”
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
from decimal import Decimal as D, ROUND_HALF_UP
import datetime, random, re
random.seed(2026)
TODAY=datetime.date.today()
def hu(x): return int(D(x).quantize(D('1'),rounding=ROUND_HALF_UP))
def iso(d): return d.isoformat()
# ---------- dane: 22.12.2025 … dziś + kilka wpisów w przyszłości (tydzień 53/2026 i przełom roku) ----------
rows=[]; d=datetime.date(2025,12,22)
while d<=TODAY+datetime.timedelta(days=60):
    fut=d>TODAY
    work=(d.weekday() in (0,1,3) or (d.weekday()==4 and d.day%2==0) or (d.weekday()==5 and d.day in (7,21)))
    if work and (not fut or d in (datetime.date(2026,12,28),datetime.date(2026,12,31),datetime.date(2027,1,4))):
        old=d<datetime.date(2026,6,1)
        for i in range(random.randint(3,9)):
            rows.append(dict(date=iso(d),ini=random.choice(['JK','AB','','','MN','','ŻÓ']),pts=random.choice([84,105.6,61.2,286.8,189.6,104,252.8,319.2,150,70.5,294.5,0.01]),
                price=1.81 if old else random.choice([1.84,1.84,1.84,1.9]),pct=random.choice([40,40,35]),revH=random.choice([0,0,0,0,0.5]) ,revRate=350,
                ex=[random.choice([15000,8050,1999])] if random.random()<0.1 else [],min=random.choice([30,30,30,40,50,None]),src='gen' if random.random()<0.7 else 'man'))
        if d.weekday()==3 and d.day<15: rows.append(dict(date=iso(d),ini='',pts=0,price=1.84,pct=40,revH=random.choice([1.5,2,3,0.25]),revRate=random.choice([350,350,400]),ex=[],min=None,src='man'))
        if random.random()<0.07: rows.append(dict(date=iso(d),ini='',pts=0,price=1.84,pct=40,revH=0,revRate=350,ex=[random.choice([20000,12345]),500],min=None,src='man'))
    d+=datetime.timedelta(days=1)
# ---------- niezależne liczenie ----------
def cents(r,basis):
    pc=hu(D(str(r['pts']))*D(str(r['price']))*100); sh=hu(D(pc)*D(str(r['pct']))/100); rv=hu(D(str(r['revH']))*D(str(r['revRate']))*100); ex=sum(r['ex'])
    pe=sh if basis=='share' else pc
    return dict(pc=pc,sh=sh,rv=rv,ex=ex,pe=pe,total=pe+rv+ex)
def is_visit(r): return r['src']=='gen' or r['pts']>0 or bool(r['ini']) or (r['min'] or 0)>0
def agg(items,basis):
    o=dict(n=0,vis=0,pts=0,pe=0,pc=0,sh=0,rv=0,ex=0,total=0,min=0,revH=0,days=set(),vtot=0)
    for r in items:
        k=cents(r,basis); o['n']+=1
        if is_visit(r): o['vis']+=1; o['vtot']+=k['total']
        o['pts']+=hu(D(str(r['pts']))*100); o['revH']+=hu(D(str(r['revH']))*100); o['min']+=r['min'] or 0
        for kk in ('pe','pc','sh','rv','ex','total'): o[kk]+=k[kk]
        o['days'].add(r['date'])
    o['work']=o['min']+hu(D(o['revH'])*60/100); o['nd']=len(o['days'])
    return o
def avg(c,n): return hu(D(c)/n) if n else 0
def cal_days(f,t,last):
    td=iso(TODAY); end=t
    if t>td:
        end=td if f<=td else f
        if last and last>end: end=min(last,t)
    return max(1,(datetime.date.fromisoformat(end)-datetime.date.fromisoformat(f)).days+1)
def month_end(f): 
    x=datetime.date.fromisoformat(f[:8]+'01'); y=(x.replace(day=28)+datetime.timedelta(days=4)); return iso(y-datetime.timedelta(days=y.day))
def periods(kind,f,to,dates_all):
    # ciągła oś: od max(pierwszy wpis w historii, początek zakresu) do końca zakresu (przyszłość tylko do ostatniego wpisu); pusty niepełny okres na starcie pomijany
    items=[x for x in dates_all if f<=x<=to]
    if not items: return 0
    first=min(dates_all); last=max(items); td=iso(TODAY); end=to
    if to>td:
        end=td if f<=td else f
        if last>end: end=min(last,to)
    start=max(first,f)
    def per(ds):
        d0=datetime.date.fromisoformat(ds)
        if kind=='w': a=d0-datetime.timedelta(days=d0.weekday()); z=a+datetime.timedelta(days=6); k=tuple(a.isocalendar()[:2])
        else: a=d0.replace(day=1); z=datetime.date.fromisoformat(month_end(iso(a))); k=(a.year,a.month)
        return k,iso(a),iso(z)
    nxt=lambda z: iso(datetime.date.fromisoformat(z)+datetime.timedelta(days=1))
    have={per(x)[0] for x in items}; k,a,z=per(start)
    if a<start and k not in have: k,a,z=per(nxt(z))
    n=0
    while a<=end: n+=1; k,a,z=per(nxt(z))
    return n
def group(items,key):
    g={}
    for r in items: g.setdefault(key(r),[]).append(r)
    return g
# ---------- odczyt z ekranu ----------
def money(s):  # '13 769,79 zł' → grosze
    s=clean(s).replace(' ','').replace('zł','').replace('−','-').replace(',','.'); return hu(D(s)*100)
def numf(s): return D(clean(s).replace(' ','').replace(',','.'))
def mins(s):
    s=clean(s); h=re.search(r'(\d+) h',s); m=re.search(r'(\d+) min',s); return (int(h.group(1))*60 if h else 0)+(int(m.group(1)) if m else 0)
TABLES="()=>[...document.querySelectorAll('table.stat')].map(t=>({head:[...t.tHead.rows[0].cells].map(c=>c.innerText.trim()),body:[...t.tBodies[0].rows].map(r=>[...r.cells].map(c=>c.innerText.trim())),foot:t.tFoot?[...t.tFoot.rows[0].cells].map(c=>c.innerText.trim()):null}))"
DOWN=['poniedziałek','wtorek','środa','czwartek','piątek','sobota','niedziela']
MONN=['styczeń','luty','marzec','kwiecień','maj','czerwiec','lipiec','sierpień','wrzesień','październik','listopad','grudzień']
def fd(i): return i[8:]+'.'+i[5:7]+'.'+i[:4]
with sync_playwright() as p:
    b=launch(p); ctx=b.new_context(viewport={'width':1300,'height':1000}); errs=[]; pg=open_page(ctx,errs=errs); t=T()
    n=pg.evaluate("""async (rows)=>{let n=0;for(const r of rows){const now=new Date().toISOString();
      const m=normMeta({id:newId()+n,no:nextNo(),ini:r.ini,date:r.date,created:now,at:now,src:r.src,codes:r.src==='gen'?['ST33','ST30']:[],pts:r.pts,price:r.price,pct:r.pct,revH:r.revH,revRate:r.revRate,ex:r.ex.map(c=>({c,d:'x'})),min:r.min,miss:0,body:false});
      await dbPut(m);n++;}return n;}""",rows)
    anon=sum(1 for r in rows if not r['ini'])
    t.chk(f'dane testowe: {len(rows)} wpisów zapisanych (w tym {anon} anonimowych), 22.12.2025 – {max(r["date"] for r in rows)}', n==len(rows) and pg.evaluate("dbList().length")==len(rows))
    pg.click('#steps button[data-n="5"]')
    def set_range(preset=None,f=None,to=None):
        if preset: pg.click(f'button[data-act="range"][data-p="{preset}"]')
        else:
            pg.fill('#i_r_from',f); pg.dispatch_event('#i_r_from','change'); pg.fill('#i_r_to',to); pg.dispatch_event('#i_r_to','change')
        return pg.input_value('#i_r_from'),pg.input_value('#i_r_to')
    CANON={'Data':['Data','Dzień','Wizyty','Punkty','Z punktów','Przeglądy','Z przeglądów','Dodatkowe','Razem','Czas wizyt'],
           'Tydzień':['Tydzień','Dni pracy','Wizyty','Punkty','Z punktów','Z przeglądów','Dodatkowe','Razem','Śr. na dzień pracy'],
           'Miesiąc':['Miesiąc','Razem','Zmiana do poprz. mies.','Dni pracy','Wizyty','Punkty','Z punktów','Z przeglądów','Dodatkowe','Śr. na dzień pracy','Śr. na dzień kalend.','Śr. na wizytę','Czas pracy']}
    SHOWN={}
    def canon(T):   # kolumny w stałej kolejności wg nagłówków – sprawdzenia nie zależą od układu na ekranie (układ sprawdzany osobno)
        c=CANON.get(T['head'][0])
        if not c or sorted(c)!=sorted(T['head']): return T
        SHOWN[T['head'][0]]=T['head'][:]; ix=[T['head'].index(h) for h in c]
        return dict(head=c,body=[[r[i] for i in ix] for r in T['body']],foot=[T['foot'][i] for i in ix] if T['foot'] else None)
    def tab(x): pg.click(f'button[data-act="tab"][data-t="{x}"]'); return [canon(T) for T in pg.evaluate(TABLES)]
    def check_range(label,f,to,basis):
        items=[r for r in rows if f<=r['date']<=to]; A=agg(items,basis); bad=[]
        if not items: 
            t.chk(f'{label}: brak wpisów → komunikat', 'Brak wpisów w wybranym zakresie' in pg.inner_text('#main')); return
        last=max(r['date'] for r in items); cd=cal_days(f,to,last)
        # kafelki
        hero=money(pg.inner_text('.hero .hv')); tl={clean(x.split('\n')[0]):[clean(y) for y in x.split('\n')[1:]] for x in pg.evaluate("[...document.querySelectorAll('.tile')].map(e=>e.innerText)")}
        pk='Punkty (udział lekarza)' if basis=='share' else 'Punkty'
        exp_k=dict(hero=A['total'],pe=A['pe'],rv=A['rv'],ex=A['ex'],vis=A['vis'],days=A['nd'],avgd=avg(A['total'],A['nd']),min=A['min'],work=A['work'])
        got_k=dict(hero=hero,pe=money(tl[pk][0]),rv=money(tl['Przeglądy'][0]),ex=money(tl['Dodatkowe zarobki'][0]),vis=int(tl['Wizyty'][0]),days=int(tl['Dni przepracowane'][0]),avgd=money(tl['Średnio na dzień pracy'][0]),min=mins(tl['Czas wizyt'][0]),work=mins(tl['Czas pracy'][0]))
        if exp_k!=got_k: bad.append(('kafelki',exp_k,got_k))
        sub=tl[pk][1]; other=A['pc'] if basis=='share' else A['sh']
        if numf(sub.split(' pkt')[0])*100!=A['pts'] or money(sub.split('zł')[0].split(' ')[-2] if False else re.findall(r'([\d  ]+,\d\d) zł',sub)[-1]+' zł')!=other: bad.append(('kafelek punktów – podpis',sub,A['pts'],other))
        if numf(tl['Przeglądy'][1].replace(' h',''))*100!=A['revH']: bad.append(('godziny przeglądów',tl['Przeglądy'][1],A['revH']))
        if A['vis'] and money(re.findall(r'średnio (.+ zł)',tl['Wizyty'][1])[0])!=avg(A['vtot'],A['vis']): bad.append(('średnia na wizytę',tl['Wizyty'][1],avg(A['vtot'],A['vis'])))
        if int(re.findall(r'na (\d+) ',tl['Dni przepracowane'][1])[0])!=cd: bad.append(('dni kalendarzowe',tl['Dni przepracowane'][1],cd))
        if money(re.findall(r'kalendarzowy (.+ zł)',tl['Średnio na dzień pracy'][1])[0])!=avg(A['total'],cd): bad.append(('średnia na dzień kalendarzowy',tl['Średnio na dzień pracy'][1],avg(A['total'],cd)))
        # Dni
        T=tab('days')[0]; g=group(items,lambda r:r['date']); sums=dict(total=0,pe=0,rv=0,ex=0,vis=0,min=0)
        if len(T['body'])!=len(g): bad.append(('dni: liczba wierszy',len(T['body']),len(g)))
        for row in T['body']:
            di=row[0][6:]+'-'+row[0][3:5]+'-'+row[0][:2]; a=agg(g.get(di,[]),basis)
            exp=[DOWN[datetime.date.fromisoformat(di).weekday()],a['vis'],a['pts'],a['pe'],a['revH'],a['rv'],a['ex'],a['total'],a['min']]
            got=[row[1],int(row[2]),numf(row[3])*100,money(row[4]),numf(row[5].replace(' h',''))*100,money(row[6]),money(row[7]),money(row[8]),mins(row[9])]
            if exp!=got: bad.append(('dzień',di,exp,got))
            for k,v in (('total',a['total']),('pe',a['pe']),('rv',a['rv']),('ex',a['ex']),('vis',a['vis']),('min',a['min'])): sums[k]+=v
        F=T['foot']; gotF=dict(total=money(F[8]),pe=money(F[4]),rv=money(F[6]),ex=money(F[7]),vis=int(F[2]),min=mins(F[9]))
        if gotF!=sums or sums['total']!=A['total']: bad.append(('dni: wiersz Razem ≠ suma dni',gotF,sums,A['total']))
        # Tygodnie
        T=tab('weeks')[0]; g=group(items,lambda r:tuple(datetime.date.fromisoformat(r['date']).isocalendar()[:2])); wsum=0
        if len(T['body'])!=len(g): bad.append(('tygodnie: liczba wierszy',len(T['body']),len(g)))
        for row in T['body']:
            m=re.match(r'(\d+) · (\d\d)\.(\d\d)\.(\d{4}) – (\d\d)\.(\d\d)\.(\d{4})',row[0]); mon=datetime.date(int(m.group(4)),int(m.group(3)),int(m.group(2))); sun=datetime.date(int(m.group(7)),int(m.group(6)),int(m.group(5)))
            key=tuple(mon.isocalendar()[:2]); a=agg(g.get(key,[]),basis)
            if mon.weekday()!=0 or (sun-mon).days!=6 or int(m.group(1))!=key[1]: bad.append(('tydzień: granice',row[0]))
            exp=[a['nd'],a['vis'],a['pts'],a['pe'],a['rv'],a['ex'],a['total'],avg(a['total'],a['nd'])]
            got=[int(row[1]),int(row[2]),numf(row[3])*100,money(row[4]),money(row[5]),money(row[6]),money(row[7]),money(row[8])]
            if exp!=got: bad.append(('tydzień',row[0],exp,got))
            wsum+=a['total']
        if wsum!=A['total'] or money(T['foot'][7])!=A['total']: bad.append(('tygodnie: suma ≠ razem',wsum,A['total']))
        # Miesiące
        T=tab('months')[0]; g=group(items,lambda r:r['date'][:7]); keys=sorted(g); msum=0
        if len(T['body'])!=len(g): bad.append(('miesiące: liczba wierszy',len(T['body']),len(g)))
        for row in T['body']:
            mn,yr=row[0].split(' '); key=yr+'-'+str(MONN.index(mn)+1).zfill(2); a=agg(g[key],basis); f1=key+'-01'
            i=keys.index(key); prev=None
            if i>0:
                pm=(datetime.date.fromisoformat(f1)-datetime.timedelta(days=1)).isoformat()[:7]
                if keys[i-1]==pm: prev=agg(g[pm],basis)['total']
            if prev: 
                ch=float(D(abs(round((a['total']-prev)/prev*1000)))/10) ; expd=('▲' if a['total']>=prev else '▼', D(str(ch)))
                gotd=(row[2][0], numf(re.sub(r'[▲▼+−%\s]','',clean(row[2]))))
            else: expd=gotd=('—',) if row[2]=='—' else ('?',row[2])
            cdm=cal_days(f1,month_end(f1),max(r['date'] for r in g[key]))
            exp=[a['total'],a['nd'],a['vis'],a['pts'],a['pe'],a['rv'],a['ex'],avg(a['total'],a['nd']),avg(a['total'],cdm),avg(a['vtot'],a['vis']),a['work']]
            got=[money(row[1]),int(row[3]),int(row[4]),numf(row[5])*100,money(row[6]),money(row[7]),money(row[8]),money(row[9]),money(row[10]),money(row[11]),mins(row[12])]
            if exp!=got or expd!=gotd: bad.append(('miesiąc',row[0],exp,got,expd,gotd))
            msum+=a['total']
        if msum!=A['total'] or money(T['foot'][1])!=A['total']: bad.append(('miesiące: suma ≠ razem',msum,A['total']))
        # Dni tygodnia
        TT=tab('dow'); T=TT[0]; g=group(items,lambda r:datetime.date.fromisoformat(r['date']).weekday()); best=None
        for i,row in enumerate(T['body']):
            a=agg(g.get(i,[]),basis); 
            if a['nd'] and (best is None or avg(a['total'],a['nd'])>best[1]): best=(i,avg(a['total'],a['nd']))
            exp=[a['nd'],avg(a['total'],a['nd']) if a['nd'] else None,(D(hu(D(a['pts'])/a['nd']))/100) if a['nd'] else None,avg(a['vtot'],a['vis']) if a['vis'] else None,a['vis'],a['total']]
            got=[int(row[1]),money(row[2]) if row[2]!='—' else None,numf(row[3]) if row[3]!='—' else None,money(row[4]) if row[4]!='—' else None,int(row[5]),money(row[6])]
            if exp!=got or not row[0].startswith(DOWN[i]): bad.append(('dzień tygodnia',row[0],exp,got))
        lead=clean(pg.inner_text('p.lead'))
        if best and not (('Najwyższy średni zarobek na dzień pracy: '+DOWN[best[0]]) in lead and 'najwyższa średnia' in T['body'][best[0]][0]): bad.append(('najlepszy dzień tygodnia',lead,DOWN[best[0]]))
        # dni tygodnia w kolejnych miesiącach – trzy wartości
        gm=group(items,lambda r:r['date'][:7])
        for metric in ('avg','pts','vis'):
            pg.click(f'button[data-act="dowm"][data-v="{metric}"]'); M=pg.evaluate(TABLES)[1]
            for row in M['body']:
                mn,yr=row[0].split(' '); key=yr+'-'+str(MONN.index(mn)+1).zfill(2)
                for wd in range(7):
                    it=[r for r in gm[key] if datetime.date.fromisoformat(r['date']).weekday()==wd]; cell=row[1+wd]
                    if not it: exp='—'
                    else:
                        a=agg(it,basis)
                        if metric=='avg': exp=hu(D(avg(a['total'],a['nd']))/100)
                        elif metric=='pts': exp=D(hu(D(a['pts'])/a['nd']))/100
                        else: exp=hu(D(avg(a['vtot'],a['vis']))/100) if a['vis'] else '—'
                    got=cell if cell=='—' else (numf(cell) if metric=='pts' else int(numf(cell.replace('zł',''))))
                    if exp!=got: bad.append(('miesiąc×dzień tygodnia',metric,row[0],wd,exp,got))
        pg.click('button[data-act="dowm"][data-v="avg"]'); tab('days')
        t.chk(f'{label} [{("udział lekarza" if basis=="share" else "pełna wartość")}]: {len(items)} wpisów, razem {D(A["total"])/100} zł – kafelki, Dni, Tygodnie, Miesiące, Dni tygodnia zgodne z niezależnym liczeniem', not bad, bad[:3])
    # ---------- zakresy ----------
    f,to=set_range('all'); lastd=max(r['date'] for r in rows)
    t.chk('zakres „Wszystko”: od pierwszego do ostatniego wpisu', (f,to)==(min(r['date'] for r in rows),max(lastd,iso(TODAY))), (f,to))
    check_range('Wszystko',f,to,'full')
    t.chk('tabele: „Razem” zaraz po nazwie okresu, średnie na dzień pracy / kalendarzowy na początku tabeli miesięcy',
          SHOWN.get('Data',[])[:3]==['Data','Dzień','Razem'] and SHOWN.get('Tydzień',[])[:4]==['Tydzień','Razem','Dni pracy','Śr. na dzień pracy']
          and SHOWN.get('Miesiąc',[])[:6]==['Miesiąc','Razem','Zmiana do poprz. mies.','Dni pracy','Śr. na dzień pracy','Śr. na dzień kalend.'], SHOWN)
    pg.click('button[data-act="basis"][data-v="share"]'); check_range('Wszystko',f,to,'share'); pg.click('button[data-act="basis"][data-v="full"]')
    mon=TODAY-datetime.timedelta(days=TODAY.weekday()); m1=TODAY.replace(day=1); pm1=(m1-datetime.timedelta(days=1)).replace(day=1)
    y12=(m1.replace(year=m1.year-1,month=m1.month+1) if m1.month<12 else m1.replace(month=1))
    exp={'today':(iso(TODAY),iso(TODAY)),'week':(iso(mon),iso(mon+datetime.timedelta(days=6))),'month':(iso(m1),month_end(iso(m1))),'prev':(iso(pm1),month_end(iso(pm1))),
         'y12':(iso(y12),month_end(iso(m1))),'year':(f'{TODAY.year}-01-01',f'{TODAY.year}-12-31')}
    for pz,(ef,et) in exp.items():
        gf,gt=set_range(pz)
        if (gf,gt)!=(ef,et): t.chk(f'zakres „{pz}”', False, ((gf,gt),(ef,et)))
        check_range({'today':'Dziś','week':'Ten tydzień','month':'Ten miesiąc','prev':'Poprzedni miesiąc','y12':'Ostatnie 12 mies.','year':'Ten rok'}[pz],ef,et,'full')
    gf,gt=set_range(None,'2026-02-10','2026-04-05'); t.chk('dowolny zakres dat wpisany ręcznie', (gf,gt)==('2026-02-10','2026-04-05'))
    check_range('Zakres 10.02–05.04.2026',gf,gt,'full')
    gf,gt=set_range(None,'2025-12-22','2026-01-11'); check_range('Przełom roku 22.12.2025–11.01.2026',gf,gt,'full')
    gf,gt=set_range(None,'2026-12-21','2027-01-10'); check_range('Przyszłość: tydzień 53/2026 i 1/2027',gf,gt,'full')
    t.chk('zakres przyszły ustawiony poprawnie (pole „Od” późniejsze niż dotychczasowe „Do” nie zamienia dat)', (gf,gt)==('2026-12-21','2027-01-10'), (gf,gt))
    gf,gt=set_range(None,'2026-06-10','2026-06-01'); t.chk('„Do” wcześniejsze niż „Od”: wygrywa pole zmienione ostatnio (zakres 01.06–01.06)', (gf,gt)==('2026-06-01','2026-06-01'), (gf,gt))
    gf,gt=set_range(None,'2024-01-01','2024-01-31'); check_range('zakres bez wpisów','2024-01-01','2024-01-31','full')
    # ---------- zgodność zestawień ze sobą i wpisy anonimowe ----------
    r=pg.evaluate("""()=>{const l=dbList(),A=agg(l);const s=(f)=>grp(l,f).reduce((o,x)=>{['pe','rv','ex','total','pc','sh','min','vis','ptsC','revHc'].forEach(k=>o[k]=(o[k]||0)+x.A[k]);return o;},{});
      const d=s(m=>m.date),w=s(m=>weekOf(m.date).key),m=s(m=>m.date.slice(0,7));const ok=x=>['pe','rv','ex','total','pc','sh','min','vis','ptsC','revHc'].every(k=>x[k]===A[k]);
      const an=agg(l.filter(m=>!m.ini)),ini=agg(l.filter(m=>m.ini));
      return {d:ok(d),w:ok(w),m:ok(m),parts:A.total===A.pe+A.rv+A.ex,anon:an.total+ini.total===A.total&&an.n>0&&an.total>0,nAnon:an.n};}""")
    t.chk('suma dni = suma tygodni = suma miesięcy = razem (każda kategoria, co do grosza)', r['d'] and r['w'] and r['m'], r)
    t.chk('razem = punkty + przeglądy + dodatkowe (kategorie się nie mieszają)', r['parts'])
    t.chk(f'wpisy anonimowe ({r["nAnon"]}) wchodzą do statystyk', r['anon'] and r['nAnon']==anon)
    # ---------- edycja i usunięcie wpisu aktualizują wszystkie zestawienia ----------
    set_range('all'); before=money(pg.inner_text('.hero .hv')); vic=pg.evaluate("(()=>{const m=dbList().find(x=>x.pts>100&&x.date<todayISO());return {id:m.id,date:m.date,t:calc(m).total,pts:m.pts,price:m.price};})()")
    pg.evaluate("async (id)=>{const m=DB.visits.get(id);await dbPut(normMeta(Object.assign({},m,{pts:m.pts+100,at:new Date().toISOString()})));render();}",vic['id'])
    for r in rows:
        pass
    after=money(pg.inner_text('.hero .hv')); dlt=hu(D(str(vic['pts']+100))*D(str(vic['price']))*100)-hu(D(str(vic['pts']))*D(str(vic['price']))*100)
    t.chk('edycja wpisu (+100 pkt) zmienia „Zarobek razem” dokładnie o wartość 100 pkt tego wpisu', after-before==dlt, (before,after,dlt))
    T=tab('days')[0]; row=[x for x in T['body'] if x[0]==fd(vic['date'])][0]; T2=tab('months')[0]
    day_items=[r for r in rows if r['date']==vic['date']]
    t.chk('…oraz wiersz dnia i wiersz miesiąca', money(row[8])==agg(day_items,'full')['total']+dlt and money(T2['foot'][1])==after)
    pg.evaluate("async (id)=>{await dbDel([id]);render();}",vic['id'])
    after2=money(pg.inner_text('.hero .hv'))
    t.chk('usunięcie wpisu odejmuje go ze wszystkich zestawień', after2==before-vic['t'] and money(tab('weeks')[0]['foot'][7])==after2 and money(tab('months')[0]['foot'][1])==after2 and money(tab('days')[0]['foot'][8])==after2, (before,vic['t'],after2))
    # wykresy: tyle słupków, ile dni/tygodni/miesięcy z wpisami, etykieta najwyższego = maksimum
    set_range('y12'); items=[r for r in rows if exp['y12'][0]<=r['date']<=exp['y12'][1] and not (r['date']==vic['date'] and False)]
    cnt={}
    for tb in ('days','weeks','months','dow'): tab(tb); cnt[tb]=pg.locator('figure.chart g.band').count()
    da=pg.evaluate("dbList().map(m=>m.date)"); R=pg.evaluate("curRange()")
    live={'days':len({x for x in da if R['from']<=x<=R['to']}),'weeks':periods('w',R['from'],R['to'],da),'months':periods('m',R['from'],R['to'],da),'dow':7}
    t.chk('wykresy: słupek na każdy dzień z wpisami, na każdy tydzień i miesiąc zakresu (ciągła oś); 7 słupków dni tygodnia', cnt==live, (cnt,live))
    tab('months'); caps=[money(x) for x in pg.evaluate("[...document.querySelectorAll('figure.chart text.cap')].map(e=>e.textContent)")]
    mx=pg.evaluate("(()=>{const R=curRange(),l=dbList().filter(m=>m.date>=R.from&&m.date<=R.to);return Math.max(...grp(l,m=>m.date.slice(0,7)).map(x=>x.A.total));})()")
    t.chk('wykres miesięczny: etykieta nad najwyższym słupkiem = największy miesiąc (w pełnych zł)', hu(D(mx)/100)*100 in caps, (caps,mx))
    seg=pg.evaluate("(()=>{const R=curRange(),l=dbList().filter(m=>m.date>=R.from&&m.date<=R.to),A=agg(l);return {exp:[A.pe,A.rv,A.ex],flex:[...document.querySelectorAll('.segbar .sb')].map(e=>+e.style.flexGrow)};})()")
    t.chk('pasek struktury przychodów: proporcje = punkty : przeglądy : dodatkowe', len(seg['flex'])==3 and all(abs(a-b)<=a*1e-4 for a,b in zip(seg['exp'],seg['flex'])), seg)
    # ---------- luki w ewidencji: miesiąc bez wpisów (np. urlop) ----------
    ctxG=b.new_context(viewport={'width':1300,'height':1000}); pG=open_page(ctxG,errs=errs)
    def seedG(dates): pG.evaluate(SEED_JS,[[x,'AB',100,0,0,'',30,'man'] for x in dates])
    seedG(['2025-12-10','2026-01-05','2026-01-20','2026-02-03','2026-04-14','2026-04-15'])
    pG.click('#steps button[data-n="5"]')
    def bands(): return pG.evaluate("[...document.querySelectorAll('figure.chart g.band')].map(g=>g.getAttribute('aria-label'))")
    def setG(f,to):
        pG.fill('#i_r_from',f); pG.dispatch_event('#i_r_from','change'); pG.fill('#i_r_to',to); pG.dispatch_event('#i_r_to','change')
    def daG(): return pG.evaluate("dbList().map(m=>m.date)")
    setG('2026-01-01','2026-04-30'); pG.click('button[data-act="tab"][data-t="months"]'); bm=bands(); TM=[canon(x) for x in pG.evaluate(TABLES)][0]
    t.chk('wykres miesięczny z luką: styczeń, luty, MARZEC (0 zł – brak wpisów), kwiecień; tabela – tylko 3 miesiące z wpisami',
          [x.split(':')[0] for x in bm]==['styczeń 2026','luty 2026','marzec 2026','kwiecień 2026'] and bm[2].endswith('brak wpisów') and len(TM['body'])==3 and len(bm)==periods('m','2026-01-01','2026-04-30',daG()), (bm,len(TM['body'])))
    kw=[r for r in TM['body'] if r[0]=='kwiecień 2026'][0]
    t.chk('…„Zmiana do poprz. mies.” dla kwietnia = „—” (marzec bez wpisów, nie porównuje z lutym)', kw[2]=='—', kw[2])
    pG.click('button[data-act="tab"][data-t="weeks"]'); bw=bands()
    t.chk('wykres tygodniowy: pusty, niepełny tydzień 1 (29.12–04.01) pominięty; ciągła oś do końca zakresu (tydz. 2–18)', bw[0].startswith('Tydzień 2 ') and bw[-1].startswith('Tydzień 18 ') and len(bw)==periods('w','2026-01-01','2026-04-30',daG())==17 and sum('brak wpisów' in x for x in bw)==13, (len(bw),bw[0],bw[-1]))
    seedG(['2026-01-02']); setG('2026-01-01','2026-04-30'); pG.click('button[data-act="tab"][data-t="weeks"]'); bw=bands()
    t.chk('…z wpisem 02.01 niepełny tydzień 1 jest pokazany', bw[0].startswith('Tydzień 1 ') and len(bw)==periods('w','2026-01-01','2026-04-30',daG())==18, bw[0])
    pG.click('button[data-act="range"][data-p="y12"]'); pG.click('button[data-act="tab"][data-t="months"]'); bm=bands(); R=pG.evaluate("curRange()")
    cur=MONN[TODAY.month-1]+' '+str(TODAY.year)
    t.chk(f'„Ostatnie 12 mies.”: od pierwszego wpisu w historii (grudzień 2025) do bieżącego miesiąca ({cur}), bez miesięcy z przyszłości', bm[0].startswith('grudzień 2025') and bm[-1].startswith(cur) and len(bm)==periods('m',R['from'],R['to'],daG()), (len(bm),bm[0],bm[-1]))
    pG.click('button[data-act="range"][data-p="all"]'); bm2=bands()
    t.chk('„Wszystko”: ten sam ciąg miesięcy', [x.split(':')[0] for x in bm2]==[x.split(':')[0] for x in bm])
    ctxH=b.new_context(viewport={'width':1300,'height':1000}); pH=open_page(ctxH,errs=errs); pH.evaluate(SEED_JS,[['2026-03-02','AB',100,0,0,'',30,'man']])
    pH.click('#steps button[data-n="5"]'); pH.click('button[data-act="range"][data-p="y12"]'); pH.click('button[data-act="tab"][data-t="months"]')
    bh=pH.evaluate("[...document.querySelectorAll('figure.chart g.band')].map(g=>g.getAttribute('aria-label').split(':')[0])")
    t.chk('nowa ewidencja (pierwszy wpis w marcu): brak zerowych słupków za miesiące sprzed pierwszego wpisu', bh[0]=='marzec 2026' and len(bh)==TODAY.month-3+1, bh[:3])
    ctxG.close(); ctxH.close()
    t.chk('brak błędów JS', not errs, errs)
    t.done('T5 statystyki'); b.close()
