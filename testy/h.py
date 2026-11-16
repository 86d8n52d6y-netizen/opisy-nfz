# wspólne narzędzia testów
from playwright.sync_api import sync_playwright
import json, re, os, sys
BASE=os.environ.get('OPISY_URL','http://127.0.0.1:8765/nfz.html')
HOME=os.environ.get('OPISY_HOME',BASE.rsplit('/',1)[0]+'/index.html')
KAL=BASE.rsplit('/',1)[0]+'/kalendarz.html'
PRYW=BASE.rsplit('/',1)[0]+'/prywatne.html'
_LOGGED=set()
def login(ctx,name='Test',pwd='haslo-test-1',migrate=True):
    # użytkownik testowy w danym kontekście przeglądarki: przy pierwszym – konto + przeniesienie starych danych (jak ekran zakładania konta)
    pg=ctx.new_page(); pg.goto(HOME); pg.wait_for_function("window.G&&typeof G.createUser==='function'")
    uid=pg.evaluate("""async ([n,p,mig])=>{const u=G.users().find(x=>x.name===n);
      if(u){await G.login(u.id,p);return u.id;}
      const r=await G.createUser(n,p);G.user=r.user;G.key=(await G.session()).key;if(mig&&G.users().length===1)await G.legacy.migrate();return r.user.id;}""",[name,pwd,migrate])
    pg.close(); _LOGGED.add(id(ctx)); return uid
V9=os.environ.get('OPISY_V9_URL','http://127.0.0.1:8765/testy/.v9/index.html')
SHOTS=os.path.join(os.path.dirname(os.path.abspath(__file__)),'zrzuty')
CHROME='/usr/bin/google-chrome'
class T:
    def __init__(self): self.ok=0; self.bad=[]
    def chk(self,name,cond,extra=''):
        if cond: self.ok+=1; print('OK   '+name+((' | '+str(extra)) if extra!='' else ''))
        else: self.bad.append(name); print('BŁĄD '+name+((' | '+str(extra)) if extra!='' else ''))
    def done(self,title):
        print(f'--- {title}: {self.ok} OK, {len(self.bad)} błędów'+(': '+'; '.join(self.bad) if self.bad else ''))
        sys.stdout.flush()
        if self.bad: sys.exit(1)
def clean(s): return (s or '').replace('\xa0',' ').replace(' ',' ')
def launch(p): return p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
def open_page(ctx,url=None,errs=None,wait=True):
    if id(ctx) not in _LOGGED: login(ctx)
    pg=ctx.new_page()
    if errs is not None:
        pg.on('pageerror',lambda e: errs.append('pageerror: '+str(e)))
        pg.on('console',lambda m: errs.append('console.error: '+m.text) if (m.type=='error' and '404' not in m.text and 'ERR_' not in m.text) else None)
    pg.goto(url or BASE)
    if wait: pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true",timeout=10000)
    return pg
def idle(pg):  # poczekaj na zakończenie zapisów w tle
    pg.wait_for_function("!state.pendSig&&!ui.busy",timeout=5000); pg.wait_for_timeout(60)
def visits(pg):  # zapisane wpisy (od najnowszego) wraz z kwotami w groszach
    return pg.evaluate("dbList().map(m=>Object.assign({},m,{k:calc(m),visit:isVisit(m)}))")
SEED_JS = """async (rows)=>{ // rows: [date, ini, pts, revH, exCents, exDesc, min, src]
  let n=0; for(const r of rows){ const now=new Date().toISOString();
    const m=normMeta({id:newId(),no:nextNo(),ini:r[1]||'',date:r[0],created:now,at:now,src:r[7]||'man',codes:r[7]==='gen'?['ST33','ST30']:[],pts:r[2]||0,price:cfg.price,pct:cfg.pct,revH:r[3]||0,revRate:cfg.rev,ex:r[4]?[{c:r[4],d:r[5]||''}]:[],min:r[6]==null?null:r[6],miss:0,body:false});
    await dbPut(m); n++; } return n; }"""
