# T9 – regresja generatora: te same dane wejściowe w wersji wyjściowej (e8476e8) i nowej → identyczny opis, punkty i błędy NFZ
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
import random, re
random.seed(7)
DEFS="""()=>{const f=(k,v)=>typeof v==='function'?v.toString():v;return {D:JSON.stringify(D,f),SEG:JSON.stringify(SEG),PLANS:JSON.stringify(PLANS,f),GROUPS:JSON.stringify(GROUPS,f),PTS:JSON.stringify(PTS),PTS_AN:JSON.stringify(PTS_AN),
  NFZ_MIN:JSON.stringify(NFZ_MIN),NFZ_NOSUM:JSON.stringify(NFZ_NOSUM),AOT_MIN:JSON.stringify(AOT_MIN),codes:Object.keys(D)};}"""
# wypełnianie formularza przez prawdziwe elementy strony; decyzja dla każdego elementu zależy tylko od ziarna i jego nazwy,
# więc obie wersje dostają dokładnie te same kliknięcia i wartości
RUN="""(c)=>{
  const seed=c.seed>>>0;
  const H=(s)=>{let h=(2166136261^seed)>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}h^=h>>>13;h=Math.imul(h,0x5bd1e995)>>>0;h^=h>>>15;return (h>>>0)/4294967296;};
  if(typeof resetVisit==='function')resetVisit();else{state.step=1;state.plan=null;state.codes=[];state.a={};state.teeth={};state.quads={};state.unknown=[];state.savedId=null;state.saveInfo=null;initDefaults();}
  if(c.age!=='')state.a['sh.age']=c.age; state.codes=c.codes.slice(); state.step=2; render();
  const fire=(el,t)=>el.dispatchEvent(new Event(t,{bubbles:true}));
  const cards=()=>[...document.querySelectorAll('#main section[id^="card-"]')];
  if(c.fill){
    const first=[];
    cards().forEach(cd=>{cd.querySelectorAll('[data-act="quad"]').forEach(e=>{if(H(cd.id+'|quad|'+e.dataset.q)<0.45)first.push('#'+cd.id+' [data-act="quad"][data-q="'+e.dataset.q+'"]');});
      cd.querySelectorAll('.tooth[data-act="tooth"]').forEach(e=>{if(H(cd.id+'|tooth|'+e.dataset.t)<0.09)first.push('#'+cd.id+' .tooth[data-act="tooth"][data-t="'+e.dataset.t+'"]');});});
    first.forEach(s=>{const e=document.querySelector(s);if(e)e.click();});
    const surf=[];cards().forEach(cd=>cd.querySelectorAll('[data-act="surf"]').forEach(e=>{const t=e.dataset.t||(e.closest('[data-t]')||{dataset:{}}).dataset.t,sf=e.dataset.s||e.dataset.sf||'';
      if(state.teeth[cd.id.slice(5)]&&state.teeth[cd.id.slice(5)][t]&&H(cd.id+'|surf|'+t+'|'+sf)<0.35)surf.push([cd.id,t,sf]);}));
    surf.forEach(([cid,t,sf])=>{const e=[...document.querySelectorAll('#'+cid+' [data-act="surf"]')].find(x=>((x.dataset.t||(x.closest('[data-t]')||{dataset:{}}).dataset.t)===t)&&((x.dataset.s||x.dataset.sf||'')===sf));if(e)fire(e,'click');});
    for(let pass=0;pass<3;pass++){
      const segs=new Map();cards().forEach(cd=>cd.querySelectorAll('button[data-act="seg"]').forEach(e=>{const k=cd.id+'|'+e.dataset.key;if(!segs.has(k))segs.set(k,[]);segs.get(k).push(e.dataset.v);}));
      segs.forEach((opts,k)=>{const i=k.indexOf('|'),cid=k.slice(0,i),key=k.slice(i+1);const idx=Math.floor(H('seg|'+k)*(opts.length+0.5));if(idx>=opts.length)return;
        const e=[...document.querySelectorAll('#'+cid+' button[data-act="seg"]')].find(x=>x.dataset.key===key&&x.dataset.v===opts[idx]);if(e&&!e.classList.contains('on'))e.click();});
      const chks=[];cards().forEach(cd=>cd.querySelectorAll('button[data-act="chk"]').forEach(e=>{if(H('chk|'+cd.id+'|'+e.dataset.key+'|'+e.dataset.v)<0.4)chks.push([cd.id,e.dataset.key,e.dataset.v]);}));
      chks.forEach(([cid,key,v])=>{const e=[...document.querySelectorAll('#'+cid+' button[data-act="chk"]')].find(x=>x.dataset.key===key&&x.dataset.v===v);if(e&&!e.classList.contains('on'))e.click();});
      const ids=[...document.querySelectorAll('#main section[id^="card-"] input[data-key], #main section[id^="card-"] select[data-key]')].map(e=>e.id).filter(Boolean);
      ids.forEach(id=>{const e=document.getElementById(id);if(!e)return;const key=e.dataset.key;
        if(e.tagName==='SELECT'){const i=Math.floor(H('sel|'+key)*e.options.length);if(e.selectedIndex!==i){e.selectedIndex=i;fire(e,'change');}return;}
        if(H('inp|'+key)<0.2)return;
        const val=e.getAttribute('inputmode')==='decimal'?String(1+Math.floor(H('v|'+key)*40)):('tekst '+Math.floor(H('v|'+key)*1000));
        if(e.value!==val){e.value=val;fire(e,'input');fire(e,'change');}});
    }
  }
  state.step=3; render();
  const outs=buildOut(),P=nfzPoints(),I=nfzIssues();
  return {txt:outs.map(o=>o.code+'\\n'+plain(o.text)).join('\\n\\n=====\\n\\n'),pts:P.total,rows:P.rows.map(r=>[r.c,r.q,r.base,r.k,r.pts]),err:I.err.map(e=>e.msg).sort(),warn:I.warn.map(w=>w.msg).sort(),
    miss:missCount(),a:Object.keys(state.a).filter(k=>!k.startsWith('sv.')&&!k.startsWith('hs.')).sort().map(k=>k+'='+JSON.stringify(state.a[k])).join(';'),teeth:JSON.stringify(state.teeth),quads:JSON.stringify(state.quads)};
}"""
with sync_playwright() as p:
    b=launch(p); t=T(); eo=[]; en=[]
    c1=b.new_context(viewport={'width':1100,'height':900}); old=c1.new_page(); old.on('pageerror',lambda e: eo.append(str(e))); old.goto(V9); old.wait_for_function("typeof buildOut==='function'")
    c2=b.new_context(viewport={'width':1100,'height':900}); new=open_page(c2,errs=en)
    d1=old.evaluate(DEFS); d2=new.evaluate(DEFS)
    for k in ('D','SEG','PLANS','GROUPS','PTS','PTS_AN','NFZ_MIN','NFZ_NOSUM','AOT_MIN'):
        t.chk(f'definicje „{k}” identyczne z wersją wyjściową'+(f' ({len(d1[k])} znaków)' if k in ('D','SEG') else ''), d1[k]==d2[k])
    codes=d1['codes']; ages=['','2','4','5','6','9','12','17','18','40']
    cases=[]
    for c in codes:
        for a in ages: cases.append(dict(seed=1,age=a,codes=[c],fill=False))          # same wartości domyślne
        for s in (11,12,13): cases.append(dict(seed=s,age=random.choice(ages[1:]),codes=[c],fill=True))
    plans=new.evaluate("Object.entries(PLANS).flatMap(([g,o])=>Object.entries(o.v).map(([w,x])=>({g,w,codes:x})))")
    for pl in plans:
        for s,a in ((21,'4'),(22,'9'),(23,'16')): cases.append(dict(seed=s,age=a,codes=pl['codes'],fill=True))
    for s in range(100,500):
        k=random.choice([1,2,2,3,3,4,5,6]); cases.append(dict(seed=s,age=random.choice(ages),codes=random.sample(codes,k),fill=True))
    diffs=[]; filled=0; chars=0; wdiff=set()
    for c in cases:
        r1=old.evaluate(RUN,c); r2=new.evaluate(RUN,c)
        if (r1['a'],r1['teeth'],r1['quads'])!=(r2['a'],r2['teeth'],r2['quads']): diffs.append(('różny stan formularza',c)); continue
        if r1['txt']!=r2['txt']: diffs.append(('opis',c,next((i for i,(x,y) in enumerate(zip(r1['txt'],r2['txt'])) if x!=y),-1)))
        if r1['pts']!=r2['pts'] or r1['rows']!=r2['rows']: diffs.append(('punkty',c,r1['pts'],r2['pts']))
        if r1['err']!=r2['err']: diffs.append(('błędy NFZ',c,[e for e in r1['err'] if e not in r2['err']],[e for e in r2['err'] if e not in r1['err']]))
        if r1['miss']!=r2['miss']: diffs.append(('liczba pól do uzupełnienia',c,r1['miss'],r2['miss']))
        for w in set(r1['warn'])^set(r2['warn']): wdiff.add(('stara: ' if w in r1['warn'] else 'nowa:  ')+re.sub(r'\d+','N',w)[:110])
        chars+=len(r1['txt']); filled+= 1 if c['fill'] and r1['teeth']!='{}' else 0
    t.chk(f'{len(cases)} scenariuszy (każdy kod × 10 wariantów wieku, 8 planów wizyt, 400 losowych zestawów z wypełnianiem pól i diagramu): opis, punkty, błędy NFZ i liczba braków identyczne – porównano {chars//1000} tys. znaków opisów', not diffs, diffs[:4])
    t.chk('w scenariuszach rzeczywiście zaznaczano zęby i wypełniano pola', filled>250, filled)
    print('     różnice w ostrzeżeniach (zamierzone – nowa zasada czasu wizyty):'); [print('       '+w) for w in sorted(wdiff)]
    t.chk('ostrzeżenia różnią się tylko komunikatami o czasie wizyty', all(('czas' in w.lower() or 'wizyt' in w.lower() or 'min' in w.lower()) for w in wdiff), sorted(wdiff))
    # kody wpisywane ręcznie
    r=new.evaluate("()=>{resetVisit();addCodes('st33, 1101; 23.1503 ST99 st30e');return {codes:state.codes.slice(),unk:state.unknown.slice()};}")
    t.chk('wpisywanie kodów: „st33, 1101; 23.1503 ST99 st30e” → ST33, 1101, 1503, ST30E; nieznany tylko ST99 (poprawka błędu „23”)', r['codes']==['ST33','1101','1503','ST30E'] and r['unk']==['ST99'], r)
    t.chk('brak błędów JS w obu wersjach', not eo and not en, (eo[:2],en[:2]))
    t.done('T9 regresja generatora'); b.close()
