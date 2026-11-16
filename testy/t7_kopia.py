# T7 – kopia zapasowa: pobranie pliku .json, odtworzenie po utracie danych, scalanie, nowe urządzenie, błędne pliki
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
import json, tempfile, datetime
TMP=tempfile.mkdtemp()
def gen(pg,age,ini=None):
    if ini: pg.fill('#i_sv_ini',ini)
    pg.fill('#i_sh_age',str(age)); pg.click('button.plan-btn[data-p="o5"][data-w="I"]'); pg.click('#bar button.btn:not(.ghost)')
    pg.click('#card-ST30 button[data-act="quadset"][data-q="1,2"]'); pg.click('#card-1101 .tooth[data-t="11"]'); pg.click('#bar button.btn:not(.ghost)'); idle(pg)
def snap(pg): return pg.evaluate("async ()=>{const o=[];for(const m of dbList()){const b=m.body?await dbBody(m.id):null;o.push(Object.assign({},m,{txt:b?bodyText(b):null,snapCodes:b&&b.snap?b.snap.codes:null}));}return o.sort((a,b)=>a.id<b.id?-1:1);}")
def export(pg,name):
    pg.click('#steps button[data-n="6"]')
    with pg.expect_download() as d: pg.click('button[data-act="bkexport"]')
    path=os.path.join(TMP,name); d.value.save_as(path); pg.wait_for_function("!ui.busy"); return path,d.value.suggested_filename
def imp(pg,path):
    pg.click('#steps button[data-n="6"]'); pg.set_input_files('#bk-file',path)
    pg.wait_for_function("ui.msg&&ui.msg.length>0&&!ui.busy",timeout=8000); pg.wait_for_timeout(150); return clean(pg.evaluate("ui.msg"))
with sync_playwright() as p:
    b=launch(p); t=T(); errs=[]
    ctx=b.new_context(viewport={'width':1100,'height':900},accept_downloads=True); pg=open_page(ctx,errs=errs)
    # ---------- dane: 2 wizyty z opisem (JK z przeglądami i kwotą, anonimowa) + 2 szybkie wpisy; własne ustawienia ----------
    gen(pg,9,'jk'); pg.fill('#i_sv_revH','1,5'); pg.press('#i_sv_revH','Tab'); pg.click('button[data-act="xadd"][data-s="v"]'); pg.fill('[data-x="v|0|a"]','150'); pg.fill('[data-x="v|0|d"]','dodatkowa procedura'); pg.press('[data-x="v|0|d"]','Tab'); idle(pg)
    pg.click('#resetBtn'); pg.click('button[data-act="automode"]'); gen(pg,12); pg.click('#resetBtn')
    pg.click('#steps button[data-n="4"]'); pg.fill('#f_q_pts','150'); pg.press('#f_q_pts','Enter'); pg.wait_for_function("dbList().length===3&&!ui.busy")
    pg.fill('#f_q_revH','2'); pg.click('button[data-act="qsave"]'); pg.wait_for_function("dbList().length===4&&!ui.busy")
    pg.click('#steps button[data-n="6"]'); pg.fill('#i_cfg_price','1,9'); pg.press('#i_cfg_price','Tab'); pg.fill('#i_cfg_rev','400'); pg.press('#i_cfg_rev','Tab'); pg.click('button[data-act="pct"][data-v="35"]'); pg.click('button[data-act="basis"][data-v="share"]')
    S0=snap(pg)
    t.chk('przed kopią: aplikacja przypomina o braku kopii', 'nie ma jeszcze kopii zapasowej' in clean(pg.inner_text('#main')).lower() or 'kopi' in clean(pg.inner_text('.bknote')).lower() if pg.locator('.bknote').count() else True, '')
    path1,fname=export(pg,'kopia1.json'); data=json.load(open(path1,encoding='utf-8'))
    t.chk('pobrany plik: nazwa z datą, format aplikacji, 4 wpisy, 2 opisy, ustawienia', fname=='opisy-nfz-kopia-'+datetime.date.today().isoformat()+'.json' and data['app']=='opisy-nfz' and len(data['visits'])==4 and len(data['bodies'])==2 and data['cfg']=={'price':1.9,'pct':35,'rev':400,'basis':'share','auto':True} and len(data['segs'])>0, (fname,len(data['visits']),len(data['bodies']),data['cfg']))
    jk=[x for x in data['visits'] if x['ini']=='JK'][0]
    t.chk('plik jest czytelny także dla człowieka: dzień tygodnia i kwoty w zł przy każdym wpisie', jk['dzien'] in ('poniedziałek','wtorek','środa','czwartek','piątek','sobota','niedziela') and jk['pts']==259.8 and jk['zl_punkty']==478.03 and jk['zl_lekarz']==191.21 and jk['zl_przeglady']==525 and jk['zl_dodatkowe']==150, {k:jk[k] for k in ('dzien','zl_punkty','zl_lekarz','zl_przeglady','zl_dodatkowe')})
    t.chk('po wykonaniu kopii zapisana jest jej data', pg.evaluate("!!cfg.lastBackup") and 'jeszcze nie wykonano' not in pg.inner_text('#main'))
    # ---------- utrata danych → odtworzenie ----------
    pg.click('#steps button[data-n="4"]'); c=pg.locator('button[data-act="hclear"]'); c.click(); c.click(); pg.wait_for_function("dbList().length===0&&!ui.busy")
    t.chk('„usuń wszystkie” (2 kliknięcia): historia pusta', len(visits(pg))==0)
    msg=imp(pg,path1); S1=snap(pg)
    t.chk('wczytanie kopii odtwarza wszystko: 4 wpisy, te same pola, identyczne teksty opisów', 'dodano 4, zaktualizowano 0, bez zmian 0' in msg and S1==S0, msg)
    msg=imp(pg,path1)
    t.chk('ponowne wczytanie tego samego pliku: 0 dubli', 'dodano 0, zaktualizowano 0, bez zmian 4' in msg and snap(pg)==S0, msg)
    # ---------- scalanie: lokalna, nowsza poprawka wygrywa ze starszą kopią ----------
    q=[x for x in S0 if x['pts']==150][0]
    pg.click('#steps button[data-n="4"]'); pg.click(f'#hist-{q["id"]} button[data-act="eopen"]'); pg.fill('#f_e_pts','175'); pg.click('button[data-act="esave"]'); pg.wait_for_function("!ui.edit&&!ui.busy")
    msg=imp(pg,path1)
    t.chk('starsza kopia nie cofa nowszej poprawki wpisu (175 pkt zostaje)', 'bez zmian 4' in msg and [x for x in snap(pg) if x['id']==q['id']][0]['pts']==175, msg)
    path2,_=export(pg,'kopia2.json')
    # ---------- nowe urządzenie: pusta przeglądarka ----------
    ctxB=b.new_context(viewport={'width':1100,'height':900},accept_downloads=True); pB=open_page(ctxB,errs=errs)
    t.chk('nowe urządzenie przed wczytaniem: ustawienia domyślne (1,84 / 350 / 40%)', pB.evaluate("[cfg.price,cfg.rev,cfg.pct,cfg.auto,cfg.basis]")==[1.84,350,40,False,'full'])
    msg=imp(pB,path1)
    t.chk('nowe urządzenie: 4 wpisy i ustawienia z kopii (1,90 zł/pkt, 400 zł/h, 35%, tryb automatyczny)', 'dodano 4' in msg and 'Przywrócono też ustawienia' in msg and pB.evaluate("[cfg.price,cfg.rev,cfg.pct,cfg.auto,cfg.basis]")==[1.9,400,35,True,'share'] and snap(pB)==S0, msg)
    pB.evaluate("()=>{cfg.price=1.84;cfgSave();}")
    msg=imp(pB,path2)
    t.chk('nowsza kopia aktualizuje tylko zmieniony wpis (175 pkt); ustawienia na niepustej historii zostają', 'dodano 0, zaktualizowano 1, bez zmian 3' in msg and 'Przywrócono' not in msg and pB.evaluate("cfg.price")==1.84 and [x for x in snap(pB) if x['id']==q['id']][0]['pts']==175, msg)
    pB.click('#steps button[data-n="4"]'); jid=[x for x in S0 if x['ini']=='JK'][0]['id']
    pB.click(f'#hist-{jid} button[data-act="hopen"]'); pB.wait_for_function("state.step===3"); idle(pB)
    t.chk('na nowym urządzeniu wpis z kopii otwiera się w generatorze i daje ten sam opis', pB.evaluate("buildOut().map(o=>plain(o.text)).join('\\n\\n')")==[x for x in S0 if x['ini']=='JK'][0]['txt'] and len(visits(pB))==4)
    # ---------- zderzenie numerów: urządzenie z własnymi wpisami #1, #2 ----------
    ctxC=b.new_context(viewport={'width':1100,'height':900}); pC=open_page(ctxC,errs=errs)
    pC.click('#steps button[data-n="4"]')
    for i,pts in enumerate(('10','20')): pC.fill('#f_q_pts',pts); pC.press('#f_q_pts','Enter'); pC.wait_for_function(f"dbList().length==={i+1}&&!ui.busy")
    own=snap(pC); msg=imp(pC,path1); v=visits(pC)
    t.chk('wczytanie kopii obok własnych wpisów: 6 wpisów, własne nietknięte, numery bez powtórzeń', 'dodano 4' in msg and len(v)==6 and len({x['no'] for x in v})==6 and all(any(x['id']==o['id'] and x['pts']==o['pts'] and x['at']==o['at'] for x in v) for o in own) and 'Przywrócono' not in msg, sorted(x['no'] for x in v))
    # ---------- błędne pliki ----------
    def mk(name,content):
        pth=os.path.join(TMP,name); open(pth,'w',encoding='utf-8').write(content); return pth
    before=snap(pC)
    m1=imp(pC,mk('zly1.json','to nie jest json {{{')); m2=imp(pC,mk('zly2.json',json.dumps({'cos':'innego','visits':[1,2]}))); m3=imp(pC,mk('zly3.json',json.dumps([1,2,3])))
    t.chk('plik uszkodzony / obcy: komunikat „Nie wczytano”, dane bez zmian', all('Nie wczytano' in m for m in (m1,m2,m3)) and snap(pC)==before, (m1,m2))
    d3=json.loads(json.dumps(data)); d3['visits']=[dict(d3['visits'][0],id='vzzz1',date='2026-02-31'),dict(d3['visits'][0],id='<script>',date='2026-02-01'),{'id':'vok12345','date':'2026-03-03','pts':'12,5x','ini':'ok'},{'id':'vok12346','date':'2026-03-04','pts':50,'price':-5,'pct':500,'revH':99,'min':-3,'ex':[{'c':'abc'},{'c':1000,'d':'ok'}],'ini':'<b>x</b>','codes':['ST33','<img>',5]},None,7]
    m4=imp(pC,mk('zly4.json',json.dumps(d3))); v=visits(pC); ok=[x for x in v if x['id']=='vok12346']
    t.chk('plik z częściowo błędnymi wpisami: błędne pominięte (zła data, zły identyfikator, śmieci), reszta wczytana i oczyszczona',
          'pominięto błędnych 4' in m4 and len(ok)==1 and ok[0]['price']==pC.evaluate("cfg.price") and ok[0]['pct']==pC.evaluate("cfg.pct") and ok[0]['revH']==0 and ok[0]['min'] is None and ok[0]['ex']==[{'c':1000,'d':'ok'}] and ok[0]['codes']==['ST33'] and '<' not in ok[0]['ini'], (m4, ok and {k:ok[0][k] for k in ('ini','price','pct','revH','min','ex','codes')}))
    okb=[x for x in v if x['id']=='vok12345']
    t.chk('wpis z nieliczbowymi punktami wczytany jako 0 pkt (bez wywracania sum)', len(okb)==1 and okb[0]['pts']==0 and isinstance(pC.evaluate("agg(dbList()).total"),int))
    # ---------- opisy do .txt (funkcja z poprzedniej wersji) ----------
    pg.click('#steps button[data-n="4"]')
    with pg.expect_download() as d: pg.click('button[data-act="hexport"]')
    pt=os.path.join(TMP,'opisy.txt'); d.value.save_as(pt); txt=open(pt,encoding='utf-8-sig').read()
    t.chk('„Opisy do pliku .txt” nadal działa: 2 opisy z nagłówkami', d.value.suggested_filename.endswith('.txt') and txt.count('===')>=4 and 'JK' in txt and 'Anonim #' in txt, txt[:120])
    t.chk('brak błędów JS', not errs, errs)
    t.done('T7 kopia zapasowa'); b.close()
