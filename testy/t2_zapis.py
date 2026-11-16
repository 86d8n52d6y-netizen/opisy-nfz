# T2 – zapis wizyt: tryb z inicjałami, tryb automatyczny (anonimowy), brak dubli i nadpisań, ponowne uruchomienie
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
import datetime
TODAY=datetime.date.today().isoformat()
def gen(pg,age,plan='I',grp='o5',q='1,2',teeth=(11,12,21,22)):
    """wizyta z planu: krok 1 → 2 → 3 prawdziwymi kliknięciami"""
    pg.fill('#i_sh_age',str(age)); pg.click(f'button.plan-btn[data-p="{grp}"][data-w="{plan}"]')
    pg.click('#bar button.btn:not(.ghost)')
    if pg.locator('#card-ST30').count() and q: pg.click(f'#card-ST30 button[data-act="quadset"][data-q="{q}"]')
    if pg.locator('#card-1101').count():
        for t in teeth: pg.click(f'#card-1101 .tooth[data-t="{t}"]')
    pg.click('#bar button.btn:not(.ghost)'); idle(pg)
def st(pg): return clean(pg.inner_text('#save-st'))
def to3(pg): pg.click('#steps button[data-n="3"]'); idle(pg)
with sync_playwright() as p:
    b=launch(p); ctx=b.new_context(viewport={'width':1100,'height':900}); errs=[]; pg=open_page(ctx,errs=errs); t=T()
    # ---------- A. tryb z inicjałami ----------
    gen(pg,9)
    t.chk('A1 bez inicjałów nic się nie zapisuje', len(visits(pg))==0 and 'Nie zapisano' in st(pg))
    pg.fill('#i_sv_ini','jk'); pg.press('#i_sv_ini','Tab'); idle(pg)
    v=visits(pg); e=v[0] if v else {}
    t.chk('A2 wpis z inicjałami: JK, dziś, 286,8 pkt, 527,71 zł, lekarz 211,08 zł, 30 min, ma opis',
          len(v)==1 and e['ini']=='JK' and e['date']==TODAY and e['pts']==286.8 and e['k']['pc']==52771 and e['k']['sh']==21108 and e['min']==30 and e['body'] and e['src']=='gen' and e['visit'], e)
    t.chk('A2 dzień tygodnia w statusie zapisu', any(d in st(pg) for d in ['pon.','wt.','śr.','czw.','pt.','sob.','niedz.']) and 'Zapisano: JK' in st(pg), st(pg))
    pg.evaluate("()=>{window.__w=0;const o=DB.be.write.bind(DB.be);DB.be.write=(ops)=>{window.__w++;return o(ops);};}")
    at0=e['at']; pg.evaluate("for(let i=0;i<6;i++)render()"); idle(pg)
    pg.click('section.card button[data-act="copyall"]'); idle(pg)
    v=visits(pg)
    t.chk('A3 sześć odświeżeń i „Kopiuj” bez zmian: 0 zapisów, 1 wpis, ten sam znacznik czasu', pg.evaluate("window.__w")==0 and len(v)==1 and v[0]['at']==at0, pg.evaluate("window.__w"))
    pg.fill('#i_sv_revH','1,5'); pg.press('#i_sv_revH','Tab'); idle(pg)
    v=visits(pg); t.chk('A4 przeglądy 1,5 h → ten sam wpis, +525,00 zł', len(v)==1 and v[0]['id']==e['id'] and v[0]['revH']==1.5 and v[0]['k']['rv']==52500 and v[0]['k']['total']==52771+52500, v[0]['k'])
    pg.click('button[data-act="xadd"][data-s="v"]'); pg.fill('[data-x="v|0|a"]','150'); pg.fill('[data-x="v|0|d"]','dodatkowa procedura'); pg.press('[data-x="v|0|d"]','Tab'); idle(pg)
    pg.click('button[data-act="xadd"][data-s="v"]'); pg.fill('[data-x="v|1|a"]','80,50'); pg.fill('[data-x="v|1|d"]','wybielanie'); pg.press('[data-x="v|1|d"]','Tab'); idle(pg)
    v=visits(pg); t.chk('A5 dwa dodatkowe zarobki (150,00 + 80,50) jako osobna kategoria', len(v)==1 and v[0]['ex']==[{'c':15000,'d':'dodatkowa procedura'},{'c':8050,'d':'wybielanie'}] and v[0]['k']['ex']==23050 and v[0]['k']['pc']==52771 and v[0]['k']['total']==52771+52500+23050, v[0]['ex'])
    t.chk('A5 suma na ekranie: punkty + przeglądy + dodatkowe', '527,71 zł' in clean(pg.inner_text('[data-o="vsum"]')) and '525,00 zł' in clean(pg.inner_text('[data-o="vsum"]')) and '230,50 zł' in clean(pg.inner_text('[data-o="vsum"]')) and '1283,21 zł' in clean(pg.inner_text('[data-o="vsum"]')), clean(pg.inner_text('[data-o="vsum"]')))
    pg.click('button[data-act="xdel"][data-s="v"][data-i="0"]'); idle(pg)
    v=visits(pg); t.chk('A5 usunięcie pierwszej kwoty → zostaje 80,50', len(v)==1 and v[0]['ex']==[{'c':8050,'d':'wybielanie'}], v[0]['ex'])
    pg.fill('#i_sv_min','45'); pg.press('#i_sv_min','Tab'); idle(pg)
    v=visits(pg); t.chk('A6 czas wizyty wpisany ręcznie: 45 min', v[0]['min']==45)
    n_w=pg.evaluate("window.__w")
    # przeglądy 1 + (kwota, opis) × 2 pozycje = 4 + usunięcie pozycji 1 + czas 1 = 7 zatwierdzonych zmian pól
    t.chk('A6 każda zatwierdzona zmiana pola = dokładnie jeden zapis (7 zmian → 7 zapisów, bez zapisów zbędnych)', n_w==7, n_w)
    pg.click('#resetBtn'); pg.wait_for_timeout(100)
    t.chk('A7 „Następny pacjent” jednym kliknięciem czyści formularz, wpis JK zostaje', pg.evaluate("state.step")==1 and pg.evaluate("state.codes.length")==0 and pg.input_value('#i_sv_ini')=='' and len(visits(pg))==1)
    # drugi pacjent
    pg.fill('#i_sv_ini','AB'); gen(pg,7,'II')
    v=visits(pg); t.chk('A8 drugi pacjent AB = drugi wpis, JK nietknięty', len(v)==2 and {x['ini'] for x in v}=={'JK','AB'} and [x for x in v if x['ini']=='JK'][0]['min']==45)
    ab=[x for x in v if x['ini']=='AB'][0]
    # bez „Następny pacjent”: inne inicjały
    pg.click('#steps button[data-n="1"]'); pg.fill('#i_sv_ini','cd'); to3(pg)
    v=visits(pg); t.chk('A9 zmiana inicjałów bez „Następny pacjent”: zapis wstrzymany, AB bez zmian', len(v)==2 and 'Inicjały zmienione z AB na CD' in st(pg) and [x for x in v if x['id']==ab['id']][0]['at']==ab['at'], st(pg))
    pg.click('#save-st button[data-act="savenew"]'); idle(pg)
    v=visits(pg); t.chk('A9 „To nowy pacjent” → trzeci wpis CD, AB i JK zostają', len(v)==3 and {x['ini'] for x in v}=={'JK','AB','CD'} and len({x['id'] for x in v})==3 and len({x['no'] for x in v})==3, [(x['ini'],x['no']) for x in v])
    pg.click('#steps button[data-n="1"]'); pg.fill('#i_sv_ini','ce'); to3(pg)
    t.chk('A10 kolejna zmiana inicjałów znów wstrzymuje zapis', 'Inicjały zmienione z CD na CE' in st(pg) and len(visits(pg))==3)
    pg.click('#save-st button[data-act="savefix"]'); idle(pg)
    v=visits(pg); t.chk('A10 „To poprawka” → nadal 3 wpisy, CD przemianowany na CE', len(v)==3 and {x['ini'] for x in v}=={'JK','AB','CE'}, [x['ini'] for x in v])
    # inny wiek
    ce=[x for x in v if x['ini']=='CE'][0]
    pg.click('#steps button[data-n="1"]'); pg.fill('#i_sh_age','12'); to3(pg)
    v=visits(pg); t.chk('A11 inny wiek → pytanie, wpis CE bez zmian', 'Inny wiek pacjenta' in st(pg) and [x for x in v if x['id']==ce['id']][0]['at']==ce['at'], st(pg))
    pg.click('#save-st button[data-act="savefix"]'); idle(pg)
    v=visits(pg); t.chk('A11 „To poprawka tej wizyty” → ten sam wpis zaktualizowany', len(v)==3 and [x for x in v if x['id']==ce['id']][0]['at']!=ce['at'])
    # zamiana zabiegów (ST34 → ST33)
    pg.click('#steps button[data-n="1"]'); pg.click('button.chip[data-c="ST34"]'); pg.click('button.chip[data-c="ST33"]'); to3(pg)
    t.chk('A12 zamienione zabiegi → pytanie, nic nie nadpisano', 'Inne zabiegi' in st(pg) and len(visits(pg))==3, st(pg))
    pg.click('#save-st button[data-act="savefix"]'); idle(pg)
    # samo dodanie kodu = poprawka bez pytania
    ce=[x for x in visits(pg) if x['ini']=='CE'][0]
    pg.click('#steps button[data-n="1"]'); pg.click('button.chip[data-c="1006"]'); to3(pg)
    v=visits(pg); c2=[x for x in v if x['id']==ce['id']][0]
    t.chk('A13 samo dodanie kodu (1006) = poprawka bez pytania, ten sam wpis', 'Zapisano: CE' in st(pg) and len(v)==3 and '1006' in c2['codes'] and c2['at']!=ce['at'], st(pg))
    # usunięcie inicjałów przy zapisanym wpisie
    pg.fill('#i_sv_ini',''); pg.press('#i_sv_ini','Tab'); idle(pg)
    v=visits(pg); t.chk('A14 usunięcie inicjałów: wpis CE zostaje, zmiany nie są zapisywane', 'Usunięto inicjały' in st(pg) and len(v)==3 and [x for x in v if x['id']==ce['id']][0]['ini']=='CE', st(pg))
    pg.click('#resetBtn'); pg.click('#resetBtn'); pg.wait_for_timeout(100)
    # ---------- B. tryb automatyczny (anonimowy) ----------
    pg.click('button[data-act="automode"]')
    t.chk('B1 przełącznik jednym kliknięciem: tryb automatyczny, pole inicjałów znika', pg.evaluate("cfg.auto")==True and pg.locator('#i_sv_ini').count()==0 and pg.get_attribute('button[data-act="automode"]','aria-checked')=='true')
    gen(pg,9)
    v=visits(pg); a1=v[0]
    t.chk('B2 wizyta zapisana sama, bez inicjałów, z numerem', len(v)==4 and a1['ini']=='' and a1['no']>0 and 'Zapisano: Anonim #'+str(a1['no']) in st(pg), st(pg))
    pg.click('#resetBtn'); pg.wait_for_timeout(100)
    gen(pg,9)   # ten sam wiek i te same zabiegi – kolejny pacjent
    v=visits(pg); an=[x for x in v if x['ini']=='']
    t.chk('B3 kolejna anonimowa wizyta nie nadpisuje poprzedniej: 2 wpisy, różne id i numery', len(v)==5 and len(an)==2 and an[0]['id']!=an[1]['id'] and an[0]['no']!=an[1]['no'] and [x for x in v if x['id']==a1['id']][0]['at']==a1['at'], [(x['no'],x['pts']) for x in an])
    # bez „Następny pacjent” w trybie anonimowym: inny wiek → pytanie
    pg.click('#steps button[data-n="1"]')
    t.chk('B4 na kroku 1 widać ostrzeżenie o powiązaniu z zapisaną wizytą', pg.locator('#link-ban.link-ban').count()==1 and 'powiązany z zapisaną wizytą' in pg.inner_text('#link-ban'))
    pg.fill('#i_sh_age','6'); to3(pg)
    t.chk('B4 anonimowo, inny wiek bez „Następny pacjent” → pytanie zamiast nadpisania', 'Inny wiek pacjenta' in st(pg) and len(visits(pg))==5, st(pg))
    pg.click('#save-st button[data-act="savenew"]'); idle(pg)
    v=visits(pg); t.chk('B4 „To nowy pacjent” → trzeci wpis anonimowy', len(v)==6 and len([x for x in v if x['ini']==''])==3)
    # inne API i GI (ten sam wiek, te same zabiegi)
    pg.click('#steps button[data-n="2"]'); pg.fill('#i_sh_api','35'); pg.fill('#i_sh_gi','1'); to3(pg)
    pg.click('#steps button[data-n="2"]'); pg.fill('#i_sh_api','80'); pg.fill('#i_sh_gi','2'); to3(pg)
    t.chk('B5 ten sam wiek i zabiegi, ale inne API i GI → pytanie', 'Inne wyniki badania' in st(pg) and len(visits(pg))==6, st(pg))
    pg.click('#save-st button[data-act="savenew"]'); idle(pg)
    t.chk('B5 → czwarty wpis anonimowy', len([x for x in visits(pg) if x['ini']==''])==4)
    ids_before=sorted(x['id'] for x in visits(pg))
    # ---------- C. ponowne uruchomienie ----------
    pg.close(); pg=open_page(ctx,errs=errs)
    v=visits(pg)
    t.chk('C1 po zamknięciu i ponownym otwarciu: tryb automatyczny nadal włączony, 7 wpisów na miejscu', pg.evaluate("cfg.auto")==True and sorted(x['id'] for x in v)==ids_before and len(v)==7, len(v))
    t.chk('C1 licznik w zakładce Historia', 'Historia (7)' in clean(pg.inner_text('#steps')), clean(pg.inner_text('#steps')))
    t.chk('C1 ostatnia wizyta wraca na ekran (szkic), bez nowego zapisu', pg.evaluate("state.step")==3 and pg.evaluate("state.codes.length")==4 and len(visits(pg))==7)
    pg.click('#resetBtn'); pg.wait_for_timeout(100)
    if pg.evaluate("state.codes.length"): pg.click('#resetBtn'); pg.wait_for_timeout(100)
    gen(pg,9)
    v=visits(pg); t.chk('C2 zapis automatyczny działa po ponownym uruchomieniu: 8. wpis z nowym numerem', len(v)==8 and len({x['no'] for x in v})==8 and max(x['no'] for x in v)==v[0]['no'])
    # otwarcie wpisu z historii nie tworzy dubla i nie zapisuje bez zmian
    pg.click('#steps button[data-n="4"]'); idle(pg)
    jk=[x for x in visits(pg) if x['ini']=='JK'][0]
    pg.fill('#i_hs_q','JK'); pg.click(f'#hist-{jk["id"]} button[data-act="hopen"]'); pg.wait_for_function("state.step===3"); idle(pg)
    v=visits(pg); j2=[x for x in v if x['id']==jk['id']][0]
    t.chk('C3 „Otwórz i popraw”: formularz odtworzony (inicjały, przeglądy, kwota, 45 min), bez dubla i bez zapisu', len(v)==8 and j2['at']==jk['at'] and pg.input_value('#i_sv_ini')=='JK' and pg.input_value('#i_sv_revH')=='1,5' and pg.input_value('#i_sv_min')=='45' and pg.input_value('[data-x="v|0|a"]')=='80,50', [pg.input_value('#i_sv_revH'),pg.input_value('#i_sv_min')])
    pg.fill('#i_sv_revH','2'); pg.press('#i_sv_revH','Tab'); idle(pg)
    v=visits(pg); j3=[x for x in v if x['id']==jk['id']][0]
    t.chk('C3 poprawka otwartego wpisu aktualizuje ten sam wpis (2 h przeglądów)', len(v)==8 and j3['revH']==2 and j3['no']==jk['no'] and j3['created']==jk['created'])
    # ---------- D. usunięcie / edycja wpisu bieżącej wizyty ----------
    pg.click('#steps button[data-n="4"]'); pg.fill('#i_hs_q','JK')
    d=pg.locator(f'#hist-{jk["id"]} button[data-act="hdel"]'); d.click(); d.click(); pg.wait_for_function("dbList().length===7")
    pg.click('#bar button.btn'); idle(pg)
    t.chk('D1 usunięty wpis bieżącej wizyty nie wraca sam po powrocie do opisu', len(visits(pg))==7 and 'nie jest teraz zapisywana' in st(pg), st(pg))
    pg.click('#save-st button[data-act="saveforce"]'); idle(pg)
    v=visits(pg); t.chk('D1 „Zapisz z formularza” zapisuje ją ponownie jako nowy wpis', len(v)==8 and len([x for x in v if x['ini']=='JK'])==1)
    # ---------- E. wyłączenie trybu automatycznego ----------
    pg.click('#resetBtn'); pg.wait_for_timeout(100); pg.click('button[data-act="automode"]')
    gen(pg,9)
    t.chk('E1 po wyłączeniu przełącznika znów wymagane inicjały', pg.evaluate("cfg.auto")==False and len(visits(pg))==8 and 'Nie zapisano' in st(pg))
    t.chk('brak błędów JS', not errs, errs)
    t.done('T2 zapis wizyt'); b.close()
