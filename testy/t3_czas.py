# T3 – czas wizyty: zasada +10 min (pakiet higienizacyjny + ekstrakcja lub leczenie zachowawcze), limity NFZ
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
SET="""(c)=>{resetVisit();state.a['sh.age']=c.age||'9';state.codes=c.codes.slice();
  Object.entries(c.quads||{}).forEach(([k,v])=>state.quads[k]=v);
  Object.entries(c.teeth||{}).forEach(([k,ts])=>{state.teeth[k]={};ts.forEach(t=>state.teeth[k][t]={s:[],f:{}});});
  Object.entries(c.a||{}).forEach(([k,v])=>state.a[k]=v);
  const vt=visitTime(),ni=nfzIssues();return {nfz:vt.nfz,decl:vt.decl,extra:vt.extra,base:vt.base,sug:vt.sug,val:vt.val,extraCodes:vt.extraCodes,
    err:ni.err.map(e=>e.msg),warn:ni.warn.filter(w=>!w.soft).map(w=>w.msg),note:timeNote(vt)};}"""
with sync_playwright() as p:
    b=launch(p); ctx=b.new_context(viewport={'width':1100,'height':900}); errs=[]; pg=open_page(ctx,errs=errs); t=T()
    def run(**c): return pg.evaluate(SET,c)
    tm=lambda r,key: [m for m in r[key] if 'znieczulenia' not in m and '6 miesięcy' not in m]   # komunikaty o czasie (bez wymogu znieczulenia i limitu 6 mies.)
    # czas pakietu w opisie: ST30 domyślnie 21 min, ST30G 21 min, ST30E 11 min (wartości z szablonów gabinetu); standardowa wizyta 30 min
    r=run(codes=['ST33','ST30','ST26','1101'],quads={'ST30':[1]})
    t.chk('sam pakiet higienizacyjny (ST30) + badanie + 1101: nic się nie dolicza, wizyta 30 min', r['extra']==0 and r['sug']==30 and r['val']==30 and not tm(r,'warn') and not tm(r,'err'), r)
    r1=run(codes=['ST30','ST01'],quads={'ST30':[1]},teeth={'ST01':[51]})
    t.chk('pakiet + ekstrakcja 1 zęba: 30 + 10 = 40 min', r1['extra']==10 and r1['base']==30 and r1['sug']==40 and r1['val']==40, r1)
    r3=run(codes=['ST30','ST01'],quads={'ST30':[1]},teeth={'ST01':[51,52,61]})
    t.chk('pakiet + ekstrakcja 3 zębów: nadal +10 min (40 min), nie +30', r3['extra']==10 and r3['sug']==40, r3)
    r=run(codes=['ST30','1503'],quads={'ST30':[1]},teeth={'1503':[36]})
    t.chk('pakiet + procedura zachowawcza (1503): +10 min (40 min)', r['extra']==10 and r['sug']==40, r)
    r=run(codes=['ST30','ST01','ST02','1503','1108','1206'],quads={'ST30':[1]},teeth={'ST01':[51,52],'ST02':[75],'1503':[36,46],'1108':[54]})
    t.chk('pakiet + kilka dodatkowych procedur (ST01×2, ST02, 1503×2, 1108, 1206): +10 min tylko raz (40 min)', r['extra']==10 and r['sug']==40 and sorted(r['extraCodes'])==['1108','1206','1503','ST01','ST02'], r)
    bad=[c for c in ['ST01','ST02','1105','1108','1206','1502','1503','1504','1505'] if run(codes=['ST30G',c])['sug']!=40]
    t.chk('każdy z kodów ST01, ST02, 1105, 1108, 1206, 1502–1505 przy pakiecie dolicza 10 min', not bad, bad)
    bad=[c for c in ['1101','1006','ST19','ST04','ST26','ST33','ST34','ST28'] if run(codes=['ST30',c],quads={'ST30':[1]})['extra']!=0]
    t.chk('1101, 1006, ST19, ST04, ST26 i badania nie doliczają 10 min', not bad, bad)
    r=run(codes=['ST01','1503'],teeth={'ST01':[51],'1503':[36]})
    t.chk('ekstrakcja + zachowawcza bez pakietu higienizacyjnego: zasada nie dotyczy, 30 min', r['extra']==0 and r['sug']==30 and 'nie dotyczy' in r['note'], r)
    bad=[hy for hy in ['ST30','ST30E','ST30G'] if run(codes=[hy,'ST01'],quads=({hy:[1]} if hy!='ST30G' else {}))['sug']!=40]
    t.chk('wszystkie trzy pakiety (ST30, ST30E, ST30G) uruchamiają zasadę', not bad, bad)
    # limity NFZ na pakiet
    r=run(codes=['ST30'],quads={'ST30':[1,2,3,4]})
    t.chk('ST30 w 4 ćwiartkach: minimum NFZ 40 min; czas 21 min w opisie = błąd NFZ; wizyta 40 min + ostrzeżenie o przekroczeniu 30 min',
          r['nfz']==40 and r['decl']==40 and r['sug']==40 and any('krótszy niż minimum NFZ 40 min' in e for e in r['err']) and any('zajmują 40 min – więcej niż standardowa wizyta 30 min' in w for w in r['warn']), [r['err'],tm(r,'warn')])
    r=run(codes=['ST30','ST01'],quads={'ST30':[1,2,3,4]},teeth={'ST01':[51]},a={'ST30.czas':'40'})
    t.chk('ST30 ×4 (40 min) + ekstrakcja: wizyta 50 min, ostrzeżenie o przekroczeniu', r['base']==40 and r['sug']==50 and not tm(r,'err') and any('wizyta trwa 50 min' in w for w in r['warn']), tm(r,'warn'))
    r=run(codes=['ST30','ST01'],quads={'ST30':[1,2,3]},teeth={'ST01':[51]},a={'ST30.czas':'35'})
    t.chk('czas pakietów z opisu dłuższy niż 30 min (35 min) jest podstawą: 35 + 10 = 45 min', r['decl']==35 and r['base']==35 and r['sug']==45, r)
    r=run(codes=['ST30','ST01'],quads={'ST30':[1,2]},teeth={'ST01':[51]},a={'ST30.czas':'25'})
    t.chk('czas pakietów krótszy niż 30 min (25 min): podstawą standardowa wizyta, 30 + 10 = 40 min', r['decl']==25 and r['base']==30 and r['sug']==40, r)
    r=run(codes=['ST30','ST01'],quads={'ST30':[1,2]},teeth={'ST01':[51]},a={'ST30.czas':'20','sv.min':'30'})
    t.chk('czas wpisany ręcznie (30 min) bez doliczenia: ostrzeżenie, wartość ręczna zostaje', r['val']==30 and any('nie zawiera doliczenia 10 min' in w and '40 min' in w for w in r['warn']) and not tm(r,'err'), tm(r,'warn'))
    r=run(codes=['ST30'],quads={'ST30':[1,2,3]},a={'ST30.czas':'30','sv.min':'20'})
    t.chk('czas wizyty krótszy niż suma minimów pakietów NFZ: błąd', any('krótszy niż suma minimalnych czasów pakietów NFZ (30 min)' in e for e in r['err']), r['err'])
    r=run(codes=['ST30','ST01'],quads={'ST30':[1]},teeth={'ST01':[51]},a={'sv.min':'abc'})
    t.chk('błędny wpis w polu czasu jest ignorowany (zostaje podpowiedź 40 min)', r['val']==40, r)
    r=run(codes=['ST30','ST01'],quads={'ST30':[1]},teeth={'ST01':[51]},a={'sv.min':'55'})
    t.chk('czas wpisany ręcznie dłuższy niż podpowiedź: bez ostrzeżeń', r['val']==55 and not tm(r,'warn') and not tm(r,'err'), tm(r,'warn'))
    # czas trafia do zapisanego wpisu i do sumy dnia (prawdziwe kliknięcia, tryb automatyczny)
    pg.evaluate("()=>{resetVisit();render();}"); pg.click('button[data-act="automode"]')
    pg.fill('#i_sh_age','9'); pg.click('button.chip[data-c="ST30"]'); pg.click('button.chip[data-c="ST01"]'); pg.click('#bar button.btn:not(.ghost)')
    pg.click('#card-ST30 button[data-act="quad"][data-q="1"]'); pg.click('#card-ST01 .tooth[data-t="51"]'); pg.click('#card-ST01 .tooth[data-t="61"]')
    box=clean(pg.inner_text('#nfz-box'))
    t.chk('na ekranie (krok 2): informacja o doliczeniu 10 min i czasie wizyty 40 min', 'doliczono 10 min' in box and 'Czas wizyty: 40 min (30 + 10)' in box, box[-260:])
    pg.click('#bar button.btn:not(.ghost)'); idle(pg)
    v=visits(pg); note=clean(pg.inner_text('[data-o="vtime"]'))
    t.chk('zapisany wpis ma czas wizyty 40 min', len(v)==1 and v[0]['min']==40, v and v[0]['min'])
    t.chk('opis pod polem czasu tłumaczy wyliczenie', 'standardowe 30 min + 10 min' in note and '= 40 min' in note and 'doliczane raz' in note, note)
    t.chk('pole „Czas wizyty” podpowiada 40', pg.get_attribute('#i_sv_min','placeholder')=='40')
    pg.click('#resetBtn'); pg.fill('#i_sh_age','9'); pg.click('button.plan-btn[data-p="o5"][data-w="I"]'); pg.click('#bar button.btn:not(.ghost)')
    pg.click('#card-ST30 button[data-act="quad"][data-q="1"]'); pg.click('#bar button.btn:not(.ghost)'); idle(pg)
    A=pg.evaluate("(()=>{const a=agg(dbList());return {min:a.min,vis:a.vis,work:a.work};})()")
    t.chk('suma czasu wizyt dnia: 40 + 30 = 70 min', A=={'min':70,'vis':2,'work':70}, A)
    t.chk('brak błędów JS', not errs, errs)
    t.done('T3 czas wizyty i +10 min'); b.close()
