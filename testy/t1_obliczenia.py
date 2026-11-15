# T1 – obliczenia, zaokrąglenia, parsowanie liczb i dat (porównanie z niezależnym liczeniem w Pythonie – Decimal / datetime)
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
from decimal import Decimal, ROUND_HALF_UP
import random, datetime
random.seed(11)
def q2(x): return int((x*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
with sync_playwright() as p:
    b=launch(p)
    ctx=b.new_context(); errs=[]; pg=open_page(ctx,errs=errs); t=T()
    # przykłady ze specyfikacji
    for pts,zl in [(100,184),(150,276),(200,368),(300,552),(500,920)]:
        t.chk(f'{pts} pkt × 1,84 = {zl} zł', pg.evaluate(f"centsPts({pts},1.84)")==zl*100)
    for h,zl in [(1,350),(2,700),(3,1050),(4,1400),(0.5,175),(1.5,525)]:
        t.chk(f'{h} h przeglądów × 350 = {zl} zł', pg.evaluate(f"centsHours({h},350)")==zl*100)
    t.chk('domyślne stawki: 1,84 zł/pkt, 350 zł/h, 40%', pg.evaluate("[cfg.price,cfg.rev,cfg.pct,PRICE_DEF,REV_DEF]")==[1.84,350,40,1.84,350])
    # losowe: punkty (2 miejsca) × stawka (4 miejsca) → grosze, zaokrąglenie połówek w górę
    cases=[[round(random.uniform(0,3000),random.choice([0,1,2])), random.choice([1.84,1.81,1.03,2.0,1.9999,0.5,1.845,1.8375])] for _ in range(4000)]
    cases+= [[294.5,1.81],[576.5,1.81],[7.5,1.81],[0.5,1.81],[70.5,1.81],[0.01,1.84],[1e6,99.9999]]
    got=pg.evaluate("(cs)=>cs.map(c=>centsPts(c[0],c[1]))",cases)
    bad=[(c,g,q2(Decimal(str(c[0]))*Decimal(str(c[1])))) for c,g in zip(cases,got) if g!=q2(Decimal(str(c[0]))*Decimal(str(c[1])))]
    t.chk(f'punkty→zł: {len(cases)} losowych przypadków zgodnych z Decimal (połówki w górę)', not bad, bad[:3])
    # udział lekarza
    cs=[[random.randint(0,500000), random.choice([40,35,0,100,33.3])] for _ in range(3000)]+[[1030,35],[53305,35],[1,50],[3,50]]
    got=pg.evaluate("(cs)=>cs.map(c=>centsPct(c[0],c[1]))",cs)
    bad=[(c,g) for c,g in zip(cs,got) if g!=int((Decimal(c[0])*Decimal(str(c[1]))/100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))]
    t.chk(f'udział lekarza: {len(cs)} przypadków zgodnych z Decimal', not bad, bad[:3])
    # godziny przeglądów
    cs=[[round(random.uniform(0,24),random.choice([0,1,2])), random.choice([350,350.5,299.99,120])] for _ in range(3000)]+[[0.25,350],[0.33,350],[1.75,350],[0.01,350]]
    got=pg.evaluate("(cs)=>cs.map(c=>centsHours(c[0],c[1]))",cs)
    bad=[(c,g) for c,g in zip(cs,got) if g!=q2(Decimal(str(c[0]))*Decimal(str(c[1])))]
    t.chk(f'przeglądy: {len(cs)} przypadków zgodnych z Decimal', not bad, bad[:3])
    # wpis: kategorie osobno i suma, obie podstawy
    r=pg.evaluate("""()=>{const m={pts:286.8,price:1.84,pct:40,revH:1.5,revRate:350,ex:[{c:15000,d:'a'},{c:2550,d:'b'}]};cfg.basis='full';const f=calc(m);cfg.basis='share';const s=calc(m);cfg.basis='full';return [f,s];}""")
    f,s=r
    t.chk('wpis: punkty 527,71 + przeglądy 525,00 + dodatkowe 175,50 = 1228,21 (pełna wartość)', [f['pc'],f['rv'],f['ex'],f['pe'],f['total']]==[52771,52500,17550,52771,122821], f)
    t.chk('wpis: udział lekarza 40% = 211,08; razem 911,58 (podstawa „udział”)', [s['sh'],s['pe'],s['total']]==[21108,21108,91158], s)
    t.chk('kategorie nie mieszają się: total = pe + rv + ex', f['total']==f['pe']+f['rv']+f['ex'] and s['total']==s['pe']+s['rv']+s['ex'])
    # parsowanie liczb
    pn=pg.evaluate("""()=>['150','61,2','61.2',' 1 234,5 ','0','','abc','-5','1,2,3','1e3','١٢','12,','.5','007'].map(v=>{const x=parseNum(v);return isNaN(x)?null:x;})""")
    t.chk('parseNum: liczby z przecinkiem/kropką, odrzuca śmieci i ujemne', pn==[150,61.2,61.2,1234.5,0,None,None,None,None,None,None,None,None,7], pn)
    tc=pg.evaluate("""()=>['150','150,5','150.50','0,005','0,004','1 234,56','12 zł','12,345','12.345,67','-1','','x',150.555,0.1+0.2].map(v=>{const x=toCents(v);return isNaN(x)?null:x;})""")
    t.chk('toCents: kwoty → grosze (połówki w górę), odrzuca błędne', tc==[15000,15050,15050,1,0,123456,1200,1235,None,None,None,None,15056,30], tc)
    # daty: tydzień ISO, dzień tygodnia, koniec miesiąca – 3000 losowych dat + granice roku
    ds=[datetime.date(2020,1,1)+datetime.timedelta(days=random.randint(0,4000)) for _ in range(3000)]
    ds+=[datetime.date(y,m,d) for y in (2024,2025,2026,2027,2028) for m,d in ((12,28),(12,29),(12,30),(12,31),(1,1),(1,2),(1,3),(1,4),(2,28),(3,1))]
    got=pg.evaluate("""(ds)=>ds.map(d=>{const w=weekOf(d);return [w.y,w.w,dowOf(d),w.from,w.to,monthEnd(d),addDays(d,1),validDate(d)];})""",[d.isoformat() for d in ds])
    bad=[]
    for d,g in zip(ds,got):
        iy,iw,idw=d.isocalendar(); mon=d-datetime.timedelta(days=d.weekday())
        me=(d.replace(day=28)+datetime.timedelta(days=4)); me=me-datetime.timedelta(days=me.day)
        exp=[iy,iw,d.weekday(),mon.isoformat(),(mon+datetime.timedelta(days=6)).isoformat(),me.isoformat(),(d+datetime.timedelta(days=1)).isoformat(),True]
        if g!=exp: bad.append((d.isoformat(),g,exp))
    t.chk(f'daty: {len(ds)} dat – tydzień ISO, dzień tygodnia, koniec miesiąca zgodne z Pythonem', not bad, bad[:2])
    vd=pg.evaluate("['2026-02-29','2026-13-01','2026-11-31','1999-12-31','2026-11-15','','2026-1-5','abc'].map(validDate)")
    t.chk('validDate odrzuca nieistniejące daty', vd==[False,False,False,False,True,False,False,False], vd)
    t.chk('daysBetween / calDays', pg.evaluate("[daysBetween('2026-10-25','2026-10-26'),daysBetween('2026-03-28','2026-03-30'),daysBetween('2026-01-01','2026-12-31')]")==[1,2,364])
    t.chk('formaty: 1228,21 zł · 286,8 pkt · 1,5 h · 4 h 51 min', [clean(x) for x in pg.evaluate("[fmtC(122821),fmtP(286.8)+' pkt',fmtH(1.5),fmtMin(291),fmtMin(45),fmtC(0)]")]==['1228,21 zł','286,8 pkt','1,5 h','4 h 51 min','45 min','0,00 zł'], pg.evaluate("[fmtC(122821),fmtP(286.8)+' pkt',fmtH(1.5),fmtMin(291),fmtMin(45),fmtC(0)]"))
    t.chk('brak błędów JS', not errs, errs)
    t.done('T1 obliczenia'); b.close()
