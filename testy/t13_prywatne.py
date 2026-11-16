# T13 – Opisy prywatne: katalog 19 procedur, formularz i tekst opisu, brak czynności dopisanych samoczynnie, cenniki gabinetów,
#       wynagrodzenie (% po kosztach / kwota) z wyrocznią Decimal, zapis zaszyfrowany, edycja tekstu, historia, szablon z wizyty,
#       szkic przy przełączaniu modułów, zarobki, okno Zarobki na stronie głównej, usuwanie treści starych opisów, usuwanie wizyty
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
import datetime, random, re
from decimal import Decimal, ROUND_HALF_UP
TODAY=datetime.date.today().isoformat()
RAW="""async ([db,store])=>{const r=indexedDB.open(db);const d=await new Promise(a=>{r.onsuccess=()=>a(r.result);});
  const t=d.transaction(store,'readonly'),o=t.objectStore(store);const ks=await new Promise(a=>{const q=o.getAllKeys();q.onsuccess=()=>a(q.result);});
  const vs=await new Promise(a=>{const q=o.getAll();q.onsuccess=()=>a(q.result);});d.close();return ks.map((k,i)=>[k,vs[i]]);}"""
ENC=re.compile(r'v1:[A-Za-z0-9+/=]+:[A-Za-z0-9+/=]+')
def ready(pg): pg.wait_for_function("typeof S!=='undefined'&&S.ready===true",timeout=15000)
def tab(pg,k): pg.click(f'#tabs button[data-tab="{k}"]'); pg.wait_for_timeout(80)
def fid(pg,i,k): return '#f_'+pg.evaluate(f"V.items[{i}].u")+'_'+k
def prid(pg,i,k): return '#pr_'+pg.evaluate(f"V.items[{i}].u")+'_'+k
def txt(pg): return pg.evaluate("curText()")
def it_(pg,sel): return clean(pg.inner_text(sel)).replace('\n',' ')
def oracle(c,q,cost,p):
    base=max(0,c*q-cost); return int((Decimal(base)*Decimal(str(p))/Decimal(100)).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
with sync_playwright() as p:
    b=launch(p); t=T(); errs=[]
    ctx=b.new_context(viewport={'width':1366,'height':950}); login(ctx)
    # ---------- gabinety w Kalendarzu: A (dziś dyżur), B ----------
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append('console: '+m.text) if m.type=='error' and 'ERR_' not in m.text and '404' not in m.text else None)
    pg.goto(KAL); pg.wait_for_function("window.Kal&&Kal.UI.loaded===true",timeout=15000)
    A,B=pg.evaluate("(d)=>{const K=Kal,s=K.S();s.clinics[0].name='Gabinet A';s.clinics[1].name='Gabinet B';s.clinics[0].active=s.clinics[1].active=true;K.saveSettings();K.M(d.slice(0,7),true).shifts.push({id:K.uid(),date:d,clinicId:s.clinics[0].id,start:'00:00',end:'23:59',status:'planned'});K.saveMonth(d.slice(0,7));return [s.clinics[0].id,s.clinics[1].id];}",TODAY)
    pg.wait_for_function("Kal.Store.sync==='saved'",timeout=8000)
    # ---------- moduł i katalog ----------
    pg.click('#gbar a[data-gmod="prywatne"]'); pg.wait_for_url('**/prywatne.html'); ready(pg)
    t.chk('pasek: „Opisy prywatne” otwiera moduł, aktywna pozycja paska', pg.inner_text('#gbar .gbar-nav a.on')=='Opisy prywatne')
    cat=pg.evaluate("KAT.kat.map(k=>[k.name,KAT.proc.filter(p=>p.kat===k.id).length])")
    t.chk('katalog: 19 procedur w 6 kategoriach (3 zachowawcze, 2 endo, 5 orto, 3 chirurgia, 3 higienizacja, 3 diagnostyka)', [c[1] for c in cat]==[3,2,5,3,3,3] and pg.locator('button[data-add]').count()==19, cat)
    pg.fill('#p_q','endodon'); pg.wait_for_timeout(250)
    t.chk('wyszukiwarka procedur („endodon” → 2 procedury)', pg.locator('button[data-add]').count()==2, pg.locator('button[data-add]').count())
    pg.fill('#p_q',''); pg.wait_for_timeout(250); pg.click('.pw-chip[data-kat="chir"]')
    t.chk('filtr kategorii (Chirurgia → 3)', pg.locator('button[data-add]').count()==3); pg.click('.pw-chip[data-kat=""]')
    # nowa procedura nie dopisuje czynności sama
    pg.click('button[data-add="zach-staly"]')
    t.chk('po dodaniu procedury lista się zwija (formularz procedury u góry), wyszukiwarka i kategorie zostają', pg.locator('button[data-add]').count()==0 and pg.locator('#p_q').count()==1)
    pg.click('.pw-chip[data-kat="orto"]'); t.chk('…kategoria rozwija listę (Ortodoncja → 5)', pg.locator('button[data-add]').count()==5)
    pg.click('button[data-a="pickhide"]')
    pg.evaluate("()=>{KAT.proc.slice(1).forEach(p=>V.items.push(newItem(p.id)));render();}")
    full=txt(pg)
    t.chk('19 dodanych procedur bez wypełniania: brak „bez powikłań”, zaleceń, zgody, znieczulenia i e-ZLA – tylko istota zabiegu i pola [UZUPEŁNIJ]',
          not re.search(r'bez powikłań|Zalecenia|zgodę|Znieczulenie|e-ZLA|Zalecone leki',full) and full.count('[UZUPEŁNIJ')==pg.evaluate("countMiss(curText())")>=19, full[:200])
    pg.evaluate("()=>{V=newVisit();render();}")
    # ---------- cennik ----------
    tab(pg,'cen'); pg.click(f'button[data-cg="{A}"]')
    pg.fill('#c_pct','40'); pg.press('#c_pct','Tab')
    pg.fill('[data-cc="zach-kompozyt"]','400'); pg.press('[data-cc="zach-kompozyt"]','Tab')
    pg.fill('[data-cc="hig-skaling"]','250'); pg.press('[data-cc="hig-skaling"]','Tab')
    pg.click(f'button[data-cg="{B}"]'); pg.fill('#c_pct','35'); pg.press('#c_pct','Tab')
    pg.fill('[data-cc="zach-kompozyt"]','350'); pg.press('[data-cc="zach-kompozyt"]','Tab')
    pg.select_option('[data-cm="zach-kompozyt"]','kw'); pg.fill('[data-cv="zach-kompozyt"]','150'); pg.press('[data-cv="zach-kompozyt"]','Tab')
    pg.fill('[data-cc="hig-skaling"]','300'); pg.press('[data-cc="hig-skaling"]','Tab'); pg.wait_for_timeout(500)
    rowB=clean(pg.locator('#c_tbl tr:has([data-cc="zach-kompozyt"])').inner_text())
    t.chk('cennik B: kompozyt 350 zł, wynagrodzenie kwotą 150 zł (podgląd w tabeli)', '350,00 zł' in rowB and '150,00 zł' in rowB, rowB)
    cen=pg.evaluate("S.cennik.gab"); kv=dict(pg.evaluate(RAW,['gabinet@'+pg.evaluate("G.user.id"),'kv']))
    t.chk('cenniki zapisane osobno dla gabinetów i zaszyfrowane', cen[A]['pct']==40 and cen[A]['items']['zach-kompozyt']['c']==40000 and cen[B]['items']['zach-kompozyt']=={'c':35000,'m':'kw','kw':15000} and ENC.fullmatch(kv.get('pryw:cennik','')) is not None, cen)
    # ---------- wizyta: formularz, tekst, ceny ----------
    tab(pg,'wiz')
    t.chk('gabinet wizyty domyślnie z dyżuru w Kalendarzu (Gabinet A)', 'Gabinet A' in pg.inner_text('#v_gab option:checked') and pg.evaluate("resolveGab()")==A)
    pg.click('button[data-add="zach-kompozyt"]')
    t.chk('procedura dostaje cenę i % z cennika gabinetu A (400 zł, 40% → 160 zł)', pg.input_value(prid(pg,0,'c'))=='400' and pg.input_value(prid(pg,0,'p'))=='40' and '160,00 zł' in it_(pg,prid(pg,0,'pay')))
    pg.click(f'#it-{pg.evaluate("V.items[0].u")} button[data-a="pick"]'); pg.click('.pw-tb[data-t="36"]')
    for o in ['M','O']: pg.check(f'#it-{pg.evaluate("V.items[0].u")} .pw-ms label:has-text("{o}") input')
    pg.fill(fid(pg,0,'rozp'),'próchnica zębiny (K02.1)')
    pg.select_option(fid(pg,0,'zn'),'nasiękowe')
    pg.fill(fid(pg,0,'znprep'),'artykaina 4% z adrenaliną 1:100 000'); pg.fill(fid(pg,0,'zndawka'),'1,7')
    pg.check(f'#it-{pg.evaluate("V.items[0].u")} .pw-ms label:has-text("kształtka i klin") input')
    pg.fill(fid(pg,0,'mat'),'kompozyt'); pg.fill(fid(pg,0,'odcien'),'A2')
    exp=('Ząb 36, powierzchnie MO. Rozpoznanie: próchnica zębiny (K02.1).\nZnieczulenie: nasiękowe, artykaina 4% z adrenaliną 1:100 000 – 1,7 ml.\n'
         'Przebieg: opracowanie ubytku, kształtka i klin, wytrawianie, system wiążący, odbudowa kompozytowa warstwowa.\nOdbudowa: kompozyt, odcień A2.')
    t.chk('tekst opisu z formularza – dokładnie (ząb z diagramu, powierzchnie, znieczulenie, czynności w kolejności zabiegu), opis kompletny', txt(pg)==exp and 'kompletny' in pg.inner_text('#miss'), txt(pg))
    t.chk('podgląd na bieżąco pokazuje ten sam tekst', clean(pg.inner_text('#txt'))==clean(exp))
    pg.select_option(fid(pg,0,'zn'),'nie stosowano'); pg.wait_for_timeout(100)
    t.chk('„nie stosowano” chowa środek i dawkę – znikają też z opisu', pg.locator(fid(pg,0,'znprep')).count()==0 and 'Znieczulenie: nie stosowano.' in txt(pg) and 'artykaina' not in txt(pg))
    pg.select_option(fid(pg,0,'zn'),'nasiękowe'); pg.wait_for_timeout(100)
    t.chk('…powrót do „nasiękowe” przywraca wpisane wartości', txt(pg)==exp)
    pg.fill(fid(pg,0,'zab'),'19'); pg.press(fid(pg,0,'zab'),'Tab'); pg.wait_for_timeout(100)
    t.chk('numer zęba spoza FDI (19) → ostrzeżenie przy polu', 'Nie ma zęba o numerze 19' in pg.inner_text(f'#it-{pg.evaluate("V.items[0].u")}'))
    pg.fill(fid(pg,0,'zab'),'36'); pg.press(fid(pg,0,'zab'),'Tab')
    pg.fill('#p_q','skaling'); pg.wait_for_timeout(250); pg.click('button[data-add="hig-skaling"]')
    pg.select_option(fid(pg,1,'zakres'),'szczęka i żuchwa')
    t.chk('druga procedura: skaling 250 zł, 40% → 100 zł; suma 650 / 260 zł', '650,00 zł' in it_(pg,'#sum') and '260,00 zł' in it_(pg,'#sum'), clean(it_(pg,'#sum')))
    pg.select_option('#v_gab',B); pg.wait_for_timeout(150)
    t.chk('zmiana gabinetu na B → ceny z cennika B (kompozyt 350 / kwota 150, skaling 300 / 35% = 105)', pg.input_value(prid(pg,0,'c'))=='350' and pg.input_value(prid(pg,0,'kw'))=='150' and '105,00 zł' in it_(pg,prid(pg,1,'pay')) and '650,00 zł' in it_(pg,'#sum') and '255,00 zł' in it_(pg,'#sum'), clean(it_(pg,'#sum')))
    pg.select_option('#v_gab',A); pg.wait_for_timeout(150)
    pg.fill(prid(pg,0,'c'),'420'); pg.fill(prid(pg,0,'k'),'50'); pg.fill(prid(pg,1,'q'),'2'); pg.press(prid(pg,1,'q'),'Tab'); pg.wait_for_timeout(100)
    t.chk('cena zmieniona przy wizycie (420 zł) i koszty 50 zł: lekarz (420−50)×40% = 148 zł; skaling ×2 = 500 / 200 zł; razem 920 / 348 zł',
          '148,00 zł' in it_(pg,prid(pg,0,'pay')) and '200,00 zł' in it_(pg,prid(pg,1,'pay')) and '920,00 zł' in it_(pg,'#sum') and '348,00 zł' in it_(pg,'#sum'), clean(it_(pg,'#sum')))
    t.chk('…cennik gabinetu A bez zmian (400 zł)', pg.evaluate(f"S.cennik.gab['{A}'].items['zach-kompozyt'].c")==40000)
    pg.select_option('#v_gab',B); pg.wait_for_timeout(100)
    t.chk('procedura z ręczną ceną nie zmienia się przy zmianie gabinetu; pozostałe – tak', pg.input_value(prid(pg,0,'c'))=='420' and pg.input_value(prid(pg,1,'c'))=='300')
    pg.select_option('#v_gab',A); pg.wait_for_timeout(100)
    # wyrocznia Decimal
    rnd=random.Random(7); cases=[(rnd.randint(0,500000),rnd.randint(1,5),rnd.randint(0,300000),rnd.choice([0,12.5,33.33,35,40,45.5,50,99.99,100])) for _ in range(300)]
    got=pg.evaluate("(cs)=>cs.map(([c,q,cost,p])=>payOf({c,qty:q,cost,m:'pct',p}).pay)",cases)
    bad=[(c,g,oracle(*c)) for c,g in zip(cases,got) if g!=oracle(*c)]
    t.chk('wynagrodzenie % po kosztach: 300 losowych przypadków zgodnych z wyrocznią Decimal (zaokrąglenie połówek w górę, koszty > wartość → 0)', not bad, bad[:3])
    # ---------- zapis ----------
    pg.fill('#v_ini','jk'); pg.click('#b_save'); pg.wait_for_function("V.id&&S.visits.size===1"); pg.wait_for_timeout(500)
    m=pg.evaluate("[...S.visits.values()][0]"); uid=pg.evaluate("G.user.id")
    t.chk('zapis wizyty: JK, gabinet A, 2 procedury, wartość 920 zł, lekarz 348 zł, koszty 50 zł', (m['ini'],m['gab'],m['n'],m['val'],m['pay'],m['cost'])==('JK',A,2,92000,34800,5000), {k:m[k] for k in ['ini','gab','n','val','pay','cost']})
    t.chk('przycisk pokazuje „Zapisano ✓” (nieaktywny), a status „zapisano”', pg.is_disabled('#b_save') and 'zapisano' in pg.inner_text('#v_st'))
    raw=pg.evaluate(RAW,['gabinet@'+uid,'wizyty'])+pg.evaluate(RAW,['gabinet@'+uid,'opisy'])
    t.chk('w bazie tylko szyfrogram (wizyta i treść opisu)', len(raw)==2 and all(ENC.fullmatch(v) for _,v in raw))
    sums=pg.evaluate("G.sums.get('pryw')")
    t.chk('suma dnia dla strony głównej: dziś, Gabinet A, 1 wizyta, 920 / 348 zł', sums.get(TODAY,{}).get(A)=={'n':1,'val':92000,'pay':34800}, sums)
    # ---------- edycja tekstu ----------
    pg.click('#b_edit'); orig=pg.input_value('#txt_ed'); pg.fill('#txt_ed',orig+'\nDOPISEK RĘCZNY'); pg.wait_for_timeout(100)
    pg.fill(fid(pg,0,'odcien'),'A3'); pg.wait_for_timeout(150)
    t.chk('„Edytuj tekst”: zmiana w formularzu nie nadpisuje ręcznego tekstu (komunikat)', 'DOPISEK RĘCZNY' in pg.input_value('#txt_ed') and 'odcień A2' in pg.input_value('#txt_ed') and 'nie został nadpisany' in pg.inner_text('#side'))
    pg.click('#b_save'); pg.wait_for_timeout(400)
    b1=pg.evaluate("G.store('opisy').get(V.id)")
    t.chk('zapisany tekst = tekst edytowany ręcznie (znacznik „edytowany”)', 'DOPISEK RĘCZNY' in b1['txt'] and b1['edited'] is True and pg.evaluate("S.visits.get(V.id).edited")==True, (b1, pg.evaluate("[V.edited,dirty(),S.visits.get(V.id).edited]")))
    pg.click('#b_regen'); pg.click('#b_regen'); pg.wait_for_timeout(100)
    t.chk('„Wygeneruj tekst z formularza” (2 kliknięcia) wraca do tekstu z formularza (odcień A3)', 'odcień A3' in txt(pg) and 'DOPISEK' not in txt(pg) and pg.evaluate("V.edited")==False)
    # ---------- historia ----------
    pg.click('#b_new'); pg.click('#b_new'); pg.wait_for_timeout(100)
    t.chk('„Nowa wizyta” przy niezapisanych zmianach wymaga drugiego kliknięcia; potem pusty formularz', pg.evaluate("V.items.length")==0 and pg.evaluate("V.id") is None)
    tab(pg,'hist')
    h=clean(pg.inner_text('#main'))
    t.chk('Historia: wizyta JK z gabinetem, procedurami i kwotami', 'JK' in h and 'Gabinet A' in h and 'Opracowanie ubytku + odbudowa kompozytowa · Skaling ×2' in h and '348,00 zł' in h and 'wartość 920,00 zł' in h, h[:300])
    pg.fill('#h_q','DOPISEK'); pg.wait_for_timeout(700)
    t.chk('wyszukiwanie w treści opisu (DOPISEK → 1)', '1 wizyta' in pg.inner_text('#main'))
    pg.fill('#h_q','zzz'); pg.wait_for_timeout(500)
    t.chk('…„zzz” → brak', 'Brak wizyt' in pg.inner_text('#main')); pg.fill('#h_q',''); pg.wait_for_timeout(400)
    vid=m['id']; pg.click(f'#h-{vid} button[data-a="hopen"]'); pg.wait_for_timeout(300)
    t.chk('„Otwórz i popraw”: formularz z zapisanej wizyty, tekst edytowany ręcznie wraca', pg.evaluate("V.id")==vid and pg.evaluate("V.edited")==True and 'DOPISEK RĘCZNY' in pg.input_value('#txt_ed') and pg.input_value('#v_ini')=='JK')
    # cennik zmieniony po zapisie nie zmienia wizyty
    tab(pg,'cen'); pg.click(f'button[data-cg="{A}"]'); pg.fill('[data-cc="zach-kompozyt"]','500'); pg.press('[data-cc="zach-kompozyt"]','Tab'); pg.wait_for_timeout(400)
    t.chk('zmiana cennika po zapisie nie zmienia zapisanej wizyty (920 / 348 zł)', pg.evaluate(f"[S.visits.get('{vid}').val,S.visits.get('{vid}').pay]")==[92000,34800])
    tab(pg,'hist'); pg.click(f'#h-{vid} button[data-a="huse"]'); pg.wait_for_timeout(300)
    t.chk('„Użyj jako szablonu”: nowa wizyta z tymi samymi polami (ząb 36, MO), ceny z aktualnego cennika (500 zł), bez inicjałów',
          pg.evaluate("V.id") is None and pg.evaluate("V.items.length")==2 and pg.evaluate("V.items[0].vals.zab")=='36' and pg.input_value(prid(pg,0,'c'))=='500' and pg.input_value('#v_ini')=='' and txt(pg).startswith('Ząb 36, powierzchnie MO.'))
    # ---------- szkic przy przełączaniu modułów ----------
    pg.click('#gbar a[data-gmod="nfz"]'); pg.wait_for_url('**/nfz.html'); pg.wait_for_function("typeof DB!=='undefined'&&DB.ready===true")
    pg.click('#gbar a[data-gmod="prywatne"]'); pg.wait_for_url('**/prywatne.html'); ready(pg)
    t.chk('po powrocie z Opisów NFZ niezapisana wizyta jest na miejscu (2 procedury, ten sam tekst)', pg.evaluate("V.items.length")==2 and pg.evaluate("V.id") is None and txt(pg).startswith('Ząb 36, powierzchnie MO.') and pg.evaluate("S.tab")=='wiz')
    pg.click('#b_save'); pg.wait_for_function("S.visits.size===2"); pg.wait_for_timeout(400)
    # ---------- zarobki ----------
    tab(pg,'zar'); pg.click('button[data-zr="today"]'); pg.wait_for_timeout(100)
    vs=pg.evaluate("[...S.visits.values()]"); totp=sum(x['pay'] for x in vs); totv=sum(x['val'] for x in vs)
    tl=it_(pg,'#z_tiles')
    fz=lambda c: (f"{c//100:,}".replace(',',' ') if c>=1000000 else str(c//100))+','+f"{c%100:02d}"+' zł'
    t.chk('Zarobki dziś: wynagrodzenie, wartość, 2 wizyty, 6 procedur (z ilością), średnio na wizytę', fz(totp) in tl and fz(totv) in tl and 'Wizyty 2' in tl and 'Procedury 6' in tl and fz(round(totp/2)) in tl, (tl,totp,totv))
    pg.select_option('#z_kat','hig'); pg.wait_for_timeout(100); tl2=it_(pg,'#z_tiles')
    hp=sum(i['pay'] for x in vs for i in x['items'] if i['kat']=='hig')
    t.chk('filtr rodzaju zabiegu (Higienizacja): tylko skaling', fz(hp) in tl2 and 'Procedury 4' in tl2 and 'Opracowanie ubytku' not in pg.inner_text('#main'), (tl2,hp))
    pg.select_option('#z_kat',''); pg.click('button[data-zp="m"]'); pg.wait_for_timeout(100)
    t.chk('tabele: gabinety, rodzaj zabiegu, okresy (miesiące)', 'Gabinet A' in pg.inner_text('#main') and 'Leczenie zachowawcze' in pg.inner_text('#main') and TODAY[5:7]+'.'+TODAY[:4] in pg.inner_text('#main'))
    # ---------- strona główna ----------
    pg.wait_for_timeout(500); pg.goto(HOME); pg.wait_for_selector('#zarobki')
    row=[clean(r.inner_text()) for r in pg.locator('#zarobki tbody tr').all() if 'Gabinet A' in r.inner_text()]
    t.chk('strona główna: okno Zarobki – Gabinet A, wizyty prywatne 2 i zarobek prywatny', len(row)==1 and fz(totp) in row[0] and '\t2\t' in pg.locator('#zarobki tbody tr', has_text='Gabinet A').inner_text(), row)
    t.chk('kafelek „Opisy prywatne”: dziś 2 wizyty i kwota', 'Dziś: 2 wizyty · '+fz(totp) in clean(pg.inner_text('.g-tile[href="prywatne.html"]')))
    # ---------- prywatność: usuwanie treści starych opisów ----------
    pg.goto(PRYW); ready(pg)
    pg.evaluate("async ()=>{V=newVisit();V.date=isoAdd(G.today(),-40);V.gab='-';V.items=[newItem('diag-kontrolna')];V.items[0].vals.cel='kontrola stara';await saveVisit();V=newVisit();render();}")
    old=[x for x in pg.evaluate("[...S.visits.values()]") if x['date']<TODAY][0]
    tab(pg,'ust'); pg.select_option('#u_kasuj','30'); pg.wait_for_timeout(600)
    ob=pg.evaluate(f"G.store('opisy').get('{old['id']}')"); nb=pg.evaluate(f"G.store('opisy').get('{vid}')")
    t.chk('„Usuwaj treść opisów starszych niż 30 dni”: treść starej wizyty usunięta, kwoty zostają; nowsze opisy nietknięte', ob is None and pg.evaluate(f"S.visits.get('{old['id']}').body")==False and pg.evaluate(f"S.visits.get('{old['id']}').items.length")==1 and nb is not None)
    tab(pg,'hist'); t.chk('…w Historii przy starej wizycie: „treść opisu usunięta”', 'treść opisu usunięta' in pg.inner_text(f'#h-{old["id"]}'))
    # ---------- usuwanie ----------
    pg.click(f'#h-{vid} button[data-a="hdel"]'); t.chk('„Usuń” wymaga potwierdzenia', pg.evaluate("S.visits.size")==3)
    pg.click(f'#h-{vid} button[data-a="hdel"]'); pg.wait_for_timeout(500)
    sums=pg.evaluate("G.sums.get('pryw')")
    t.chk('po usunięciu: 2 wizyty, suma dnia przeliczona (1 wizyta)', pg.evaluate("S.visits.size")==2 and sums[TODAY][A]['n']==1, sums.get(TODAY))
    pg.reload(); ready(pg)
    t.chk('po ponownym otwarciu: 2 wizyty, cenniki i ustawienia na miejscu', pg.evaluate("S.visits.size")==2 and pg.evaluate(f"S.cennik.gab['{A}'].items['zach-kompozyt'].c")==50000 and pg.evaluate("S.ust.kasuj")==30)
    # ---------- tablet ----------
    pg.set_viewport_size({'width':820,'height':1180}); tab(pg,'wiz'); pg.fill('#p_q','wielokorzen'); pg.wait_for_timeout(250); pg.click('button[data-add="endo-wielo"]'); pg.wait_for_timeout(200)
    ow=pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth+1")
    t.chk('tablet 820 px: bez przewijania w bok, 3 wiersze kanałów w endodoncji wielokorzeniowej', ow and pg.locator(f'#it-{pg.evaluate("V.items[V.items.length-1].u")} .pw-rows tbody tr').count()==3, (ow, pg.evaluate("[document.documentElement.scrollWidth,V.items.map(i=>i.pid)]"), pg.evaluate("[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>window.innerWidth+1).slice(0,4).map(e=>e.tagName+'.'+e.className)")))
    pg.screenshot(path=os.path.join(SHOTS,'t13_tablet.png'))
    t.chk('brak błędów JS', not errs, errs[:3])
    t.done('T13 Opisy prywatne'); b.close()
