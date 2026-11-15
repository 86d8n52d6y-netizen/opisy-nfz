# ETAP 1 – audyt wersji wyjściowej (main, commit e8476e8): odtwarzanie podejrzewanych błędów na działającej aplikacji
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from h import *
URL=V9
def setup(pg,js): pg.evaluate(js)
with sync_playwright() as p:
    b=launch(p)
    ctx=b.new_context(viewport={'width':1100,'height':900}); pg=ctx.new_page()
    errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto(URL)
    # 1) nadpisanie wpisu przy zmianie inicjałów bez „Nowy pacjent”
    pg.evaluate("""()=>{state.a['sh.age']='9';state.a['sv.ini']='JK';state.codes=['ST33','ST30'];state.quads.ST30=[1,2];state.step=3;render();}""")
    n1=pg.evaluate("histIdx().map(x=>x.ini+':'+x.pts)")
    pg.evaluate("""()=>{state.step=1;render();state.a['sh.age']='40';state.a['sv.ini']='AB';state.codes=['ST02'];state.teeth.ST02={46:{s:[],f:{}}};state.quads={};state.step=3;render();}""")
    n2=pg.evaluate("histIdx().map(x=>x.ini+':'+x.pts)")
    print('1) nadpisanie bez resetu: po 1. pacjencie',n1,'→ po 2. pacjencie',n2,'=> JK utracony:', len(n2)==1 and n2[0].startswith('AB'))
    # 2) zbędne zapisy: ile setItem na jedno wyświetlenie kroku 3 bez żadnej zmiany
    r=pg.evaluate("""()=>{let n=0,bytes=0;const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){n++;bytes+=String(v).length;return o.apply(this,arguments);};
      const at0=histIdx()[0].at;for(let i=0;i<5;i++)render();Storage.prototype.setItem=o;return {writes:n,bytes,atChanged:histIdx()[0].at!==at0};}""")
    print('2) 5× render kroku 3 bez zmian:',r)
    # 3) zaokrąglenia
    r=pg.evaluate("""()=>{const out={};cfg.price=1.81;cfg.pct=35;out.a=money(7.5);      // 7,5 pkt × 1,81 = 13,575 → 13,58
      cfg.price=1.03;out.b=money(10);                                                    // 10,30 zł × 35% = 3,605 → 3,61
      out.js=[Math.round(1.005*100)/100, 7.5*1.81*100, 10.3*35];cfg.price=1.81;cfg.pct=40;return out;}""")
    print('3) zaokrąglenia:',json.dumps(r))
    # 4) kod wpisany jako 23.1101
    pg.evaluate("state.codes=[];addCodes('23.1101, ST30E');")
    print('4) addCodes("23.1101, ST30E"): codes',pg.evaluate("state.codes"),'nieznane',pg.evaluate("state.unknown"))
    # 5) wydajność przy dużej historii
    r=pg.evaluate("""()=>{state.a['sh.age']='9';state.codes=['ST33','ST30','ST26','1101'];state.quads.ST30=[1,2];let n=0;
      for(let i=0;i<1000;i++){state.savedId=null;state.a['sv.ini']='P'+i;const x=saveEntry();if(!x.ok)break;n++;}
      const t=(f,k=20)=>{const t0=performance.now();for(let i=0;i<k;i++)f();return +((performance.now()-t0)/k).toFixed(2);};
      state.step=3;const s3=t(()=>render());const st=t(()=>renderSteps());state.step=4;const s4=t(()=>render(),5);state.step=2;const bar=t(()=>renderBar());
      return {entries:n,idxChars:(localStorage.getItem('opisyNFZ.hidx')||'').length,render_step3_ms:s3,renderSteps_ms:st,render_historia_ms:s4,renderBar_krok2_ms:bar};}""")
    print('5) wydajność przy ~1000 wpisach:',r)
    pg.evaluate("localStorage.clear()")
    # 6) dym: wszystkie kody × wiek × kroki 2 i 3
    errs.clear()
    r=pg.evaluate("""()=>{const bad=[];Object.keys(D).forEach(c=>{[null,'3','9','16','30'].forEach(age=>{try{state.a={};state.teeth={};state.quads={};initDefaults();if(age)state.a['sh.age']=age;state.codes=[c];
        state.step=2;render();state.step=3;render();state.step=1;render();}catch(e){bad.push(c+'/'+age+': '+e.message);}});});return bad;}""")
    print('6) dym (20 kodów × 5 wariantów wieku × kroki 1–3): błędy JS:',r, errs)
    # 7) usunięcie bieżącego wpisu
    pg.evaluate("""()=>{state.a={};state.teeth={};state.quads={};initDefaults();state.savedId=null;state.a['sv.ini']='XY';state.codes=['ST34'];state.step=3;render();}""")
    a=pg.evaluate("histIdx().length"); pg.evaluate("histDel(histIdx()[0].id);render()"); b2=pg.evaluate("histIdx().length")
    print('7) usunięcie bieżącego wpisu: przed',a,'po',b2,'inicjały wyczyszczone:',pg.evaluate("state.a['sv.ini']")=='' )
    b.close()
