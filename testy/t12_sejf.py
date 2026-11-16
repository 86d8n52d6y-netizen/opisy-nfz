# T12 – aplikacja Gabinet: konto i hasło, kod odzyskiwania, blokada, szyfrowanie na dysku, izolacja użytkowników,
#       pasek modułów i szkic wizyty, gabinet z grafiku, okno Zarobki, przeniesienie danych z poprzednich wersji
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
import datetime, json, re
TODAY=datetime.date.today().isoformat()
RAW="""async ([db,store])=>{const r=indexedDB.open(db);const d=await new Promise((a,b)=>{r.onsuccess=()=>a(r.result);r.onerror=()=>b(r.error);});
  const t=d.transaction(store,'readonly'),o=t.objectStore(store);const ks=await new Promise(a=>{const q=o.getAllKeys();q.onsuccess=()=>a(q.result);});
  const vs=await new Promise(a=>{const q=o.getAll();q.onsuccess=()=>a(q.result);});d.close();return ks.map((k,i)=>[k,vs[i]]);}"""
def wait_home(pg): pg.wait_for_function("window.G&&document.querySelector('#app')&&document.querySelector('#app').children.length>0",timeout=15000)
def create_ui(pg,name,pwd):
    pg.fill('#nm',name); pg.fill('#p1',pwd); pg.fill('#p2',pwd); pg.click('#f-setup button[type=submit]')
    pg.wait_for_selector('#code',timeout=20000); code=pg.inner_text('#code').strip()
    return code
def fresh(pg):   # pusty formularz: krok 3 → „Nowy/Następny pacjent” (niezapisaną wizytę trzeba potwierdzić drugim kliknięciem)
    if not pg.evaluate("state.codes.length"): return
    if pg.evaluate("state.step")!=3: pg.click('#steps button[data-n="3"]'); pg.wait_for_timeout(150)
    for _ in range(2):
        if pg.evaluate("state.codes.length"): pg.click('#resetBtn'); pg.wait_for_timeout(150)
def visit_ui(pg,ini):
    pg.fill('#i_sv_ini',ini); pg.fill('#i_sh_age','9'); pg.click('button.plan-btn[data-p="o5"][data-w="I"]'); pg.click('#bar button.btn:not(.ghost)')
    pg.click('#card-ST30 button[data-act="quadset"][data-q="1,2"]'); pg.click('#bar button.btn:not(.ghost)'); idle(pg)
with sync_playwright() as p:
    b=launch(p); t=T(); errs=[]
    ctx=b.new_context(viewport={'width':1200,'height':900})
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e))); pg.goto(HOME); wait_home(pg)
    t.chk('pierwsze uruchomienie: ekran zakładania konta', pg.locator('#f-setup').count()==1 and 'Załóż konto' in pg.inner_text('#app'))
    pg.fill('#nm','Patryk'); pg.fill('#p1','tajne-haslo-1'); pg.fill('#p2','inne-haslo'); pg.click('#f-setup button[type=submit]')
    t.chk('różne hasła → komunikat, konto nie powstaje', 'Hasła różnią się' in pg.inner_text('#app') and pg.evaluate("G.users().length")==0)
    pg.fill('#nm','Patryk'); pg.fill('#p1','12345'); pg.fill('#p2','12345'); pg.evaluate("document.getElementById('p1').removeAttribute('minlength');document.getElementById('p2').removeAttribute('minlength')"); pg.click('#f-setup button[type=submit]')
    pg.wait_for_function("document.querySelector('.g-err')"); t.chk('za krótkie hasło (5 znaków) → komunikat', 'co najmniej 6 znaków' in pg.inner_text('#app') and pg.evaluate("G.users().length")==0)
    code=create_ui(pg,'Patryk','tajne-haslo-1')
    t.chk('po utworzeniu konta: kod odzyskiwania 6×4 znaki, „Dalej” nieaktywne do potwierdzenia zapisu', re.fullmatch(r'([0-9A-Z]{4}-){5}[0-9A-Z]{4}',code) is not None and pg.is_disabled('#dalej'), code)
    pg.check('#ok'); pg.click('#dalej'); pg.wait_for_selector('.g-tiles',timeout=15000)
    uid=pg.evaluate("G.user.id"); tiles=[x.strip() for x in pg.locator('.g-tile b').all_inner_texts()]
    t.chk('strona główna: 3 kafelki (Kalendarz, Opisy NFZ, Opisy prywatne) i pasek modułów', tiles==['Kalendarz','Opisy NFZ','Opisy prywatne'] and pg.locator('#gbar .gbar-nav a').count()==3, tiles)
    u=pg.evaluate("G.users()[0]"); t.chk('lista użytkowników przechowuje tylko zaszyfrowane klucze (bez hasła i klucza jawnego)', 'tajne' not in json.dumps(u) and set(u)>= {'pwd','rec','kdf'} and u['kdf']['iter']>=600000, list(u))
    # ---------- moduły i pasek ----------
    pg.click('.g-tile[href="nfz.html"]'); pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true",timeout=15000)
    t.chk('kafelek „Opisy NFZ” otwiera moduł bez ponownego hasła; pasek: aktywny moduł', pg.url.endswith('nfz.html') and pg.inner_text('#gbar .gbar-nav a.on')=='Opisy NFZ')
    visit_ui(pg,'jk')
    raw=pg.evaluate(RAW,['opisyNFZ@'+uid,'visits']); rawb=pg.evaluate(RAW,['opisyNFZ@'+uid,'bodies'])
    t.chk('wizyta zapisana zaszyfrowana: w bazie tylko szyfrogram (bez inicjałów, kodów i treści opisu)', len(raw)==1 and all(isinstance(v,str) and re.fullmatch(r'v1:[A-Za-z0-9+/=]+:[A-Za-z0-9+/=]+',v) for _,v in raw+rawb) and len(rawb)==1, [v[:30] for _,v in raw])
    # szkic: wizyta w toku, przejście do Kalendarza i z powrotem
    fresh(pg)
    pg.fill('#i_sh_age','12'); pg.click('button.plan-btn[data-p="o5"][data-w="II"]'); pg.click('#bar button.btn:not(.ghost)'); pg.wait_for_timeout(600)
    codes0=pg.evaluate("state.codes.join(',')")
    pg.click('#gbar a[data-gmod="kalendarz"]'); pg.wait_for_url('**/kalendarz.html',timeout=15000); pg.wait_for_function("window.Kal&&Kal.UI.loaded===true",timeout=15000)
    t.chk('przejście do Kalendarza z paska: moduł działa, aktywny „Kalendarz”', pg.inner_text('#gbar .gbar-nav a.on')=='Kalendarz' and pg.locator('#tabs [data-a="tab"]').count()==6)
    pg.click('#gbar a[data-gmod="nfz"]'); pg.wait_for_url('**/nfz.html'); pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true"); pg.wait_for_timeout(300)
    t.chk('powrót do Opisów NFZ: niezapisana wizyta odtworzona (kody, krok 2, wiek)', pg.evaluate("state.codes.join(',')")==codes0 and pg.evaluate("state.step")==2 and pg.evaluate("state.a['sh.age']")=='12', (codes0,pg.evaluate("[state.codes.join(','),state.step]")))
    # ---------- gabinet z grafiku ----------
    pg.goto(KAL); pg.wait_for_function("window.Kal&&Kal.UI.loaded===true",timeout=15000)
    pg.evaluate("(d)=>{const K=Kal,s=K.S();s.clinics[0].name='Gabinet Testowy';s.clinics[0].active=true;K.saveSettings();K.M(d.slice(0,7),true).shifts.push({id:K.uid(),date:d,clinicId:s.clinics[0].id,start:'00:00',end:'23:59',status:'planned'});K.saveMonth(d.slice(0,7));}",TODAY)
    pg.wait_for_function("Kal.Store.sync==='saved'",timeout=8000)
    kraw=pg.evaluate(RAW,['gabinet@'+uid,'kv']); kv=dict(kraw)
    t.chk('Kalendarz zapisany zaszyfrowany (bez nazwy gabinetu w bazie)', 'grafik' in kv and re.fullmatch(r'v1:[A-Za-z0-9+/=]+:[A-Za-z0-9+/=]+',kv['grafik']) is not None)
    pg.reload(); pg.wait_for_function("window.Kal&&Kal.UI.loaded===true",timeout=15000)
    t.chk('po ponownym otwarciu Kalendarz ma te same dane', pg.evaluate("Kal.S().clinics[0].name")=='Gabinet Testowy')
    pg.goto(BASE); pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true"); fresh(pg)
    visit_ui(pg,'ab'); sel=pg.inner_text('#i_sv_gab option:checked') if pg.locator('#i_sv_gab').count() else ''
    v=[x for x in visits(pg) if x['ini']=='AB'][0]
    t.chk('Opisy NFZ: gabinet wizyty domyślnie z dyżuru w Kalendarzu', v['gab']==pg.evaluate("state.clinics[0].id") and 'Gabinet Testowy' in sel, (v['gab'],sel))
    pg.select_option('#i_sv_gab','-'); idle(pg)
    t.chk('…i można go zmienić (bez gabinetu)', [x for x in visits(pg) if x['ini']=='AB'][0]['gab']=='')
    pg.select_option('#i_sv_gab',pg.evaluate("state.clinics[0].id")); idle(pg)
    # ---------- okno Zarobki ----------
    vs={x['ini']:x['k'] for x in visits(pg)}; pg.wait_for_timeout(900); pg.goto(HOME); pg.wait_for_selector('#zarobki')
    rows={clean(r.inner_text().split('\t')[0]).strip():clean(r.inner_text()) for r in pg.locator('#zarobki tbody tr').all()}
    zl=lambda c: f"{c//100:,}".replace(',',' ')+','+f"{c%100:02d}"
    gt=[v for k,v in rows.items() if 'Gabinet Testowy' in k]; bg=rows.get('Bez gabinetu','')
    t.chk('okno Zarobki: wizyta AB w wierszu „Gabinet Testowy”, JK w „Bez gabinetu” (kwoty jak w Opisach NFZ)', len(gt)==1 and zl(vs['AB']['total']) in gt[0] and zl(vs['JK']['total']) in bg, (rows,vs['AB']['total'],vs['JK']['total']))
    # ---------- blokada ----------
    pg.goto(BASE); pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true")
    fresh(pg)
    pg.fill('#i_sh_age','30'); pg.click('button.plan-btn[data-p="o5"][data-w="I"]'); pg.wait_for_timeout(500)
    pg.click('#gbar .gbar-ubtn'); pg.click('#gbar [data-g="lock"]'); pg.wait_for_url('**/index.html?wroc=nfz&p=blokada',timeout=10000); wait_home(pg)
    t.chk('„Zablokuj”: ekran logowania z informacją o blokadzie', 'zablokowana' in pg.inner_text('#app') and pg.locator('#f-login').count()==1)
    pg.goto(BASE); pg.wait_for_url('**/index.html?wroc=nfz**',timeout=10000)
    t.chk('po blokadzie moduł bez logowania nie otwiera danych (przekierowanie do logowania)', 'index.html' in pg.url)
    wait_home(pg); pg.fill('#pw','zle-haslo'); pg.click('#f-login button[type=submit]'); pg.wait_for_selector('.g-err',timeout=15000)
    t.chk('złe hasło → „Nieprawidłowe hasło”', 'Nieprawidłowe hasło' in pg.inner_text('#app'))
    pg.fill('#pw','tajne-haslo-1'); pg.click('#f-login button[type=submit]'); pg.wait_for_url('**/nfz.html',timeout=15000); pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true"); pg.wait_for_timeout(300)
    t.chk('po zalogowaniu powrót do Opisów NFZ z tą samą niezapisaną wizytą', pg.evaluate("state.a['sh.age']")=='30' and pg.evaluate("state.codes.length")==4)
    # bezczynność: zegar strony przesunięty o 16 min (limit domyślny 15 min)
    pg.clock.install(); pg.reload(); pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true"); pg.wait_for_timeout(300)
    pg.clock.fast_forward("05:00"); pg.wait_for_timeout(500)
    t.chk('5 min bezczynności – bez blokady', pg.url.endswith('nfz.html'))
    pg.clock.fast_forward("11:00"); pg.wait_for_url('**/index.html?wroc=nfz&p=blokada',timeout=15000)
    t.chk('16 min bezczynności (limit 15) → automatyczna blokada', 'p=blokada' in pg.url)
    pg.close(); pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    # ---------- drugi użytkownik ----------
    pg.goto(HOME); wait_home(pg); pg.click('[data-a="newuser"]'); create_ui(pg,'Anna','haslo-anny-2'); pg.check('#ok'); pg.click('#dalej'); pg.wait_for_selector('.g-tiles',timeout=15000)
    pg.goto(BASE); pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true")
    aid=pg.evaluate("G.user.id")
    t.chk('drugi użytkownik: własna, pusta przestrzeń (0 wizyt), inna baza', aid!=uid and len(visits(pg))==0 and pg.evaluate("DB.kind")=='idb')
    leak=pg.evaluate("""async ([raw])=>{const ok=[];for(const [k,v] of raw){try{await G.dec(v,'nfz:visits:'+k);ok.push(k);}catch(e){}}return ok.length;}""",[raw])
    t.chk('kluczem drugiego użytkownika nie da się odszyfrować danych pierwszego', leak==0)
    pg.goto(KAL); pg.wait_for_function("window.Kal&&Kal.UI.loaded===true",timeout=15000)
    t.chk('Kalendarz drugiego użytkownika nie ma gabinetów pierwszego', pg.evaluate("Kal.S().clinics.every(c=>c.name!=='Gabinet Testowy')"))
    # ---------- kod odzyskiwania, zmiana hasła, usunięcie konta ----------
    pg.goto(HOME); wait_home(pg); pg.click('#gbar .gbar-ubtn'); pg.click('#gbar [data-g="switch"]'); pg.wait_for_selector('#f-login',timeout=10000)
    pg.click(f'[data-u="{uid}"]'); pg.click('[data-a="forgot"]'); pg.click(f'[data-u="{uid}"]')
    pg.fill('#rc',code.lower().replace('-',' ')); pg.fill('#p1','nowe-haslo-3'); pg.fill('#p2','nowe-haslo-3'); pg.click('#f-rec button[type=submit]'); pg.wait_for_selector('.g-tiles',timeout=20000)
    t.chk('kod odzyskiwania (wpisany małymi literami, ze spacjami) ustawia nowe hasło i loguje', pg.evaluate("G.user.id")==uid)
    pg.goto(BASE); pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true")
    t.chk('…dane nienaruszone (2 wizyty)', sorted(x['ini'] for x in visits(pg))==['AB','JK'])
    old_ok=pg.evaluate("async (id)=>{try{await G.login(id,'tajne-haslo-1');return true;}catch(e){return false;}}",uid)
    t.chk('stare hasło przestało działać', old_ok is False)
    pg.goto(HOME+'#konto'); pg.wait_for_selector('#f-pw',state='attached'); pg.click('details:has(#f-pw) summary')
    pg.fill('#o1','nowe-haslo-3'); pg.fill('#n1','czwarte-haslo'); pg.fill('#n2','czwarte-haslo'); pg.click('#f-pw button[type=submit]'); pg.wait_for_selector('#pw-msg .g-ok',timeout=15000)
    ok4=pg.evaluate("async (id)=>{try{await G.login(id,'czwarte-haslo');return true;}catch(e){return false;}}",uid)
    t.chk('zmiana hasła w „Konto i bezpieczeństwo” działa', ok4 is True)
    pg.evaluate("async (id)=>{await G.login(id,'haslo-anny-2');}",aid)
    seen=None                                                            # karta z kontem Patryka sama się przełącza, gdy w przeglądarce zaloguje się ktoś inny
    for _ in range(40):
        pg.wait_for_timeout(500)
        try: seen=pg.evaluate("document.querySelector('.g-tiles h1, h1')?document.querySelector('#app h1').textContent:''")
        except Exception: continue
        if 'Anna' in (seen or ''): break
    t.chk('gdy w tej przeglądarce zaloguje się inny użytkownik, otwarta karta poprzedniego w ciągu kilku sekund przestaje pokazywać jego dane', 'Anna' in (seen or '') and 'Patryk' not in clean(pg.inner_text('#app')), seen)
    pg.goto(HOME+'#konto'); pg.wait_for_selector('#f-del',state='attached')
    pg.click('details:has(#f-del) summary'); pg.fill('#o3','haslo-anny-2'); pg.click('#f-del button[type=submit]'); pg.wait_for_selector('#f-login',timeout=15000)
    dbs=pg.evaluate("indexedDB.databases?indexedDB.databases().then(a=>a.map(x=>x.name)):[]")
    t.chk('usunięcie konta: znika użytkownik i jego bazy; drugi użytkownik zostaje', [x['name'] for x in pg.evaluate("G.users()")]==['Patryk'] and not any(aid in n for n in dbs) and any(uid in n for n in dbs), dbs)
    # ---------- przeniesienie danych z poprzednich wersji (jawnych) ----------
    c2=b.new_context(); p2=c2.new_page(); p2.on('pageerror',lambda e: errs.append(str(e)))
    p2.goto(HOME); wait_home(p2)
    p2.evaluate("""async (d)=>{const r=indexedDB.open('opisyNFZ',1);r.onupgradeneeded=()=>{['visits','bodies','segs'].forEach(s=>r.result.createObjectStore(s));};
      const db=await new Promise(a=>{r.onsuccess=()=>a(r.result);});const t=db.transaction(['visits','bodies'],'readwrite');
      t.objectStore('visits').put({id:'vstary1',v:2,no:1,ini:'ZZ',date:d,created:d+'T08:00:00.000Z',at:d+'T08:00:00.000Z',src:'man',codes:[],pts:100,price:1.84,pct:40,revH:0,revRate:350,ex:[],min:30,miss:0,body:false},'vstary1');
      await new Promise(a=>{t.oncomplete=a;});db.close();
      localStorage.setItem('opisyNFZ.cfg',JSON.stringify({v:2,price:1.84,pct:35,rev:350,basis:'full',auto:false,seq:1}));
      localStorage.setItem('grafik-gabinetow-v1',JSON.stringify({settings:{v:1,clinics:[{id:'c1',name:'Stary Gabinet',short:'SG',color:2,active:true}]},['m'+d.slice(0,7)]:{shifts:[{id:'s1',date:d,clinicId:'c1',start:'08:00',end:'14:00',status:'done',turnover:1000}],off:{},inv:{},costs:[]}}));}""",TODAY)
    p2.reload(); wait_home(p2); create_ui(p2,'Patryk','haslo-5555'); p2.check('#ok'); p2.click('#dalej')
    p2.wait_for_function("(document.querySelector('#app h2')||{}).textContent==='Dotychczasowe dane'",timeout=20000)
    mtxt=p2.inner_text('#app')
    t.chk('nowe urządzenie z danymi poprzednich wersji: po założeniu konta dane przeniesione i zaszyfrowane (lista)', 'Opisy NFZ: 1 wpis' in mtxt and 'Kalendarz: 1 dyżur, 1 gabinet' in mtxt, mtxt[:300])
    p2.click('#dalej'); p2.wait_for_selector('.g-tiles')
    left=p2.evaluate("(async()=>{const ks=[];for(let i=0;i<localStorage.length;i++)ks.push(localStorage.key(i));const dbs=indexedDB.databases?(await indexedDB.databases()).map(x=>x.name):[];return {ks:ks.sort(),dbs:dbs.sort()};})()")
    u2=p2.evaluate("G.user.id")
    t.chk('jawne kopie usunięte (stara baza i klucze), zostały tylko dane zaszyfrowane i ustawienia', 'opisyNFZ' not in left['dbs'] and 'grafik-gabinetow-v1' not in left['ks'] and 'opisyNFZ.cfg' not in left['ks'] and ('opisyNFZ@'+u2+'.cfg') in left['ks'], left)
    p2.goto(BASE); p2.wait_for_function("typeof DB!=='undefined'&&DB.ready===true")
    v2=visits(p2)
    t.chk('Opisy NFZ po przeniesieniu: stary wpis ZZ i ustawienie 35% na miejscu', len(v2)==1 and v2[0]['ini']=='ZZ' and p2.evaluate("cfg.pct")==35)
    p2.goto(KAL); p2.wait_for_function("window.Kal&&Kal.UI.loaded===true",timeout=15000)
    t.chk('Kalendarz po przeniesieniu: gabinet i dyżur na miejscu', p2.evaluate("Kal.S().clinics[0].name")=='Stary Gabinet' and p2.evaluate(f"Kal.M('{TODAY[:7]}').shifts.length")==1)
    t.chk('brak błędów JS', not errs, errs[:3])
    t.done('T12 konto, szyfrowanie, moduły'); b.close()
