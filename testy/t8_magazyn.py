# T8 – magazyn danych: awarie i sytuacje nietypowe (brak IndexedDB, zablokowana pamięć, błąd zapisu, dwie karty)
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
NO_IDB="Object.defineProperty(window,'indexedDB',{get(){return undefined;},configurable:true});"
HANG_IDB="(()=>{const real=window.indexedDB;Object.defineProperty(window,'indexedDB',{get(){return {open(){return {};},};},configurable:true});})();"
NO_LS="(()=>{const S=Storage.prototype;S.setItem=function(){throw new DOMException('QuotaExceededError');};S.getItem=function(){return null;};})();"
def quick(pg,pts,n):
    pg.click('#steps button[data-n="4"]'); pg.fill('#f_q_pts',str(pts)); pg.press('#f_q_pts','Enter'); pg.wait_for_function(f"dbList().length==={n}&&!ui.busy",timeout=6000)
def lskeys(pg): return pg.evaluate("(()=>{const o=[];for(let i=0;i<localStorage.length;i++)o.push(localStorage.key(i));return o.sort();})()")
with sync_playwright() as p:
    b=launch(p); t=T(); errs=[]
    # ---------- 1. IndexedDB niedostępne → zapis awaryjny w localStorage → powrót do IndexedDB ----------
    ctx=b.new_context(viewport={'width':1100,'height':900}); ctx.add_init_script(NO_IDB)
    pg=open_page(ctx,errs=errs)
    t.chk('bez IndexedDB aplikacja startuje w trybie zapasowym (localStorage)', pg.evaluate("DB.kind")=='ls')
    quick(pg,100,1); quick(pg,50,2)
    pg.click('button[data-act="automode"]') if pg.locator('button[data-act="automode"]').count() else None
    pg.click('#steps button[data-n="1"]'); pg.evaluate("()=>{if(!cfg.auto){cfg.auto=true;cfgSave();}}")
    pg.fill('#i_sh_age','9'); pg.click('button.plan-btn[data-p="o5"][data-w="I"]'); pg.click('#bar button.btn:not(.ghost)'); pg.click('#card-ST30 button[data-act="quadset"][data-q="1,2"]'); pg.click('#bar button.btn:not(.ghost)'); idle(pg)
    v=visits(pg); gen=[x for x in v if x['src']=='gen'][0]
    txt=pg.evaluate("async (id)=>bodyText(await dbBody(id))",gen['id'])
    pg.click('#steps button[data-n="6"]')
    t.chk('tryb zapasowy: 3 wpisy zapisane (w tym wizyta z opisem), widoczne ostrzeżenie', len(v)==3 and len(txt)>500 and 'pamięci zapasowej' in clean(pg.inner_text('#main')), len(v))
    pg.close(); pg=open_page(ctx,errs=errs)
    t.chk('tryb zapasowy: po ponownym uruchomieniu wpisy są na miejscu', len(visits(pg))==3 and pg.evaluate("DB.kind")=='ls')
    k_ls=[k for k in lskeys(pg) if k!='opisyNFZ.cfg']
    pg.close()
    ctx2=b.new_context(viewport={'width':1100,'height':900},storage_state=ctx.storage_state())     # ta sama pamięć localStorage, IndexedDB znów działa
    pg=open_page(ctx2,errs=errs); v2=visits(pg)
    t.chk('gdy IndexedDB wraca: wpisy z pamięci zapasowej przenoszą się do głównej bazy (3 wpisy, ten sam opis), pamięć zapasowa opróżniona',
          pg.evaluate("DB.kind")=='idb' and sorted(x['id'] for x in v2)==sorted(x['id'] for x in v) and pg.evaluate("async (id)=>bodyText(await dbBody(id))",gen['id'])==txt and len(k_ls)>0 and lskeys(pg)==['opisyNFZ.cfg'], (len(k_ls),lskeys(pg)))
    pg.close(); pg=open_page(ctx2,errs=errs)
    t.chk('…i nie dublują się przy kolejnym uruchomieniu', len(visits(pg))==3)
    # ---------- 2. IndexedDB „wisi” (nie odpowiada) → po 4 s tryb zapasowy ----------
    ctx3=b.new_context(); ctx3.add_init_script(HANG_IDB); pg3=ctx3.new_page(); pg3.goto(BASE)
    pg3.wait_for_function("typeof DB!=='undefined'&&DB.ready===true",timeout=9000)
    t.chk('nieodpowiadające IndexedDB nie blokuje aplikacji: po limicie czasu tryb zapasowy', pg3.evaluate("DB.kind")=='ls')
    # ---------- 3. żadna pamięć nie działa → praca tymczasowa z wyraźnym ostrzeżeniem ----------
    ctx4=b.new_context(viewport={'width':1100,'height':900}); ctx4.add_init_script(NO_IDB+NO_LS); e4=[]; pg4=open_page(ctx4,errs=e4)
    quick(pg4,100,1)
    warn=clean(pg4.inner_text('#main'))
    t.chk('zablokowana cała pamięć przeglądarki: aplikacja działa, wpis jest w pamięci karty, czerwone ostrzeżenie o braku trwałego zapisu', pg4.evaluate("DB.kind")=='mem' and len(visits(pg4))==1 and 'nie da się zapisywać danych na stałe' in warn and not e4, e4)
    pg4.click('#steps button[data-n="5"]'); t.chk('…statystyki działają także wtedy', '184,00' in clean(pg4.inner_text('.hero')))
    # ---------- 4. błąd zapisu w trakcie pracy (np. brak miejsca) ----------
    ctx5=b.new_context(viewport={'width':1100,'height':900}); pg5=open_page(ctx5,errs=errs)
    pg5.evaluate("()=>{cfg.auto=true;cfgSave();window.__real=DB.be.write.bind(DB.be);DB.be.write=()=>Promise.reject(new Error('QuotaExceededError'));}")
    pg5.fill('#i_sh_age','9'); pg5.click('button.plan-btn[data-p="o5"][data-w="I"]'); pg5.click('#bar button.btn:not(.ghost)'); pg5.click('#card-ST30 button[data-act="quadset"][data-q="1,2"]'); pg5.click('#bar button.btn:not(.ghost)')
    pg5.wait_for_function("state.saveInfo&&state.saveInfo.ok===false&&!state.pendSig"); st=clean(pg5.inner_text('#save-st'))
    t.chk('błąd zapisu: czytelny komunikat z przyciskiem „Spróbuj ponownie”, formularz i opis zostają', 'Nie udało się zapisać' in st and pg5.locator('#save-st button[data-act="saveforce"]').count()==1 and len(visits(pg5))==0 and pg5.evaluate("state.codes.length")==4, st)
    pg5.click('#resetBtn'); pg5.wait_for_timeout(150)
    t.chk('niezapisana wizyta: „Następny pacjent” wymaga potwierdzenia (drugiego kliknięcia)', pg5.evaluate("state.codes.length")==4 and 'kliknij ponownie' in pg5.inner_text('#resetBtn').lower(), pg5.inner_text('#resetBtn'))
    pg5.evaluate("()=>{DB.be.write=window.__real;}"); pg5.click('#save-st button[data-act="saveforce"]'); idle(pg5)
    v=visits(pg5); t.chk('po ustąpieniu błędu „Spróbuj ponownie” zapisuje wizytę – jeden wpis, bez dubla', len(v)==1 and 'Zapisano' in clean(pg5.inner_text('#save-st')), len(v))
    # szybki wpis przy błędzie zapisu
    pg5.click('#steps button[data-n="4"]'); pg5.evaluate("()=>{DB.be.write=()=>Promise.reject(new Error('QuotaExceededError'));}")
    pg5.fill('#f_q_pts','77'); pg5.press('#f_q_pts','Enter'); pg5.wait_for_function("!ui.busy"); pg5.wait_for_timeout(150)
    t.chk('szybki wpis przy błędzie zapisu: komunikat, wpisane wartości zostają w formularzu', len(visits(pg5))==1 and pg5.input_value('#f_q_pts')=='77' and 'Nie zapisano: błąd zapisu' in clean(pg5.inner_text('#quick-card')), clean(pg5.inner_text('#quick-card'))[-160:])
    pg5.evaluate("()=>{DB.be.write=window.__real;}"); pg5.press('#f_q_pts','Enter'); pg5.wait_for_function("dbList().length===2&&!ui.busy")
    t.chk('…a ponowny Enter zapisuje go raz', len(visits(pg5))==2)
    # ---------- 5. dwie karty tej samej przeglądarki ----------
    ctx6=b.new_context(viewport={'width':1100,'height':900}); A=open_page(ctx6,errs=errs); B=open_page(ctx6,errs=errs)
    quick(A,100,1)
    B.click('#steps button[data-n="4"]'); B.evaluate("()=>document.dispatchEvent(new Event('visibilitychange'))"); B.wait_for_function("dbList().length===1")
    t.chk('wpis zapisany w karcie A pojawia się w karcie B po powrocie do niej', B.locator('section.card.hist').count()==1)
    B.fill('#f_q_pts','60'); B.press('#f_q_pts','Enter'); B.wait_for_function("dbList().length===2&&!ui.busy")
    A.evaluate("()=>document.dispatchEvent(new Event('visibilitychange'))"); A.wait_for_function("dbList().length===2")
    nos=sorted(x['no'] for x in visits(A))
    t.chk('wpisy z dwóch kart dostają różne numery (#1, #2)', nos==[1,2], nos)
    A.click('#steps button[data-n="6"]'); A.fill('#i_cfg_price','1,95'); A.press('#i_cfg_price','Tab'); A.wait_for_timeout(250)
    t.chk('zmiana stawki w karcie A dociera do karty B (karty nie nadpisują sobie ustawień)', B.evaluate("cfg.price")==1.95, B.evaluate("cfg.price"))
    B.fill('#f_q_pts','10'); B.press('#f_q_pts','Enter'); B.wait_for_function("dbList().length===3&&!ui.busy")
    t.chk('wpis z karty B liczony już po nowej stawce 1,95; ustawienie w pamięci przeglądarki nadal 1,95', visits(B)[0]['price']==1.95 and B.evaluate("LS.get('cfg',{}).price")==1.95)
    # dwie karty, ta sama wizyta zapisana wcześniej: brak zderzenia identyfikatorów
    ids=[x['id'] for x in visits(B)]; t.chk('identyfikatory wpisów unikalne', len(set(ids))==len(ids))
    t.chk('brak błędów JS', not errs, errs)
    t.done('T8 magazyn danych i awarie'); b.close()
