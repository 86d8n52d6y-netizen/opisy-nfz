# T11 – wydajność przy 5000 wpisów oraz wygląd na telefonie, tablecie i komputerze (zrzuty ekranu w testy/zrzuty/)
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
import json, tempfile, time
from decimal import Decimal, ROUND_HALF_UP
os.makedirs(SHOTS,exist_ok=True); TMP=tempfile.mkdtemp()
SEED5K="""async (N)=>{   // N wpisów: dni robocze od 2024-01-02, ok. 7 dziennie; co 3. wpis to wizyta z opisem (ok. 1,5 kB) i odpowiedziami
  let seed=12345;const rnd=()=>{seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;};
  const ops=[];let d=new Date(Date.UTC(2024,0,2)),n=0;const today=todayISO();const INI=['JK','AB','MN','','','PW','ZT',''];
  const txt='BADANIE LEKARSKIE STOMATOLOGICZNE. '+'Pacjent zgłosił się na wizytę kontrolną, wywiad ogólny bez zmian, higiena dobra. '.repeat(18);
  while(n<N){const iso=d.toISOString().slice(0,10);const dow=d.getUTCDay();
    if(iso>today){d=new Date(Date.UTC(2024,0,2));continue;}
    if(dow!==0&&(dow!==6||rnd()<0.2)){const k=5+Math.floor(rnd()*5);
      for(let i=0;i<k&&n<N;i++){const gen=n%3===0,at=iso+'T'+String(8+i).padStart(2,'0')+':'+String(Math.floor(rnd()*60)).padStart(2,'0')+':00.000Z';
        const m=normMeta({id:'s'+n.toString(36).padStart(5,'0'),no:n+1,ini:INI[Math.floor(rnd()*INI.length)],date:iso,created:at,at,src:gen?'gen':'man',codes:gen?['ST33','ST30','ST26','1101']:[],
          pts:Math.round((40+rnd()*400)*10)/10,price:iso<'2026-01-01'?1.81:1.84,pct:rnd()<0.8?40:35,revH:rnd()<0.1?Math.round(rnd()*6)/2:0,revRate:350,ex:rnd()<0.08?[{c:Math.round(rnd()*40000),d:'dodatkowa procedura'}]:[],min:rnd()<0.3?40:30,body:gen});
        ops.push({s:'visits',key:m.id,val:m});
        if(gen)ops.push({s:'bodies',key:m.id,val:{txt:txt+' #'+n,p:0,snap:{codes:m.codes,a:{'sh.age':'9','sh.api':'35','sh.gi':'1'},teeth:{'1101':{'11':{s:[],f:{}}}},quads:{'ST30':[1,2]},plan:null}}});
        n++;}}
    d=new Date(d.getTime()+86400000);}
  for(let i=0;i<ops.length;i+=1500)await DB.be.write(ops.slice(i,i+1500));
  cfg.seq=N;cfgSave();await dbReload();return {n:DB.visits.size,days:new Set(dbList().map(m=>m.date)).size};}"""
def ms(pg,js): return pg.evaluate("async ()=>{const t=performance.now();"+js+";await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return Math.round(performance.now()-t);}")
OVERFLOW="""()=>{const W=window.innerWidth,bad=[];
  const clipped=(e)=>{for(let p=e.parentElement;p&&p!==document.body;p=p.parentElement){const o=getComputedStyle(p).overflowX;if(o==='auto'||o==='scroll'||o==='hidden')return true;}return false;};
  document.querySelectorAll('header *, #main *, #bar *').forEach(e=>{const r=e.getBoundingClientRect();if(!r.width||!r.height)return;if((r.right>W+1||r.left<-1)&&!clipped(e))bad.push(e.tagName.toLowerCase()+'.'+String(e.className&&e.className.baseVal!==undefined?e.className.baseVal:e.className).split(' ')[0]+' → '+Math.round(r.left)+'…'+Math.round(r.right));});
  const small=[];document.querySelectorAll('#steps button, #main button, #bar button, #main input:not([hidden]), #main select').forEach(e=>{const r=e.getBoundingClientRect();if(!r.width||!r.height||e.disabled)return;if(r.height<24||r.width<24)small.push((e.dataset.act||e.id||e.tagName)+' '+Math.round(r.width)+'×'+Math.round(r.height));});
  return {pageScroll:document.documentElement.scrollWidth-W,bad:[...new Set(bad)].slice(0,8),small:[...new Set(small)].slice(0,8),nav:[...document.querySelectorAll('#steps button')].map(b=>{const r=b.getBoundingClientRect();return [b.textContent.trim(),Math.round(r.left),Math.round(r.right),Math.round(r.top)];})};}"""
with sync_playwright() as p:
    b=launch(p); t=T(); errs=[]
    ctx=b.new_context(viewport={'width':1280,'height':900},accept_downloads=True); pg=open_page(ctx,errs=errs)
    # ================= WYDAJNOŚĆ =================
    t0=time.time(); r=pg.evaluate(SEED5K,5000); seed_s=time.time()-t0
    t.chk(f'przygotowano 5000 wpisów ({r["days"]} dni pracy, ok. 1667 z opisem)', r['n']==5000, r)
    pg.close(); pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append('pageerror: '+str(e)))
    t0=time.time(); pg.goto(BASE); pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true"); start_ms=round((time.time()-t0)*1000)
    boot=pg.evaluate("Math.round(performance.now())")
    t.chk(f'uruchomienie z 5000 wpisów: {start_ms} ms do gotowości (limit 2000 ms)', start_ms<2000 and len(visits(pg))==5000, boot)
    M={}
    M['historia']=ms(pg,"state.step=4;ui.lim=40;render()")
    t.chk(f'Historia (40 najnowszych z 5000): {M["historia"]} ms (limit 300 ms)', M['historia']<300 and pg.locator('section.card.hist').count()==40)
    pg.fill('#i_hs_q','jk'); pg.wait_for_timeout(300)
    M['szukaj']=ms(pg,"ui.q='ab';render()")
    t.chk(f'wyszukiwanie w 5000 wpisach: {M["szukaj"]} ms (limit 300 ms)', M['szukaj']<300)
    pg.fill('#i_hs_q',''); pg.wait_for_timeout(100)
    while pg.locator('button[data-act="hmore"]').count() and pg.locator('section.card.hist').count()<200: pg.click('button[data-act="hmore"]')
    M['historia200']=ms(pg,"render()")
    t.chk(f'Historia rozwinięta do {pg.locator("section.card.hist").count()} wpisów: {M["historia200"]} ms (limit 600 ms)', M['historia200']<600)
    for tab in ('days','weeks','months','dow'):
        M['st_'+tab]=ms(pg,f"state.step=5;ui.range={{p:'all',from:'',to:''}};ui.tab='{tab}';render()")
    t.chk('Statystyki z całego okresu (5000 wpisów, 4 zakładki): '+', '.join(f'{k[3:]} {v} ms' for k,v in M.items() if k.startswith('st_'))+' (limit 500 ms każda)', all(v<500 for k,v in M.items() if k.startswith('st_')))
    M['st_miesiac']=ms(pg,"ui.range={p:'month',from:'',to:''};ui.tab='days';render()")
    t.chk(f'Statystyki bieżącego miesiąca: {M["st_miesiac"]} ms (limit 300 ms)', M['st_miesiac']<300)
    # sumy przy 5000 wpisów zgodne z niezależnym przeliczeniem
    rows=pg.evaluate("dbList().map(m=>[m.pts,m.price,m.revH,m.revRate,m.ex.reduce((a,e)=>a+e.c,0)])")
    Q=lambda x:int(x.quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    tot=sum(Q(Decimal(str(p_))*Decimal(str(pr))*100)+Q(Decimal(str(h))*Decimal(str(r_))*100)+e for p_,pr,h,r_,e in rows)   # niezależne przeliczenie (Decimal, połówki w górę)
    A=pg.evaluate("(()=>{const l=dbList(),A=agg(l);const g=f=>grp(l,f).reduce((s,x)=>s+x.A.total,0);return {total:A.total,d:g(m=>m.date),w:g(m=>weekOf(m.date).key),m:g(m=>m.date.slice(0,7))};})()")
    t.chk(f'suma 5000 wpisów = suma dni = suma tygodni = suma miesięcy = niezależne przeliczenie ({tot/100:,.2f} zł)'.replace(',',' '), A['total']==A['d']==A['w']==A['m']==tot, (A,tot))
    pg.click('#steps button[data-n="4"]')
    t0=time.time(); pg.fill('#f_q_pts','123'); pg.press('#f_q_pts','Enter'); pg.wait_for_function("dbList().length===5001&&!ui.busy"); M['zapis']=round((time.time()-t0)*1000)
    t.chk(f'szybki wpis przy 5000 wpisach: {M["zapis"]} ms od Enter do zapisania (limit 500 ms)', M['zapis']<500)
    pg.click('#steps button[data-n="6"]'); t0=time.time()
    with pg.expect_download() as d: pg.click('button[data-act="bkexport"]')
    path=os.path.join(TMP,'k5000.json'); d.value.save_as(path); M['kopia']=round((time.time()-t0)*1000); size=os.path.getsize(path)
    t.chk(f'kopia zapasowa 5001 wpisów: {M["kopia"]} ms, plik {size/1e6:.1f} MB (limit 4000 ms)', M['kopia']<4000 and len(json.load(open(path,encoding="utf-8"))['visits'])==5001)
    ctxB=b.new_context(viewport={'width':1280,'height':900}); pB=open_page(ctxB,errs=errs); pB.click('#steps button[data-n="6"]'); t0=time.time()
    pB.set_input_files('#bk-file',path); pB.wait_for_function("ui.msg&&ui.msg.includes('dodano 5001')&&!ui.busy",timeout=20000); M['import']=round((time.time()-t0)*1000)
    t.chk(f'wczytanie kopii 5001 wpisów na pustym urządzeniu: {M["import"]} ms (limit 6000 ms)', M['import']<6000 and len(visits(pB))==5001)
    est=pg.evaluate("navigator.storage&&navigator.storage.estimate?navigator.storage.estimate().then(e=>Math.round(e.usage/1e5)/10):null")
    print(f'     zajętość bazy przeglądarki przy 5001 wpisach: ok. {est} MB')
    ctxB.close()
    # ================= WYGLĄD =================
    # bieżąca wizyta z rozliczeniem (krok 3) – żeby każdy widok miał treść
    pg.click('#steps button[data-n="1"]'); pg.fill('#i_sv_ini','jk'); pg.fill('#i_sh_age','9'); pg.click('button.plan-btn[data-p="o5"][data-w="I"]'); pg.click('#bar button.btn:not(.ghost)')
    pg.click('#card-ST30 button[data-act="quadset"][data-q="1,2"]'); pg.click('#card-1101 .tooth[data-t="11"]'); pg.click('#bar button.btn:not(.ghost)'); idle(pg)
    pg.fill('#i_sv_revH','1,5'); pg.press('#i_sv_revH','Tab'); pg.click('button[data-act="xadd"][data-s="v"]'); pg.fill('[data-x="v|0|a"]','150'); pg.fill('[data-x="v|0|d"]','dodatkowa procedura'); pg.press('[data-x="v|0|d"]','Tab'); idle(pg)
    NAMES={1:'1-kody',2:'2-pytania',3:'3-opis',4:'4-historia',5:'5-statystyki',6:'6-ustawienia'}
    res={}
    for label,(w,h),scheme in (('telefon',(390,844),'light'),('tablet',(768,1024),'light'),('komputer',(1280,900),'light'),('telefon-ciemny',(390,844),'dark'),('komputer-ciemny',(1280,900),'dark'),('maly-telefon',(320,640),'light')):
        pg.set_viewport_size({'width':w,'height':h}); pg.emulate_media(color_scheme=scheme)
        for n in (1,2,3,4,5,6):
            pg.click(f'#steps button[data-n="{n}"]'); pg.wait_for_timeout(120)
            if n==5: pg.click('button[data-act="range"][data-p="y12"]'); pg.click('button[data-act="tab"][data-t="months"]'); pg.wait_for_timeout(120)
            res[(label,n)]=pg.evaluate(OVERFLOW)
            if label in ('telefon','komputer','telefon-ciemny') or n in (3,5): pg.screenshot(path=os.path.join(SHOTS,f'{label}-{NAMES[n]}.png'),full_page=True)
        if label=='telefon':
            for tb in ('days','weeks','dow'):
                pg.click('#steps button[data-n="5"]'); pg.click(f'button[data-act="tab"][data-t="{tb}"]'); pg.wait_for_timeout(100); res[(label,'5'+tb)]=pg.evaluate(OVERFLOW)
                pg.screenshot(path=os.path.join(SHOTS,f'{label}-5-statystyki-{tb}.png'),full_page=True)
    for label in ('telefon','tablet','komputer','telefon-ciemny','komputer-ciemny','maly-telefon'):
        rr={k:v for k,v in res.items() if k[0]==label}
        ps={k[1]:v['pageScroll'] for k,v in rr.items() if v['pageScroll']>1}; bad={k[1]:v['bad'] for k,v in rr.items() if v['bad']}
        t.chk(f'{label}: żaden z {len(rr)} widoków nie wymaga przewijania strony w bok, nic nie wystaje poza ekran', not ps and not bad, (ps,bad))
    nav=res[('telefon',1)]['nav']
    t.chk('telefon (390 px): wszystkie 6 zakładek nawigacji mieści się na ekranie', len(nav)==6 and all(l>=0 and r<=390 for _,l,r,_ in nav), nav)
    nav=res[('maly-telefon',1)]['nav']
    t.chk('mały telefon (320 px): 6 zakładek nawigacji widocznych', len(nav)==6 and all(l>=0 and r<=320 for _,l,r,_ in nav), nav)
    small={k:v['small'] for k,v in res.items() if k[0] in ('telefon','maly-telefon') and v['small']}
    t.chk('telefon: wszystkie przyciski i pola mają co najmniej 24×24 px (WCAG 2.2, kryterium 2.5.8)', not small, small)
    # przełącznik trybu zapisu działa dotykiem na telefonie i przetrwa ponowne uruchomienie
    pg.set_viewport_size({'width':390,'height':844}); pg.emulate_media(color_scheme='light'); pg.click('#steps button[data-n="6"]')
    before=pg.evaluate("cfg.auto"); pg.click('button[data-act="automode"]'); after=pg.evaluate("cfg.auto")
    pg.close(); pg=open_page(ctx,errs=errs)
    t.chk('przełącznik trybu zapisu: jedno dotknięcie zmienia tryb, ustawienie zostaje po ponownym uruchomieniu', before is False and after is True and pg.evaluate("cfg.auto") is True)
    t.chk('brak błędów JS', not errs, errs[:3])
    print('     pomiary [ms]:',json.dumps(M,ensure_ascii=False)); print('     zrzuty ekranu:',SHOTS)
    t.done('T11 wydajność i wygląd'); b.close()
