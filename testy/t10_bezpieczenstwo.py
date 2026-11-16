# T10 – wrogie dane: plik kopii z kodem HTML/JS w inicjałach, opisach, kodach i zapisanych odpowiedziach; wpisy z klawiatury
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
import json, tempfile, datetime, re
TMP=tempfile.mkdtemp(); X='<img src=x onerror="window.__x=(window.__x||0)+1">'; XS='"><script>window.__x=99</script><b id="inj">'
TODAY=datetime.date.today().isoformat()
def injected(pg): return pg.evaluate("({x:window.__x||0,img:document.querySelectorAll('img[src=\"x\"]').length,inj:!!document.getElementById('inj'),scripts:document.querySelectorAll('#main script').length})")
with sync_playwright() as p:
    b=launch(p); ctx=b.new_context(viewport={'width':1100,'height':900},accept_downloads=True); errs=[]; pg=open_page(ctx,errs=errs); t=T()
    now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    # nazwy wszystkich pól formularza (wszystkie kody naraz, po jednym zębie i ćwiartce w każdej karcie) – każde dostanie wrogą wartość
    F=pg.evaluate("""()=>{resetVisit();state.a['sh.age']='9';state.codes=Object.keys(D);state.step=2;render();
      Object.keys(D).forEach(c=>{const t=document.querySelector('#card-'+c+' .tooth[data-act="tooth"]');if(t)t.click();const q=document.querySelector('#card-'+c+' [data-act="quad"]');if(q)q.click();});
      const u=a=>[...new Set(a)];
      const r={inp:u([...document.querySelectorAll('#main input[data-key],#main select[data-key]')].map(e=>e.dataset.key)),
        seg:u([...document.querySelectorAll('#main button[data-act="seg"]')].map(e=>e.dataset.key)),chk:u([...document.querySelectorAll('#main button[data-act="chk"]')].map(e=>e.dataset.key)),
        codes:state.codes.slice(),teeth:JSON.parse(JSON.stringify(state.teeth)),quads:JSON.parse(JSON.stringify(state.quads))};
      resetVisit();state.step=1;render();return r;}""")
    A={}; TE=json.loads(json.dumps(F['teeth']))
    def put(key,val):
        if key.startswith('T|'):
            _,c,tt,f=key.split('|'); TE.setdefault(c,{}).setdefault(tt,{'s':[],'f':{}})['f'][f]=val
        elif key.startswith('R|'):
            _,lk,i,f=key.split('|'); A.setdefault(lk,[{}])[0][f]=val
        else: A[key]=val
    for k in F['inp']+F['seg']: put(k,X if len(k)%2 else XS)
    for k in F['chk']: put(k,[X,XS])
    A['sh.age']='9'; A['__proto__x']='x'
    snap_hostile={'codes':F['codes']+[XS,'ST33',5,None],'a':dict(A,**{'sh.gi':{'a':1},'sh.ex':None,'constructor':'x','prototype':'y'}),
                  'teeth':dict(TE,**{'ZLY':{'11':{}},'1503':'tekst','ST01':dict(TE.get('ST01',{}),**{'9'+XS:{'s':[],'f':{}},'55':None,'11':{'s':['M',XS,'X'],'f':{}}})}),
                  'quads':dict(F['quads'],**{'ST30':[1,7,XS,1],'ST33':'x'}),'plan':{'p':XS,'w':'I'}}
    snap_types={'codes':['ST01'],'a':{'sh.age':'9','ST01.wer':'z pliku gabinetu'},'teeth':{'ST01':{'11':{'s':[],'f':{'an':'tekst zamiast listy','why':'tekst zamiast listy'}}}},'quads':{},'plan':None}
    data={'app':'opisy-nfz','schema':2,'exported':now,'cfg':{'price':'1.84"><b id=inj>','pct':XS,'rev':-1,'basis':X,'auto':'tak'},
      'visits':[
        {'id':'vzlosliwy1','no':1,'ini':X,'date':TODAY,'at':now,'created':now,'src':'gen','codes':['ST33',X,'ST01'],'pts':100,'price':1.84,'pct':40,'revH':1,'revRate':350,'ex':[{'c':1500,'d':X},{'c':2500,'d':XS}],'min':30,'miss':2,'body':True},
        {'id':'vzlosliwy2','no':'1','ini':XS,'date':TODAY,'at':now,'src':X,'codes':X,'pts':'1e400','price':'x','ex':'x','min':'<b>','body':'true'},
        {'id':'v"><img src=x onerror=1>','date':TODAY,'pts':5},
        {'id':'vzlosliwy3','date':TODAY+XS,'pts':5},
        {'id':'vzlosliwy4','no':7,'ini':'ZT','date':TODAY,'at':now,'created':now,'src':'gen','codes':['ST01'],'pts':93,'price':1.84,'pct':40,'body':True}],
      'bodies':{'vzlosliwy1':{'txt':'Opis '+X+'\n'+XS+' \u0003zzzz_zz\u0004 koniec','p':1,'snap':snap_hostile},'vzlosliwy2':{'txt':{'nie':'tekst'}},'vzlosliwy4':{'txt':'Opis ZT','p':0,'snap':snap_types},'__proto__':{'txt':'x'}},
      'segs':{'zzzz_zz':X,'__proto__':'x','constructor':X}}
    path=os.path.join(TMP,'zla.json'); json.dump(data,open(path,'w',encoding='utf-8'))
    pg.click('#steps button[data-n="6"]'); pg.set_input_files('#bk-file',path); pg.wait_for_function("ui.msg&&ui.msg.length>0&&!ui.busy")
    msg=clean(pg.evaluate("ui.msg")); v=visits(pg); by={x['id']:x for x in v}
    t.chk('wroga kopia: wczytane 3 wpisy o poprawnej budowie, 2 odrzucone (zły identyfikator, zła data)', len(v)==3 and set(by)=={'vzlosliwy1','vzlosliwy2','vzlosliwy4'} and 'pominięto błędnych 2' in msg, msg)
    a=by['vzlosliwy1']; c=by['vzlosliwy2']
    t.chk('inicjały i kody oczyszczone ze znaczników; liczby spoza zakresu zastąpione bezpiecznymi wartościami', '<' not in a['ini'] and '>' not in a['ini'] and len(a['ini'])<=10 and a['codes']==['ST33','ST01'] and c['codes']==[] and c['pts']==0 and c['price']==1.84 and c['ex']==[] and c['min'] is None and c['src']=='gen' and c['body'] is False, (a['ini'],c['ini'],c['pts'],c['price']))
    t.chk('ustawienia z wrogiej kopii: przyjęte tylko poprawne wartości (reszta bez zmian)', pg.evaluate("[cfg.price,cfg.pct,cfg.rev,cfg.basis,cfg.auto]")==[1.84,40,350,'full',False], pg.evaluate("[cfg.price,cfg.pct,cfg.rev,cfg.basis,cfg.auto]"))
    views=[]
    def look(name): r=injected(pg); views.append((name,r)); return r
    look('ustawienia')
    pg.click('#steps button[data-n="4"]'); pg.wait_for_selector('section.card.hist'); look('historia')
    card=pg.inner_text('#hist-vzlosliwy1')
    t.chk('Historia pokazuje wrogie teksty jako zwykły tekst (opis kwoty widoczny dosłownie)', '<img src=x onerror=' in card and 'onerror' in pg.inner_html('#hist-vzlosliwy1') and '&lt;img' in pg.inner_html('#hist-vzlosliwy1'))
    pg.click('#hist-vzlosliwy1 button[data-act="hshow"]'); pg.wait_for_function("document.getElementById('htxt-vzlosliwy1').textContent.length>5"); look('pokaż opis')
    t.chk('„Pokaż opis”: znaczniki w treści opisu są tekstem, brakujący fragment szablonu oznaczony', '<img src=x' in pg.inner_text('#htxt-vzlosliwy1') and 'BRAK FRAGMENTU SZABLONU' in pg.inner_text('#htxt-vzlosliwy1'))
    pg.click('#hist-vzlosliwy1 button[data-act="eopen"]'); look('edycja kwot')
    t.chk('formularz edycji: wrogi opis kwoty trafia do pola jako tekst', pg.input_value('[data-x="e|0|d"]')==X)
    pg.click('button[data-act="ecancel"]')
    pg.fill('#i_hs_q',XS); pg.wait_for_timeout(100); look('szukanie'); pg.fill('#i_hs_q','')
    pg.click('#steps button[data-n="5"]'); pg.click('button[data-act="range"][data-p="all"]')
    for tb in ('days','weeks','months','dow'): pg.click(f'button[data-act="tab"][data-t="{tb}"]'); look('statystyki '+tb)
    # wpis z odpowiedziami o błędnej budowie (tekst w miejscu listy) – nie może zawiesić strony
    pg.click('#steps button[data-n="4"]'); pg.click('#hist-vzlosliwy4 button[data-act="hopen"]'); pg.wait_for_function("document.getElementById('toast').classList.contains('show')")
    t.chk('wpis z uszkodzonymi odpowiedziami: zamiast błędu komunikat, zostajemy w Historii, opis i kwoty nietknięte', 'zapisane odpowiedzi są uszkodzone' in pg.inner_text('#toast') and pg.evaluate("state.step")==4 and pg.evaluate("state.codes.length")==0 and pg.locator('section.card.hist').count()==3 and pg.evaluate("async ()=>bodyText(await dbBody('vzlosliwy4'))")=='Opis ZT', pg.inner_text('#toast'))
    look('po nieudanym otwarciu')
    # otwarcie wpisu, w którym KAŻDE pole formularza ma wrogą wartość (budowa poprawna)
    pg.click('#hist-vzlosliwy1 button[data-act="hopen"]'); pg.wait_for_function("state.step===3"); idle(pg); look('generator krok 3')
    stt=pg.evaluate("({codes:state.codes,teeth:state.teeth,quads:state.quads,plan:state.plan,poll:({}).polluted,keys:Object.keys(state.a),gi:state.a['sh.gi'],own:Object.prototype.hasOwnProperty.call(state.a,'constructor')})")
    t.chk('„Otwórz i popraw”: z zapisanych odpowiedzi przyjęte tylko poprawne kody, zęby, powierzchnie, ćwiartki i wartości',
          stt['codes']==F['codes'] and 'ZLY' not in stt['teeth'] and all(re.fullmatch(r'\d\d',k) for c in stt['teeth'].values() for k in c) and {'11','55'}<=set(stt['teeth']['ST01']) and '1503' not in stt['teeth'] and stt['teeth']['ST01']['11']['s']==['M'] and stt['quads']['ST30']==[1] and 'ST33' not in stt['quads'] and stt['plan'] is None and stt['poll'] is None and stt['gi'] is None and not stt['own'], (stt['codes'],stt['quads'],stt['plan']))
    nf=len(F['inp'])+len(F['seg'])+len(F['chk'])
    out=pg.inner_text('.out.all')
    t.chk(f'opis wygenerowany z {nf} wrogich pól zawiera je jako zwykły tekst', nf>60 and '<img src=x onerror=' in out and '<script>' in out, nf)
    for n in (2,1): pg.click(f'#steps button[data-n="{n}"]'); pg.wait_for_timeout(120); look(f'generator krok {n}')
    pg.click('#steps button[data-n="2"]'); pg.wait_for_timeout(120)
    t.chk('krok 2: wrogie wartości trafiają do pól formularza jako tekst', pg.evaluate("[...document.querySelectorAll('#main input[data-key]')].filter(e=>e.value.includes('onerror')||e.value.includes('<script>')).length")>20, pg.evaluate("[...document.querySelectorAll('#main input[data-key]')].filter(e=>e.value.includes('onerror')||e.value.includes('<script>')).length"))
    pg.click('#steps button[data-n="3"]'); idle(pg); look('generator krok 3 ponownie')
    # siatka bezpieczeństwa: błąd w widoku nie zostawia strony odświeżonej w połowie
    errs_before=len(errs)
    pg.evaluate("()=>{state.codes=['ST01'];state.teeth={ST01:{'11':{s:[],f:{an:'tekst',why:'tekst'}}}};state.a['ST01.wer']='z pliku gabinetu';state.step=3;render();}")
    card=clean(pg.inner_text('#main'))
    t.chk('błąd podczas rysowania widoku: czytelna karta z komunikatem zamiast pustej strony, nawigacja działa', 'Nie udało się wyświetlić tego widoku' in card and 'Zapisane wizyty są bezpieczne' in card and pg.locator('button[data-act="crashreset"]').count()==1 and pg.locator('#steps button[data-n="4"]').count()==1, card[:160])
    del errs[errs_before:]                                   # ten jeden błąd w konsoli był wywołany celowo
    pg.click('button[data-act="crashreset"]'); pg.wait_for_timeout(100)
    t.chk('„Wyczyść formularz i wróć do początku” przywraca działanie (krok 1, pusty formularz, wpisy na miejscu)', pg.evaluate("state.step")==1 and pg.evaluate("state.codes.length")==0 and pg.locator('button.plan-btn').count()==8 and len(visits(pg))==3)
    # wrogie wpisy z klawiatury
    pg.fill('#i_sv_ini',X); pg.fill('#i_sh_age','9'); pg.click('button.plan-btn[data-p="o5"][data-w="I"]'); pg.click('#bar button.btn:not(.ghost)')
    pg.fill('#i_sh_api',X); pg.click('#card-ST30 button[data-act="quadset"][data-q="1,2"]'); pg.click('#bar button.btn:not(.ghost)'); idle(pg)
    pg.click('button[data-act="xadd"][data-s="v"]'); pg.fill('[data-x="v|0|a"]','10'); pg.fill('[data-x="v|0|d"]',XS); pg.press('[data-x="v|0|d"]','Tab'); idle(pg); look('wpis z klawiatury krok 3')
    k=[x for x in visits(pg) if x['id'] not in ('vzlosliwy1','vzlosliwy2','vzlosliwy4')]
    t.chk('wpis z klawiatury: inicjały oczyszczone, opis kwoty zachowany dosłownie i bezpiecznie wyświetlony', len(k)==1 and '<' not in k[0]['ini'] and k[0]['ex'][0]['d']==XS, k and (k[0]['ini'],k[0]['ex']))
    out=pg.inner_text('.out.all')
    t.chk('tekst wpisany w pole opisu (API) pojawia się w opisie dosłownie', '<img src=x onerror=' in out)
    pg.click('#steps button[data-n="4"]'); look('historia po wpisie'); pg.click('#steps button[data-n="6"]'); look('ustawienia po wpisie')
    bad=[(n,r) for n,r in views if r['x'] or r['img'] or r['inj'] or r['scripts']]
    t.chk(f'żaden wstrzyknięty kod nie został wykonany ani wstawiony jako element strony ({len(views)} widoków sprawdzonych)', not bad, bad)
    # kopia z wrogimi danymi daje się pobrać i wczytać ponownie bez zmian
    with pg.expect_download() as d: pg.click('button[data-act="bkexport"]')
    p2=os.path.join(TMP,'k2.json'); d.value.save_as(p2); pg.wait_for_function("!ui.busy")
    pg.set_input_files('#bk-file',p2); pg.wait_for_function("ui.msg&&ui.msg.includes('bez zmian 4')&&!ui.busy")
    t.chk('kopia z takimi danymi pobiera się i wczytuje ponownie bez zmian (4 wpisy)', len(visits(pg))==4)
    t.chk('brak błędów JS', not errs, errs)
    t.done('T10 wrogie dane'); b.close()
