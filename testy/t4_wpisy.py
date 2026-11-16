# T4 – Historia: szybki wpis, błędne dane, edycja kwot, usuwanie, wyszukiwanie; wpływ na sumy
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
import datetime
TODAY=datetime.date.today(); TI=TODAY.isoformat(); YI=(TODAY-datetime.timedelta(days=1)).isoformat()
def wait_n(pg,n): pg.wait_for_function(f"dbList().length==={n}&&!ui.busy",timeout=5000)
def err(pg): return clean(pg.inner_text('#quick-card .err')) if pg.locator('#quick-card .err').count() else ''
def totals(pg): return pg.evaluate("(()=>{const a=agg(dbList());return {n:a.n,vis:a.vis,pts:a.ptsC,pc:a.pc,sh:a.sh,rv:a.rv,ex:a.ex,total:a.total,min:a.min,revH:a.revHc,days:a.days.size};})()")
with sync_playwright() as p:
    b=launch(p); ctx=b.new_context(viewport={'width':1100,'height':1000}); errs=[]; pg=open_page(ctx,errs=errs); t=T()
    pg.click('#steps button[data-n="4"]')
    t.chk('pusta Historia: szybki wpis z dzisiejszą datą, podsumowanie dnia 0,00 zł', pg.input_value('#f_q_date')==TI and '0,00 zł' in clean(pg.inner_text('section.card >> nth=0')))
    # 1) same punkty, Enter
    pg.fill('#f_q_pts','150'); 
    t.chk('podgląd na żywo: 150 pkt = 276,00 zł', '276,00 zł' in clean(pg.inner_text('[data-o="qsum"]')), clean(pg.inner_text('[data-o="qsum"]')))
    pg.press('#f_q_pts','Enter'); wait_n(pg,1)
    v=visits(pg); e=v[0]
    t.chk('szybki wpis punktów (Enter): 150 pkt = 276,00 zł, wizyta, 30 min, anonimowy z numerem', e['src']=='man' and e['pts']==150 and e['k']['pc']==27600 and e['k']['total']==27600 and e['visit'] and e['min']==30 and e['ini']=='' and e['no']==1 and e['date']==TI and not e['body'], e)
    t.chk('po zapisie formularz jest pusty i gotowy na kolejny wpis (kursor w polu punktów)', pg.input_value('#f_q_pts')=='' and pg.evaluate("document.activeElement.id")=='f_q_pts')
    # 2) same przeglądy
    pg.fill('#f_q_revH','1,5'); pg.click('button[data-act="qsave"]'); wait_n(pg,2)
    e=visits(pg)[0]; t.chk('wpis samych przeglądów: 1,5 h = 525,00 zł, nie jest wizytą, bez czasu wizyty', e['revH']==1.5 and e['k']['rv']==52500 and e['k']['total']==52500 and not e['visit'] and e['min'] is None, e)
    # 3) sama kwota dodatkowa
    pg.click('button[data-act="xadd"][data-s="q"]'); pg.fill('[data-x="q|0|a"]','150'); pg.fill('[data-x="q|0|d"]','dodatkowa procedura'); pg.click('button[data-act="qsave"]'); wait_n(pg,3)
    e=visits(pg)[0]; t.chk('wpis samej kwoty dodatkowej: 150,00 zł z opisem, osobna kategoria', e['ex']==[{'c':15000,'d':'dodatkowa procedura'}] and e['k']['ex']==15000 and e['k']['pc']==0 and e['k']['total']==15000 and not e['visit'], e)
    # 4) pełny wpis z inicjałami, wczorajsza data
    pg.fill('#f_q_date',YI); pg.fill('#f_q_ini','mn'); pg.fill('#f_q_pts','61,2'); pg.fill('#f_q_revH','0,5'); pg.fill('#f_q_min','45')
    pg.click('button[data-act="xadd"][data-s="q"]'); pg.fill('[data-x="q|0|a"]','80,50'); pg.fill('[data-x="q|0|d"]','a')
    pg.click('button[data-act="xadd"][data-s="q"]'); pg.fill('[data-x="q|1|a"]','19,5'); pg.fill('[data-x="q|1|d"]','b')
    pg.click('button[data-act="qsave"]'); wait_n(pg,4)
    mn=[x for x in visits(pg) if x['ini']=='MN'][0]
    t.chk('pełny szybki wpis: MN, wczoraj, 61,2 pkt = 112,61 zł, 0,5 h = 175,00 zł, dwie kwoty = 100,00 zł, razem 387,61 zł, 45 min',
          mn['date']==YI and mn['k']['pc']==11261 and mn['k']['rv']==17500 and mn['k']['ex']==10000 and mn['k']['total']==38761 and mn['min']==45 and mn['visit'], mn['k'])
    t.chk('data w formularzu zostaje na kolejny wpis (uzupełnianie zaległego dnia)', pg.input_value('#f_q_date')==YI)
    pg.fill('#f_q_date',TI)
    # 5) błędne dane – nic nie może się zapisać
    bad=[]
    def tryq(name,exp,**f):
        for k,vv in f.items(): pg.fill('#f_q_'+k,vv)
        pg.click('button[data-act="qsave"]'); pg.wait_for_timeout(150)
        m=err(pg); ok=(exp in m) and pg.evaluate("dbList().length")==4
        if not ok: bad.append((name,m))
        for k in f: pg.fill('#f_q_'+k,'' if k!='date' else TI)
    tryq('pusty formularz','wpisz punkty, godziny przeglądów albo dodatkową kwotę')
    tryq('punkty tekstem','punkty – wpisz liczbę',pts='abc')
    tryq('punkty ujemne','punkty – wpisz liczbę',pts='-5')
    tryq('punkty z dwoma przecinkami','punkty – wpisz liczbę',pts='1,2,3')
    tryq('przeglądy > 24 h','przeglądy – liczba godzin od 0 do 24',revH='30')
    tryq('przeglądy tekstem','przeglądy – liczba godzin',revH='dwie')
    tryq('czas tekstem','czas wizyty – liczba minut',pts='10',min='pół godziny')
    tryq('brak daty','podaj poprawną datę',pts='10',date='')
    pg.click('button[data-act="xadd"][data-s="q"]'); pg.fill('[data-x="q|0|a"]','0'); pg.fill('[data-x="q|0|d"]','zero')
    pg.click('button[data-act="qsave"]'); pg.wait_for_timeout(150)
    if not ('dodatkowy zarobek 1 – wpisz kwotę większą od 0' in err(pg) and pg.evaluate("dbList().length")==4): bad.append(('kwota 0',err(pg)))
    pg.fill('[data-x="q|0|a"]','sto'); pg.click('button[data-act="qsave"]'); pg.wait_for_timeout(150)
    if not ('dodatkowy zarobek 1' in err(pg) and pg.evaluate("dbList().length")==4): bad.append(('kwota tekstem',err(pg)))
    pg.click('button[data-act="xdel"][data-s="q"][data-i="0"]')
    t.chk('10 rodzajów błędnych danych: czytelny komunikat, nic się nie zapisuje', not bad, bad)
    T0=totals(pg)
    t.chk('sumy po 4 wpisach: 211,2 pkt; punkty 388,61; przeglądy 700,00; dodatkowe 250,00; razem 1338,61; wizyt 2 z 4 wpisów; 75 min; 2 dni',
          T0=={'n':4,'vis':2,'pts':21120,'pc':38861,'sh':15544,'rv':70000,'ex':25000,'total':133861,'min':75,'revH':200,'days':2}, T0)
    head=clean(pg.inner_text('.dayh >> nth=0'))
    t.chk('nagłówek dzisiejszego dnia: 1 wizyta · 150 pkt · 951,00 zł · przeglądy 1,5 h', '1 wizyta' in head and '150 pkt' in head and '951,00 zł' in head and 'przeglądy 1,5 h' in head, head)
    today=clean(pg.inner_text('section.card >> nth=0'))
    t.chk('karta „Dziś”: 951,00 zł; punkty 276,00; przeglądy 525,00; dodatkowe 150,00', '951,00 zł' in today and '276,00 zł' in today and '525,00 zł' in today and '150,00 zł' in today, today)
    # 6) edycja kwot
    pg.click(f'#hist-{mn["id"]} button[data-act="eopen"]')
    t.chk('formularz edycji pokazuje zapisane wartości', [pg.input_value('#f_e_'+k) for k in ('date','ini','pts','price','revH','revRate','min')]==[YI,'MN','61,2','1,84','0,5','350','45'] and pg.input_value('[data-x="e|0|a"]')=='80,50' and pg.input_value('[data-x="e|1|a"]')=='19,50', [pg.input_value('#f_e_'+k) for k in ('date','ini','pts','price','revH','revRate','min')])
    pg.fill('#f_e_pts','200'); pg.fill('#f_e_revH','2'); pg.fill('#f_e_min','50'); pg.fill('#f_e_ini','mx'); pg.fill('#f_e_date',TI)
    pg.fill('[data-x="e|0|a"]','100'); pg.click('button[data-act="xdel"][data-s="e"][data-i="1"]')
    pg.click('button[data-act="xadd"][data-s="e"]'); pg.fill('[data-x="e|1|a"]','25'); pg.fill('[data-x="e|1|d"]','nowa')
    pg.click('button[data-act="esave"]'); pg.wait_for_function("!ui.edit&&!ui.busy")
    m2=[x for x in visits(pg) if x['id']==mn['id']][0]
    t.chk('edycja: 200 pkt = 368,00; 2 h = 700,00; kwoty 100 + 25; 50 min; MX; przeniesiony na dziś; ten sam numer i identyfikator',
          m2['pts']==200 and m2['k']['pc']==36800 and m2['k']['rv']==70000 and m2['ex']==[{'c':10000,'d':'a'},{'c':2500,'d':'nowa'}] and m2['min']==50 and m2['ini']=='MX' and m2['date']==TI and m2['no']==mn['no'] and m2['created']==mn['created'] and m2['at']!=mn['at'] and len(visits(pg))==4, m2['k'])
    T1=totals(pg)
    t.chk('sumy po edycji przeliczone: 350 pkt; punkty 644,00; przeglądy 1225,00; dodatkowe 275,00; razem 2144,00; 80 min; 1 dzień',
          T1=={'n':4,'vis':2,'pts':35000,'pc':64400,'sh':25760,'rv':122500,'ex':27500,'total':214400,'min':80,'revH':350,'days':1}, T1)
    # stawki tylko tego wpisu
    pg.click(f'#hist-{mn["id"]} button[data-act="eopen"]'); pg.fill('#f_e_price','2'); pg.fill('#f_e_revRate','400'); pg.click('button[data-act="epct"][data-v="35"]')
    t.chk('podgląd na żywo w edycji: 200 pkt × 2,00 = 400,00 zł', '400,00 zł' in clean(pg.inner_text('[data-o="esum"]')), clean(pg.inner_text('[data-o="esum"]')))
    pg.press('#f_e_price','Enter'); pg.wait_for_function("!ui.edit&&!ui.busy")
    m3=[x for x in visits(pg) if x['id']==mn['id']][0]
    t.chk('własne stawki wpisu (2,00 zł/pkt, 400 zł/h, 35%): 400,00 / 140,00 / 800,00; ustawienia ogólne bez zmian', m3['k']['pc']==40000 and m3['k']['sh']==14000 and m3['k']['rv']==80000 and pg.evaluate("[cfg.price,cfg.rev,cfg.pct]")==[1.84,350,40], m3['k'])
    # błędna edycja i anulowanie
    pg.click(f'#hist-{mn["id"]} button[data-act="eopen"]'); pg.fill('#f_e_pts','x'); pg.click('button[data-act="esave"]'); pg.wait_for_timeout(150)
    t.chk('błędna edycja: komunikat, wpis bez zmian', 'punkty – wpisz liczbę' in clean(pg.inner_text(f'#hist-{mn["id"]} .err')) and [x for x in visits(pg) if x['id']==mn['id']][0]['at']==m3['at'])
    pg.fill('#f_e_pts','999'); pg.click('button[data-act="ecancel"]')
    t.chk('„Anuluj” niczego nie zmienia', [x for x in visits(pg) if x['id']==mn['id']][0]['pts']==200 and pg.locator('.eform[data-form="e"]').count()==0)
    # 7) usuwanie: pojedyncze kliknięcie nie usuwa
    first=[x for x in visits(pg) if x['pts']==150][0]
    d=pg.locator(f'#hist-{first["id"]} button[data-act="hdel"]'); d.click(); pg.wait_for_timeout(150)
    t.chk('jedno kliknięcie „usuń” tylko prosi o potwierdzenie', len(visits(pg))==4 and 'kliknij ponownie' in d.inner_text())
    d.click(); wait_n(pg,3)
    T2=totals(pg)
    t.chk('po usunięciu wpisu 150 pkt sumy maleją dokładnie o 276,00 zł i 30 min', T2['n']==3 and T2['vis']==1 and T2['pc']==40000 and T2['pts']==20000 and T2['min']==50 and T2['total']==40000+80000+52500+15000+12500, T2)
    # 8) wyszukiwanie
    def found(q): pg.fill('#i_hs_q',q); pg.wait_for_timeout(80); return pg.locator('section.card.hist').count()
    r=[found('mx'),found('#'+str(mn['no'])),found(TODAY.strftime('%d.%m')),found('nowa'),found('zzz'),found('')]
    t.chk('szukanie: inicjały 1, numer wpisu 1, data 3, opis kwoty 1, brak 0, puste 3', r==[1,1,3,1,0,3], r)
    # 9) statystyki pokazują te same sumy (pełna wartość i udział lekarza)
    pg.click('#steps button[data-n="5"]')
    hero=clean(pg.inner_text('.hero')); tiles=clean(pg.inner_text('.tiles'))
    t.chk('Statystyki (ten miesiąc): razem 2000,00 zł; punkty 400,00; przeglądy 1325,00 (3,5 h); dodatkowe 275,00; 1 wizyta', '2000,00 zł' in hero and '400,00 zł' in tiles and '1325,00 zł' in tiles and '3,5 h' in tiles and '275,00 zł' in tiles, tiles[:300])
    pg.click('button[data-act="basis"][data-v="share"]')
    hero=clean(pg.inner_text('.hero')); tiles=clean(pg.inner_text('.tiles'))
    t.chk('przełącznik „udział lekarza”: punkty 140,00 zł (35% wpisu), razem 1740,00 zł; przeglądy i kwoty w całości', '1740,00 zł' in hero and '140,00 zł' in tiles and '1325,00 zł' in tiles and '275,00 zł' in tiles, hero)
    pg.click('button[data-act="basis"][data-v="full"]')
    t.chk('powrót do pełnej wartości: 2000,00 zł', '2000,00 zł' in clean(pg.inner_text('.hero')))
    # 10) po ponownym uruchomieniu wszystko jest na miejscu
    pg.close(); pg=open_page(ctx,errs=errs)
    t.chk('po ponownym uruchomieniu: 3 wpisy, te same sumy', totals(pg)==T2, totals(pg))
    t.chk('brak błędów JS', not errs, errs)
    t.done('T4 szybki wpis, edycja, usuwanie'); b.close()
