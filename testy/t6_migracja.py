# T6 – przeniesienie historii z poprzedniej wersji (localStorage, commit e8476e8) do nowej bazy; stawka 1,81 → 1,84
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
import datetime
TODAY=datetime.date.today().isoformat()
MK="""(c)=>{state.step=1;state.plan=null;state.codes=[];state.a={};state.teeth={};state.quads={};state.unknown=[];state.savedId=null;state.saveInfo=null;initDefaults();
  state.a['sh.age']=c.age;state.a['sv.ini']=c.ini;if(c.date)state.a['sv.date']=c.date;state.codes=c.codes.slice();
  Object.entries(c.quads||{}).forEach(([k,v])=>state.quads[k]=v);
  Object.entries(c.teeth||{}).forEach(([k,ts])=>{state.teeth[k]={};ts.forEach(t=>state.teeth[k][t]={s:[],f:{}});});
  Object.entries(c.a||{}).forEach(([k,v])=>state.a[k]=v);
  state.step=3;render();
  const m=histIdx().find(x=>x.id===state.savedId);return Object.assign({},m,{txt:histText(m.id),snapCodes:histGet(m.id).snap.codes});}"""
LSKEYS="()=>{const o=[];for(let i=0;i<localStorage.length;i++)o.push(localStorage.key(i));return o.sort();}"
with sync_playwright() as p:
    b=launch(p); ctx=b.new_context(viewport={'width':1100,'height':900}); errs=[]; t=T()
    # ---------- stara wersja: trzy wizyty z różnymi stawkami ----------
    old=ctx.new_page(); old.goto(V9); old.wait_for_function("typeof histIdx==='function'")
    e1=old.evaluate(MK,dict(age='9',ini='JK',codes=['ST33','ST30','ST26','1101'],quads={'ST30':[1,2]},teeth={'1101':[11,12,21,22]},a={'sh.api':'35','sh.gi':'1'}))
    old.evaluate("()=>{cfg.pct=35;LS.set('pct',35);}")
    e2=old.evaluate(MK,dict(age='40',ini='AB',date='2026-11-10',codes=['ST02'],teeth={'ST02':[46]}))
    old.evaluate("()=>{cfg.price=1.9;LS.set('price',1.9);}")
    e3=old.evaluate(MK,dict(age='7',ini='CD',date='2026-10-30',codes=['ST34','ST30','ST26','1101'],quads={'ST30':[1,2,3,4]},teeth={'1101':[16,26]}))
    e4=old.evaluate(MK,dict(age='5',ini='EF',date='2026-10-30',codes=['ST28','ST30G'],))
    olds=[e1,e2,e3,e4]
    old.evaluate("(id)=>localStorage.removeItem('opisyNFZ.h.'+id)",e4['id'])     # uszkodzony wpis: indeks jest, treści opisu brak
    keys0=old.evaluate(LSKEYS)
    t.chk('stara wersja: 4 wpisy w localStorage (stawki 1,81/40%, 1,81/35%, 1,90/35%, 1,90/35%)', [(x['ini'],x['price'],x['pct']) for x in olds]==[('JK',1.81,40),('AB',1.81,35),('CD',1.9,35),('EF',1.9,35)] and 'opisyNFZ.hidx' in keys0 and 'opisyNFZ.price' in keys0, [(x['ini'],x['pts'],x['zl'],x['doc']) for x in olds])
    old.close()
    # ---------- nowa wersja na tym samym adresie ----------
    pg=open_page(ctx,errs=errs); v=visits(pg); by={x['id']:x for x in v}
    t.chk('wszystkie 4 wpisy przeniesione do nowej bazy (te same identyfikatory)', len(v)==4 and set(by)=={x['id'] for x in olds} and pg.evaluate("DB.kind")=='idb')
    bad=[]
    for o in olds:
        n=by.get(o['id']); 
        if not n: bad.append(('brak',o['ini'])); continue
        if (n['ini'],n['date'],n['codes'],n['pts'],n['price'],n['pct'])!=(o['ini'],o['date'],o['codes'],o['pts'],o['price'],o['pct']): bad.append(('pola',o['ini'],n))
        if n['k']['pc']!=round(o['zl']*100) or n['k']['sh']!=round(o['doc']*100): bad.append(('kwoty',o['ini'],n['k'],o['zl'],o['doc']))
        if n['src']!='gen' or not n['visit'] or n['min'] is not None or n['revH']!=0 or n['ex']!=[]: bad.append(('typ',o['ini'],n))
    t.chk('inicjały, daty, kody, punkty i stawka każdego wpisu bez zmian; kwoty identyczne jak w starej wersji', not bad, bad)
    t.chk('stare wpisy zachowują swoją stawkę (1,81 / 1,90), nowa stawka ogólna to 1,84 zł', pg.evaluate("cfg.price")==1.84 and by[e1['id']]['price']==1.81 and by[e3['id']]['price']==1.9)
    t.chk('wybrany wcześniej udział lekarza 35% zostaje, przeglądy 350 zł/h, tryb z inicjałami', pg.evaluate("[cfg.pct,cfg.rev,cfg.auto,cfg.basis]")==[35,350,False,'full'])
    txt=pg.evaluate("async (ids)=>{const o={};for(const id of ids){const b=await dbBody(id);o[id]=b?bodyText(b):null;}return o;}",[x['id'] for x in olds])
    t.chk('teksty opisów identyczne co do znaku (3 wpisy); wpis bez treści przeniesiony z samymi kwotami', all(txt[x['id']]==x['txt'] for x in olds[:3]) and txt[e4['id']] is None and by[e4['id']]['body'] is False and by[e1['id']]['body'] is True, {x['ini']:len(x['txt'] or '') for x in olds})
    nos=sorted((x['date'],x['no'],x['ini']) for x in v)
    t.chk('numery wpisów nadane kolejno wg daty (1–4), bez powtórzeń', sorted(x['no'] for x in v)==[1,2,3,4] and [n[1] for n in nos]==sorted(n[1] for n in nos), nos)
    keys1=pg.evaluate(LSKEYS)
    t.chk('stare klucze usunięte z localStorage dopiero po sprawdzeniu przeniesienia; zostają tylko ustawienia', [k for k in keys1 if k.startswith('opisyNFZ')]==['opisyNFZ@'+pg.evaluate("G.user.id")+'.cfg'] and all(k.startswith('gabinet.') or k.startswith('opisyNFZ@') for k in keys1), keys1)
    # widok
    pg.click('#steps button[data-n="4"]')
    cards=clean(pg.inner_text('#hist-list'))
    t.chk('Historia pokazuje 4 wpisy z własną stawką (× 1,81 zł); wpis bez treści nie ma przycisku „Kopiuj opis”', pg.locator('section.card.hist').count()==4 and pg.locator(f'#hist-{e4["id"]} button[data-act="hcopy"]').count()==0 and pg.locator(f'#hist-{e1["id"]} button[data-act="hcopy"]').count()==1 and '286,8 pkt × 1,81 zł · 519,11 zł' in cards and '362,1 pkt × 1,9 zł' in cards, cards[:200])
    pg.click(f'#hist-{e1["id"]} button[data-act="hshow"]'); pg.wait_for_function(f"document.getElementById('htxt-{e1['id']}').textContent.length>50")
    t.chk('„Pokaż opis” wyświetla zapisany tekst', pg.inner_text(f'#htxt-{e1["id"]}').replace('\\r','')[:400].strip()[:60]==e1['txt'].strip()[:60])
    pg.click('#steps button[data-n="5"]'); pg.click('button[data-act="range"][data-p="all"]')
    tot=sum(round(x['zl']*100) for x in olds)
    t.chk('Statystyki liczą przeniesione wpisy: razem = suma kwot ze starej wersji', pg.evaluate("agg(dbList()).total")==tot and pg.evaluate("agg(dbList()).vis")==4, (pg.evaluate("agg(dbList()).total"),tot))
    # ponowne uruchomienie: bez powtórnej migracji i dubli
    pg.close(); pg=open_page(ctx,errs=errs)
    t.chk('ponowne uruchomienie: nadal 4 wpisy, bez dubli', len(visits(pg))==4)
    # „Otwórz i popraw” na przeniesionym wpisie
    pg.click('#steps button[data-n="4"]'); pg.click(f'#hist-{e1["id"]} button[data-act="hopen"]'); pg.wait_for_function("state.step===3"); idle(pg)
    out=pg.evaluate("buildOut().map(o=>plain(o.text)).join('\\n\\n')")
    n1=[x for x in visits(pg) if x['id']==e1['id']][0]
    t.chk('otwarcie przeniesionego wpisu: formularz odtworzony, opis generuje się identycznie, stawka wpisu 1,81 zostaje', out==e1['txt'] and pg.evaluate("state.codes.join(',')")=='ST33,ST30,ST26,1101' and n1['price']==1.81 and n1['pts']==e1['pts'] and len(visits(pg))==4 and '1,81' in clean(pg.inner_text('#pts-card .warn')), clean(pg.inner_text('#pts-card .warn'))[:160])
    t.chk('…i uzupełnia mu brakujący czas wizyty (30 min)', n1['min']==30)
    pg.click('#pts-card button[data-act="usecur"]'); idle(pg)
    n1=[x for x in visits(pg) if x['id']==e1['id']][0]
    t.chk('„Przelicz po aktualnych stawkach” przelicza wpis na 1,84 zł / 35%', n1['price']==1.84 and n1['pct']==35 and n1['k']['pc']==52771, n1['k'])
    # uszkodzony indeks starej wersji nie zatrzymuje aplikacji
    ctx2=b.new_context(); pz=ctx2.new_page(); pz.goto(V9); pz.evaluate("()=>{localStorage.setItem('opisyNFZ.hidx','{to nie jest JSON');localStorage.setItem('opisyNFZ.pct','35');}"); pz.close()
    e2s=[]; p2=open_page(ctx2,errs=e2s)
    t.chk('uszkodzony stary indeks: aplikacja startuje normalnie, nic nie przenosi', p2.evaluate("DB.ready")==True and len(visits(p2))==0 and not e2s, e2s)
    t.chk('brak błędów JS', not errs, errs)
    t.done('T6 migracja starej historii'); b.close()
