/* Opisy prywatne – domyślny katalog procedur (wersja 1).
   Każda procedura: id, kategoria, nazwa, pola formularza i szablon tekstu.
   Składnia szablonu: {pole} – wartość; {?pole}…{/pole} – fragment, gdy pole wypełnione; {!pole}…{/pole} – gdy puste.
   Pole wymagane i puste → [UZUPEŁNIJ: nazwa pola]. Każda linia szablonu = linia opisu; puste linie znikają.
   Zasada: żadna czynność nie trafia do opisu sama – czynności to pola do zaznaczenia (domyślnie tylko istota procedury),
   „bez powikłań”, zgoda i zalecenia są domyślnie puste. Podpowiedzi rozpoznań: kody ICD-10 (WHO) – sprawdź ze słownikiem
   systemu gabinetu. Tego pliku nie zmienia edycja szablonów – zmiany użytkownika zapisują się w jego zaszyfrowanych danych. */
(function () {
  'use strict';
  const ZN = [
    { k: 'zn', t: 'select', l: 'Znieczulenie', opts: ['nasiękowe', 'przewodowe', 'śródwięzadłowe', 'powierzchniowe', 'nie stosowano'] },
    { k: 'znprep', t: 'text', l: 'Środek znieczulający', sug: ['artykaina 4% z adrenaliną 1:100 000', 'artykaina 4% z adrenaliną 1:200 000', 'lidokaina 2% z adrenaliną', 'mepiwakaina 3% bez środka obkurczającego', 'lidokaina w żelu / aerozolu'], show: { k: 'zn', not: ['nie stosowano'] } },
    { k: 'zndawka', t: 'num', l: 'Dawka (ml)', unit: 'ml', show: { k: 'zn', not: ['nie stosowano'] } }
  ];
  const T_ZN = '{?zn}Znieczulenie: {zn}{?znprep}, {znprep}{/znprep}{?zndawka} – {zndawka} ml{/zndawka}.{/zn}';
  const WYW = { k: 'wywiad', t: 'area', l: 'Wywiad / dolegliwości', ph: 'np. ból na zimno od tygodnia; choroby ogólne, leki, alergie' };
  const BAD = { k: 'badanie', t: 'area', l: 'Badanie / badania dodatkowe', ph: 'np. test żywotności, opukiwanie, RTG' };
  const T_WB = '{?wywiad}Wywiad: {wywiad}.{/wywiad}\n{?badanie}Badanie: {badanie}.{/badanie}';
  const END = (zal, extra) => [
    { k: 'bezpow', t: 'bool', l: 'Bez powikłań (zaznacz, jeśli tak było)' },
    { k: 'powik', t: 'text', l: 'Powikłania / uwagi z przebiegu' }
  ].concat(extra || []).concat([
    { k: 'zal', t: 'multi', l: 'Zalecenia', opts: zal || [] },
    { k: 'zalinne', t: 'text', l: 'Inne zalecenia' },
    { k: 'plan', t: 'text', l: 'Plan / następna wizyta' }
  ]);
  const T_END = '{?bezpow}Zabieg przebiegł bez powikłań.{/bezpow}{?powik} {powik}.{/powik}\n' +
    '{?zal}Zalecenia: {zal}{?zalinne}; {zalinne}{/zalinne}.{/zal}{!zal}{?zalinne}Zalecenia: {zalinne}.{/zalinne}{/zal}\n' +
    '{?leki}Zalecone leki: {leki}.{/leki}\n{?plan}Plan: {plan}.{/plan}';
  const LEKI = { k: 'leki', t: 'text', l: 'Zalecone leki / recepta', ph: 'nazwa, dawkowanie' };
  const ZGODA = { k: 'zgoda', t: 'bool', l: 'Pisemna zgoda pacjenta na zabieg uzyskana' };
  const T_ZGODA = '{?zgoda}Pacjent wyraził pisemną zgodę na zabieg.{/zgoda}';
  const OPIEKUN = { k: 'opiekun', t: 'text', l: 'Opiekun obecny / zgoda opiekuna', ph: 'np. matka' };
  const T_OPIEKUN = '{?opiekun}Zabieg w obecności i za zgodą opiekuna: {opiekun}.{/opiekun}';
  const WSP = { k: 'wsp', t: 'select', l: 'Współpraca dziecka', opts: ['dobra', 'ograniczona', 'brak współpracy'] };
  const LUK = { k: 'luk', t: 'select', l: 'Łuk', opts: ['szczęka', 'żuchwa', 'szczęka i żuchwa'] };
  const POW = { k: 'pows', t: 'multi', l: 'Powierzchnie', opts: ['M', 'O', 'D', 'B', 'L', 'P', 'I'], join: '' };
  const ZAL_ZACH = ['nie spożywać pokarmów do ustąpienia znieczulenia', 'możliwa przejściowa nadwrażliwość zęba', 'w razie bólu samoistnego – kontakt z gabinetem', 'instruktaż higieny jamy ustnej'];
  const ZAL_CHIR = ['ucisk jałowym gazikiem', 'nie płukać intensywnie jamy ustnej w dniu zabiegu', 'zimne okłady', 'miękka, chłodna dieta w dniu zabiegu', 'nie palić tytoniu', 'nie spożywać pokarmów do ustąpienia znieczulenia', 'w razie krwawienia, narastającego obrzęku lub gorączki – kontakt z gabinetem'];
  const ZAL_ORTO = ['instruktaż higieny jamy ustnej z aparatem', 'unikać twardych i lepkich pokarmów', 'w razie uszkodzenia aparatu – kontakt z gabinetem'];
  const ZAL_HIG = ['instruktaż higieny jamy ustnej', 'unikać barwiących pokarmów i napojów w dniu zabiegu', 'wizyta kontrolna / higienizacja zgodnie z planem'];
  const ROZP_PRO = ['próchnica szkliwa (K02.0)', 'próchnica zębiny (K02.1)', 'próchnica cementu (K02.2)', 'próchnica zatrzymana (K02.3)', 'próchnica wtórna przy wypełnieniu', 'nieszczelne / uszkodzone wypełnienie', 'złamanie korony zęba bez obnażenia miazgi (S02.5)', 'ubytek niepróchnicowy – abrazja (K03.1)', 'ubytek niepróchnicowy – erozja (K03.2)'];
  const ROZP_ENDO = ['zapalenie miazgi (K04.0)', 'martwica miazgi (K04.1)', 'ostre zapalenie tkanek okołowierzchołkowych (K04.4)', 'przewlekłe zapalenie tkanek okołowierzchołkowych (K04.5)', 'ropień okołowierzchołkowy z przetoką (K04.6)', 'ropień okołowierzchołkowy bez przetoki (K04.7)', 'stan po leczeniu kanałowym – leczenie powtórne'];
  const ROZP_ORTO = ['anomalie stosunków łuków zębowych (K07.2)', 'anomalie ustawienia zębów (K07.3)', 'retencja po leczeniu ortodontycznym'];
  const MAT_WYP = ['kompozyt', 'kompozyt płynny', 'kompozyt typu bulk-fill', 'glasjonomer', 'glasjonomer modyfikowany żywicą', 'kompomer'];
  const KANALY = { k: 'kanaly', t: 'rows', l: 'Kanały', cols: [{ k: 'k', l: 'Kanał', ph: 'np. MB' }, { k: 'dl', l: 'Długość robocza (mm)', num: 1 }, { k: 'r', l: 'Opracowanie do (rozmiar / stożek)', ph: 'np. 30/.04' }],
    fmt: '{k}{?dl} – długość robocza {dl} mm{/dl}{?r}, opracowanie do {r}{/r}' };
  const ENDO = (multi) => ({
    fields: [
      { k: 'zab', t: 'tooth', l: 'Ząb (FDI)', req: 1 },
      { k: 'rozp', t: 'text', l: 'Rozpoznanie', req: 1, sug: ROZP_ENDO },
      { k: 'etap', t: 'select', l: 'Etap leczenia', req: 1, opts: ['pierwsza wizyta – otwarcie komory i opracowanie kanałów', 'kontynuacja leczenia', 'wypełnienie kanałów', 'leczenie na jednej wizycie (opracowanie i wypełnienie)', 'leczenie powtórne – usunięcie dotychczasowego wypełnienia kanałów'] },
      WYW, BAD
    ].concat(ZN).concat([
      { k: 'izol', t: 'select', l: 'Izolacja', opts: ['koferdam', 'wałki ligninowe, ślinociąg'] },
      { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['trepanacja i otwarcie komory', 'usunięcie miazgi', 'usunięcie dotychczasowego wypełnienia kanałów', 'odnalezienie ujść kanałów', 'pomiar długości roboczej endometrem', 'pomiar długości roboczej na RTG', 'opracowanie kanałów', 'płukanie kanałów', 'osuszenie kanałów', 'wkładka do kanałów', 'wypełnienie kanałów', 'RTG kontrolne'], def: [] },
      Object.assign({}, KANALY, multi ? { def: [{ k: '', dl: '', r: '' }, { k: '', dl: '', r: '' }, { k: '', dl: '', r: '' }] } : { def: [{ k: '', dl: '', r: '' }] }),
      { k: 'plyn', t: 'multi', l: 'Płukanie', opts: ['podchloryn sodu', 'EDTA', 'chlorheksydyna', 'sól fizjologiczna', 'aktywacja ultradźwiękowa'], show: { k: 'czyn', has: 'płukanie kanałów' } },
      { k: 'wkl', t: 'text', l: 'Wkładka do kanałów', sug: ['wodorotlenek wapnia'] },
      { k: 'metoda', t: 'select', l: 'Metoda wypełnienia kanałów', opts: ['kondensacja boczna', 'technika pojedynczego ćwieka', 'kondensacja pionowa na ciepło', 'technika termoplastyczna (fala ciągła)'] },
      { k: 'uszcz', t: 'text', l: 'Uszczelniacz', sug: ['na bazie żywic epoksydowych', 'na bazie krzemianu wapnia (bioceramiczny)', 'na bazie tlenku cynku z eugenolem'] },
      { k: 'zamk', t: 'text', l: 'Zamknięcie zęba', sug: ['opatrunek tymczasowy', 'glasjonomer', 'odbudowa kompozytowa'] },
      { k: 'rtg', t: 'text', l: 'Wynik RTG kontrolnego', show: { k: 'czyn', has: 'RTG kontrolne' } }
    ]).concat(END(ZAL_ZACH, [LEKI])),
    tpl: 'Ząb {zab}. Rozpoznanie: {rozp}.\nEtap: {etap}.\n' + T_WB + '\n' + T_ZN + '\n{?izol}Izolacja: {izol}.{/izol}\n' +
      '{?czyn}Przebieg: {czyn}.{/czyn}\n{?kanaly}' + (multi ? 'Kanały' : 'Kanał') + ': {kanaly}.{/kanaly}\n{?plyn}Płukanie: {plyn}.{/plyn}\n{?wkl}Wkładka: {wkl}.{/wkl}\n' +
      '{?metoda}Wypełnienie kanałów: {metoda}{?uszcz}, uszczelniacz {uszcz}{/uszcz}.{/metoda}{!metoda}{?uszcz}Uszczelniacz: {uszcz}.{/uszcz}{/metoda}\n{?zamk}Zamknięcie: {zamk}.{/zamk}\n{?rtg}RTG kontrolne: {rtg}.{/rtg}\n' + T_END
  });

  const P = [
    /* ---------- leczenie zachowawcze ---------- */
    { id: 'zach-staly', kat: 'zach', name: 'Leczenie zachowawcze – ząb stały', desc: 'Ubytek próchnicowy lub niepróchnicowy zęba stałego, wypełnienie.',
      fields: [
        { k: 'zab', t: 'tooth', l: 'Ząb (FDI)', req: 1 }, POW,
        { k: 'rozp', t: 'text', l: 'Rozpoznanie', req: 1, sug: ROZP_PRO },
        { k: 'klasa', t: 'select', l: 'Klasa ubytku (Black)', opts: ['I', 'II', 'III', 'IV', 'V', 'VI'] },
        WYW, BAD
      ].concat(ZN).concat([
        { k: 'izol', t: 'select', l: 'Izolacja', opts: ['koferdam', 'wałki ligninowe, ślinociąg'] },
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['opracowanie ubytku', 'usunięcie zmienionych próchnicowo tkanek', 'usunięcie starego wypełnienia', 'kształtka i klin', 'wytrawianie', 'system wiążący', 'kontrola zwarcia', 'opracowanie i polerowanie wypełnienia'], def: ['opracowanie ubytku'] },
        { k: 'podklad', t: 'text', l: 'Podkład', sug: ['materiał na bazie krzemianu wapnia', 'wodorotlenek wapnia', 'glasjonomer'] },
        { k: 'mat', t: 'text', l: 'Materiał wypełnienia', req: 1, sug: MAT_WYP },
        { k: 'odcien', t: 'text', l: 'Odcień' }
      ]).concat(END(ZAL_ZACH)),
      tpl: 'Ząb {zab}{?pows}, powierzchnie {pows}{/pows}. Rozpoznanie: {rozp}{?klasa}, ubytek klasy {klasa} wg Blacka{/klasa}.\n' + T_WB + '\n' + T_ZN + '\n{?izol}Izolacja: {izol}.{/izol}\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?podklad}Podkład: {podklad}.{/podklad}\nWypełnienie: {mat}{?odcien}, odcień {odcien}{/odcien}.\n' + T_END },
    { id: 'zach-mleczny', kat: 'zach', name: 'Leczenie zachowawcze – ząb mleczny', desc: 'Ubytek zęba mlecznego, wypełnienie.',
      fields: [
        { k: 'zab', t: 'tooth', l: 'Ząb (FDI)', req: 1, mleczne: 1 }, POW,
        { k: 'rozp', t: 'text', l: 'Rozpoznanie', req: 1, sug: ['próchnica szkliwa (K02.0)', 'próchnica zębiny (K02.1)', 'próchnica zatrzymana (K02.3)', 'nieszczelne / uszkodzone wypełnienie'] },
        WYW, BAD, OPIEKUN, WSP
      ].concat(ZN).concat([
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['opracowanie ubytku', 'usunięcie zmienionych próchnicowo tkanek', 'kontrola zwarcia', 'polerowanie wypełnienia'], def: ['opracowanie ubytku'] },
        { k: 'mat', t: 'text', l: 'Materiał wypełnienia', req: 1, sug: ['glasjonomer', 'glasjonomer modyfikowany żywicą', 'kompomer', 'kompozyt'] },
        { k: 'fluor', t: 'text', l: 'Fluoryzacja / lakierowanie (preparat)' }
      ]).concat(END(['nie spożywać pokarmów do ustąpienia znieczulenia – uwaga na przygryzanie wargi i policzka', 'instruktaż higieny jamy ustnej dla opiekuna', 'ograniczenie słodyczy i słodkich napojów między posiłkami'])),
      tpl: 'Ząb mleczny {zab}{?pows}, powierzchnie {pows}{/pows}. Rozpoznanie: {rozp}.\n' + T_WB + '\n' + T_OPIEKUN + '\n{?wsp}Współpraca dziecka: {wsp}.{/wsp}\n' + T_ZN + '\n{?czyn}Przebieg: {czyn}.{/czyn}\nWypełnienie: {mat}.\n{?fluor}Fluoryzacja: {fluor}.{/fluor}\n' + T_END },
    { id: 'zach-kompozyt', kat: 'zach', name: 'Opracowanie ubytku + odbudowa kompozytowa', desc: 'Odbudowa kompozytowa (także rozległa, po leczeniu kanałowym lub złamaniu).',
      fields: [
        { k: 'zab', t: 'tooth', l: 'Ząb (FDI)', req: 1 }, POW,
        { k: 'rozp', t: 'text', l: 'Rozpoznanie / wskazanie', req: 1, sug: ROZP_PRO.concat(['stan po leczeniu kanałowym – odbudowa korony']) },
        WYW, BAD
      ].concat(ZN).concat([
        { k: 'izol', t: 'select', l: 'Izolacja', opts: ['koferdam', 'wałki ligninowe, ślinociąg'] },
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['opracowanie ubytku', 'usunięcie zmienionych próchnicowo tkanek', 'usunięcie starego wypełnienia', 'kształtka i klin', 'klucz silikonowy', 'wytrawianie', 'system wiążący', 'wkład z włókna szklanego', 'odbudowa kompozytowa warstwowa', 'kontrola zwarcia', 'opracowanie i polerowanie odbudowy'], def: ['opracowanie ubytku', 'wytrawianie', 'system wiążący', 'odbudowa kompozytowa warstwowa'] },
        { k: 'wiaz', t: 'select', l: 'Technika wiązania', opts: ['total-etch', 'self-etch', 'selective-etch'] },
        { k: 'mat', t: 'text', l: 'Kompozyt', req: 1, sug: MAT_WYP.slice(0, 3) },
        { k: 'odcien', t: 'text', l: 'Odcień' }
      ]).concat(END(ZAL_ZACH)),
      tpl: 'Ząb {zab}{?pows}, powierzchnie {pows}{/pows}. Rozpoznanie: {rozp}.\n' + T_WB + '\n' + T_ZN + '\n{?izol}Izolacja: {izol}.{/izol}\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?wiaz}Technika wiązania: {wiaz}.{/wiaz}\nOdbudowa: {mat}{?odcien}, odcień {odcien}{/odcien}.\n' + T_END },

    /* ---------- endodoncja ---------- */
    Object.assign({ id: 'endo-jedno', kat: 'endo', name: 'Leczenie endodontyczne – ząb jednokorzeniowy', desc: 'Jeden kanał – długość robocza, opracowanie, wypełnienie.' }, ENDO(false)),
    Object.assign({ id: 'endo-wielo', kat: 'endo', name: 'Leczenie endodontyczne – ząb wielokorzeniowy', desc: 'Kilka kanałów – każdy z własną długością i opracowaniem.' }, ENDO(true)),

    /* ---------- ortodoncja ---------- */
    { id: 'orto-ruchomy', kat: 'orto', name: 'Aparat ruchomy', desc: 'Wycisk, oddanie, kontrola, aktywacja lub naprawa aparatu ruchomego.',
      fields: [
        { k: 'rozp', t: 'text', l: 'Rozpoznanie', sug: ROZP_ORTO },
        { k: 'etap', t: 'select', l: 'Wizyta', req: 1, opts: ['wycisk / skan do wykonania aparatu', 'oddanie aparatu', 'wizyta kontrolna', 'naprawa aparatu'] }, LUK,
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['wycisk', 'skan wewnątrzustny', 'dopasowanie aparatu', 'aktywacja śruby', 'aktywacja sprężyn / łuku', 'korekta płyty', 'instruktaż zakładania, noszenia i higieny aparatu'] },
        { k: 'aktyw', t: 'text', l: 'Aktywacja – szczegóły', ph: 'np. liczba obrotów śruby' },
        { k: 'noszenie', t: 'text', l: 'Zalecany czas noszenia' },
        { k: 'wsp', t: 'select', l: 'Współpraca / noszenie aparatu', opts: ['dobra', 'dostateczna', 'zła'] }
      ].concat(END(ZAL_ORTO)),
      tpl: 'Aparat ruchomy{?luk} – {luk}{/luk}. Wizyta: {etap}.\n{?rozp}Rozpoznanie: {rozp}.{/rozp}\n{?wsp}Współpraca: {wsp}.{/wsp}\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?aktyw}Aktywacja: {aktyw}.{/aktyw}\n{?noszenie}Zalecany czas noszenia: {noszenie}.{/noszenie}\n' + T_END },
    { id: 'orto-staly', kat: 'orto', name: 'Aparat stały', desc: 'Założenie zamków, wymiana łuku, kontrola, naprawa lub zdjęcie aparatu.',
      fields: [
        { k: 'rozp', t: 'text', l: 'Rozpoznanie', sug: ROZP_ORTO },
        { k: 'etap', t: 'select', l: 'Wizyta', req: 1, opts: ['założenie aparatu', 'wymiana łuku', 'wizyta kontrolna / aktywacja', 'naprawa – doklejenie zamka', 'zdjęcie aparatu'] }, LUK,
        { k: 'zeby', t: 'teeth', l: 'Zęby (zamki / naprawa)' },
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['przygotowanie powierzchni szkliwa', 'naklejenie zamków', 'założenie łuku', 'wymiana łuku', 'założenie ligatur', 'założenie elementów dodatkowych (łańcuszek, sprężyna, wyciągi)', 'usunięcie zamków i resztek kompozytu', 'polerowanie powierzchni szkliwa', 'instruktaż higieny'] },
        { k: 'luk_r', t: 'text', l: 'Łuk (rodzaj, przekrój)' },
        { k: 'hig', t: 'select', l: 'Higiena jamy ustnej', opts: ['dobra', 'dostateczna', 'zła'] }
      ].concat(END(ZAL_ORTO)),
      tpl: 'Aparat stały{?luk} – {luk}{/luk}. Wizyta: {etap}.\n{?rozp}Rozpoznanie: {rozp}.{/rozp}\n{?zeby}Zęby: {zeby}.{/zeby}\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?luk_r}Łuk: {luk_r}.{/luk_r}\n{?hig}Higiena jamy ustnej: {hig}.{/hig}\n' + T_END },
    { id: 'orto-retencja', kat: 'orto', name: 'Szyna retencyjna / aparat retencyjny', desc: 'Retencja po leczeniu: szyna termoformowana, retainer stały, aparat płytowy.',
      fields: [
        { k: 'rodzaj', t: 'select', l: 'Rodzaj', req: 1, opts: ['szyna retencyjna termoformowana', 'retainer stały (drut retencyjny)', 'aparat retencyjny ruchomy'] },
        { k: 'etap', t: 'select', l: 'Wizyta', req: 1, opts: ['wycisk / skan', 'oddanie / założenie', 'wizyta kontrolna', 'naprawa / ponowne przyklejenie'] }, LUK,
        { k: 'zeby', t: 'teeth', l: 'Zęby (retainer stały)' },
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['wycisk', 'skan wewnątrzustny', 'dopasowanie', 'przyklejenie retainera', 'kontrola retainera', 'instruktaż noszenia i higieny'] },
        { k: 'noszenie', t: 'text', l: 'Zalecany czas noszenia' }
      ].concat(END(ZAL_ORTO)),
      tpl: 'Retencja: {rodzaj}{?luk} – {luk}{/luk}. Wizyta: {etap}.\n{?zeby}Zęby: {zeby}.{/zeby}\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?noszenie}Zalecany czas noszenia: {noszenie}.{/noszenie}\n' + T_END },
    { id: 'orto-szyna-bierna', kat: 'orto', name: 'Szyna bierna', desc: 'Szyna bez elementów aktywnych (np. relaksacyjna, ochronna).',
      fields: [
        { k: 'rodzaj', t: 'text', l: 'Rodzaj szyny', req: 1, sug: ['szyna relaksacyjna (zgryzowa)', 'szyna ochronna miękka', 'szyna stabilizacyjna'] },
        { k: 'rozp', t: 'text', l: 'Rozpoznanie / wskazanie', sug: ['bruksizm', 'zaburzenia stawu skroniowo-żuchwowego (K07.6)', 'ochrona uzębienia'] },
        { k: 'etap', t: 'select', l: 'Wizyta', req: 1, opts: ['wycisk / skan', 'oddanie szyny', 'wizyta kontrolna / korekta'] }, LUK,
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['wycisk', 'skan wewnątrzustny', 'rejestracja zwarcia', 'dopasowanie szyny', 'korekta kontaktów zwarciowych', 'polerowanie', 'instruktaż użytkowania i higieny szyny'] },
        { k: 'noszenie', t: 'text', l: 'Zalecany czas noszenia' }
      ].concat(END(['przechowywać szynę w pojemniku, czyścić po każdym użyciu', 'w razie bólu lub ucisku – kontakt z gabinetem'])),
      tpl: 'Szyna bierna: {rodzaj}{?luk} – {luk}{/luk}. Wizyta: {etap}.\n{?rozp}Wskazanie: {rozp}.{/rozp}\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?noszenie}Zalecany czas noszenia: {noszenie}.{/noszenie}\n' + T_END },
    { id: 'orto-szyna-aktywna', kat: 'orto', name: 'Szyna aktywna', desc: 'Szyna przesuwająca zęby lub żuchwę (np. nakładki ortodontyczne, szyna repozycyjna).',
      fields: [
        { k: 'rodzaj', t: 'text', l: 'Rodzaj szyny', req: 1, sug: ['nakładki ortodontyczne', 'szyna repozycyjna', 'szyna z elementami aktywnymi'] },
        { k: 'rozp', t: 'text', l: 'Rozpoznanie', sug: ROZP_ORTO.concat(['zaburzenia stawu skroniowo-żuchwowego (K07.6)']) },
        { k: 'etap', t: 'select', l: 'Wizyta', req: 1, opts: ['skan / wycisk', 'oddanie szyny / zestawu nakładek', 'wizyta kontrolna – wydanie kolejnych nakładek', 'założenie lub korekta atachmentów', 'separacja interproksymalna (IPR)'] }, LUK,
        { k: 'nr', t: 'text', l: 'Etap / numer nakładki', ph: 'np. 5 z 20' },
        { k: 'zeby', t: 'teeth', l: 'Zęby (atachmenty / IPR)' },
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['skan wewnątrzustny', 'wycisk', 'założenie atachmentów', 'separacja interproksymalna (IPR)', 'kontrola dopasowania', 'aktywacja', 'instruktaż noszenia i higieny'] },
        { k: 'ipr', t: 'text', l: 'IPR – wielkość / miejsca' },
        { k: 'noszenie', t: 'text', l: 'Zalecany czas noszenia' }
      ].concat(END(ZAL_ORTO.slice(0, 1).concat(['zdejmować do jedzenia i picia innego niż woda', 'w razie bólu lub złego dopasowania – kontakt z gabinetem']))),
      tpl: 'Szyna aktywna: {rodzaj}{?luk} – {luk}{/luk}. Wizyta: {etap}.\n{?rozp}Rozpoznanie: {rozp}.{/rozp}\n{?nr}Etap: {nr}.{/nr}\n{?zeby}Zęby: {zeby}.{/zeby}\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?ipr}IPR: {ipr}.{/ipr}\n{?noszenie}Zalecany czas noszenia: {noszenie}.{/noszenie}\n' + T_END },

    /* ---------- chirurgia ---------- */
    { id: 'chir-ekstrakcja', kat: 'chir', name: 'Ekstrakcja zęba', desc: 'Usunięcie zęba stałego lub korzenia.',
      fields: [
        { k: 'zab', t: 'tooth', l: 'Ząb (FDI)', req: 1 },
        { k: 'rozp', t: 'text', l: 'Rozpoznanie / wskazanie', req: 1, sug: ['martwica miazgi (K04.1)', 'przewlekłe zapalenie tkanek okołowierzchołkowych (K04.5)', 'ropień okołowierzchołkowy bez przetoki (K04.7)', 'przewlekłe zapalenie przyzębia z ruchomością zęba (K05.3)', 'złamanie zęba – ząb niemożliwy do odbudowy (S02.5)', 'pozostawiony korzeń zęba (K08.3)', 'próchnica – ząb niemożliwy do odbudowy', 'ekstrakcja ze wskazań ortodontycznych'] },
        WYW, BAD, ZGODA
      ].concat(ZN).concat([
        { k: 'tech', t: 'select', l: 'Technika', opts: ['ekstrakcja kleszczowa', 'ekstrakcja z użyciem dźwigni', 'ekstrakcja z separacją korzeni'] },
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['ząb usunięty w całości – kontrola korzeni', 'wyłyżeczkowanie zębodołu', 'płukanie zębodołu solą fizjologiczną', 'materiał hemostatyczny w zębodole', 'szycie', 'ucisk jałowym gazikiem'] },
        { k: 'szwy', t: 'text', l: 'Szwy (rodzaj, liczba)', show: { k: 'czyn', has: 'szycie' } }
      ]).concat(END(ZAL_CHIR, [LEKI])),
      tpl: 'Ekstrakcja zęba {zab}. Rozpoznanie: {rozp}.\n' + T_WB + '\n' + T_ZGODA + '\n' + T_ZN + '\n{?tech}Technika: {tech}.{/tech}\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?szwy}Szwy: {szwy}.{/szwy}\n' + T_END },
    { id: 'chir-zatrzymany', kat: 'chir', name: 'Ekstrakcja zęba zatrzymanego', desc: 'Usunięcie chirurgiczne: płat, osteotomia, separacja.',
      fields: [
        { k: 'zab', t: 'tooth', l: 'Ząb (FDI)', req: 1 },
        { k: 'rozp', t: 'text', l: 'Rozpoznanie / wskazanie', req: 1, sug: ['ząb zatrzymany (K01.0)', 'ząb zaklinowany (K01.1)', 'ostre zapalenie okołokoronowe (K05.2)', 'przewlekłe zapalenie okołokoronowe (K05.3)', 'ekstrakcja ze wskazań ortodontycznych'] },
        WYW, { k: 'badanie', t: 'area', l: 'Badanie / RTG / CBCT', ph: 'położenie zęba, relacja do kanału żuchwy / zatoki' }, ZGODA
      ].concat(ZN).concat([
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['nacięcie i odwarstwienie płata śluzówkowo-okostnowego', 'osteotomia', 'separacja korony / korzeni', 'usunięcie zęba', 'wyłyżeczkowanie i kontrola zębodołu', 'wygładzenie brzegów kostnych', 'płukanie solą fizjologiczną', 'materiał w zębodole', 'szycie'], def: ['usunięcie zęba'] },
        { k: 'plat', t: 'text', l: 'Rodzaj płata / cięcia' },
        { k: 'matz', t: 'text', l: 'Materiał w zębodole', show: { k: 'czyn', has: 'materiał w zębodole' } },
        { k: 'szwy', t: 'text', l: 'Szwy (rodzaj, liczba)', show: { k: 'czyn', has: 'szycie' } }
      ]).concat(END(ZAL_CHIR, [LEKI])),
      tpl: 'Chirurgiczne usunięcie zęba zatrzymanego {zab}. Rozpoznanie: {rozp}.\n' + T_WB + '\n' + T_ZGODA + '\n' + T_ZN + '\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?plat}Płat / cięcie: {plat}.{/plat}\n{?matz}Materiał w zębodole: {matz}.{/matz}\n{?szwy}Szwy: {szwy}.{/szwy}\n' + T_END },
    { id: 'chir-mleczny', kat: 'chir', name: 'Ekstrakcja zęba mlecznego', desc: 'Usunięcie zęba mlecznego.',
      fields: [
        { k: 'zab', t: 'tooth', l: 'Ząb (FDI)', req: 1, mleczne: 1 },
        { k: 'rozp', t: 'text', l: 'Rozpoznanie / wskazanie', req: 1, sug: ['przetrwały ząb mleczny (K00.6)', 'martwica miazgi (K04.1)', 'ropień okołowierzchołkowy bez przetoki (K04.7)', 'ropień okołowierzchołkowy z przetoką (K04.6)', 'próchnica – ząb niemożliwy do odbudowy', 'ekstrakcja ze wskazań ortodontycznych'] },
        WYW, BAD, OPIEKUN, WSP
      ].concat(ZN).concat([
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['ekstrakcja kleszczowa', 'ząb usunięty w całości – kontrola korzeni', 'ucisk jałowym gazikiem'] }
      ]).concat(END(['ucisk jałowym gazikiem', 'nie spożywać pokarmów do ustąpienia znieczulenia – uwaga na przygryzanie wargi i policzka', 'w dniu zabiegu miękkie, chłodne posiłki', 'w razie krwawienia lub gorączki – kontakt z gabinetem'])),
      tpl: 'Ekstrakcja zęba mlecznego {zab}. Rozpoznanie: {rozp}.\n' + T_WB + '\n' + T_OPIEKUN + '\n{?wsp}Współpraca dziecka: {wsp}.{/wsp}\n' + T_ZN + '\n{?czyn}Przebieg: {czyn}.{/czyn}\n' + T_END },

    /* ---------- higienizacja ---------- */
    { id: 'hig-skaling', kat: 'hig', name: 'Skaling', desc: 'Usunięcie kamienia nazębnego.',
      fields: [
        { k: 'rozp', t: 'text', l: 'Rozpoznanie', sug: ['złogi nazębne (K03.6)', 'przewlekłe zapalenie dziąseł (K05.1)', 'przewlekłe zapalenie przyzębia (K05.3)'] },
        { k: 'api', t: 'num', l: 'API (%)', unit: '%' }, { k: 'krw', t: 'text', l: 'Krwawienie (SBI / BOP)' },
        { k: 'zakres', t: 'select', l: 'Zakres', opts: ['szczęka i żuchwa', 'szczęka', 'żuchwa', 'wybrane okolice'] },
        { k: 'zeby', t: 'teeth', l: 'Wybrane zęby / okolice', show: { k: 'zakres', eq: 'wybrane okolice' } }
      ].concat(ZN).concat([
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['skaling ultradźwiękowy naddziąsłowy', 'skaling poddziąsłowy', 'skaling ręczny', 'polerowanie powierzchni zębów', 'fluoryzacja', 'instruktaż higieny jamy ustnej'], def: ['skaling ultradźwiękowy naddziąsłowy'] },
        { k: 'fluor', t: 'text', l: 'Preparat fluorkowy', show: { k: 'czyn', has: 'fluoryzacja' } }
      ]).concat(END(ZAL_HIG)),
      tpl: 'Skaling{?zakres} – {zakres}{/zakres}{?zeby}: {zeby}{/zeby}.\n{?rozp}Rozpoznanie: {rozp}.{/rozp}\n{?api}API {api}%.{/api}{?krw} Krwawienie: {krw}.{/krw}\n' + T_ZN + '\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?fluor}Preparat fluorkowy: {fluor}.{/fluor}\n' + T_END },
    { id: 'hig-piaskowanie', kat: 'hig', name: 'Piaskowanie', desc: 'Usunięcie osadu i przebarwień zewnątrzpochodnych.',
      fields: [
        { k: 'rozp', t: 'text', l: 'Rozpoznanie', sug: ['złogi nazębne / osad (K03.6)', 'przebarwienia zewnątrzpochodne (K03.6)'] },
        { k: 'zakres', t: 'select', l: 'Zakres', opts: ['szczęka i żuchwa', 'szczęka', 'żuchwa', 'wybrane okolice'] },
        { k: 'proszek', t: 'select', l: 'Proszek', opts: ['wodorowęglan sodu', 'glicyna', 'erytrytol'] },
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['piaskowanie', 'polerowanie powierzchni zębów', 'fluoryzacja', 'instruktaż higieny jamy ustnej'], def: ['piaskowanie'] },
        { k: 'fluor', t: 'text', l: 'Preparat fluorkowy', show: { k: 'czyn', has: 'fluoryzacja' } }
      ].concat(END(ZAL_HIG)),
      tpl: 'Piaskowanie{?zakres} – {zakres}{/zakres}{?proszek}, proszek: {proszek}{/proszek}.\n{?rozp}Rozpoznanie: {rozp}.{/rozp}\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?fluor}Preparat fluorkowy: {fluor}.{/fluor}\n' + T_END },
    { id: 'hig-kompleks', kat: 'hig', name: 'Higienizacja kompleksowa', desc: 'Skaling, piaskowanie, polerowanie, fluoryzacja.',
      fields: [
        { k: 'rozp', t: 'text', l: 'Rozpoznanie', sug: ['złogi nazębne (K03.6)', 'przewlekłe zapalenie dziąseł (K05.1)', 'przewlekłe zapalenie przyzębia (K05.3)'] },
        { k: 'api', t: 'num', l: 'API (%)', unit: '%' }, { k: 'krw', t: 'text', l: 'Krwawienie (SBI / BOP)' },
        { k: 'zakres', t: 'select', l: 'Zakres', opts: ['szczęka i żuchwa', 'szczęka', 'żuchwa'] }
      ].concat(ZN).concat([
        { k: 'czyn', t: 'multi', l: 'Przebieg', opts: ['skaling ultradźwiękowy naddziąsłowy', 'skaling poddziąsłowy', 'skaling ręczny', 'piaskowanie', 'polerowanie powierzchni zębów', 'fluoryzacja', 'instruktaż higieny jamy ustnej'], def: ['skaling ultradźwiękowy naddziąsłowy', 'piaskowanie', 'polerowanie powierzchni zębów', 'fluoryzacja'] },
        { k: 'proszek', t: 'select', l: 'Proszek do piaskowania', opts: ['wodorowęglan sodu', 'glicyna', 'erytrytol'], show: { k: 'czyn', has: 'piaskowanie' } },
        { k: 'fluor', t: 'text', l: 'Preparat fluorkowy', show: { k: 'czyn', has: 'fluoryzacja' } }
      ]).concat(END(ZAL_HIG)),
      tpl: 'Higienizacja{?zakres} – {zakres}{/zakres}.\n{?rozp}Rozpoznanie: {rozp}.{/rozp}\n{?api}API {api}%.{/api}{?krw} Krwawienie: {krw}.{/krw}\n' + T_ZN + '\n{?czyn}Przebieg: {czyn}.{/czyn}\n{?proszek}Proszek: {proszek}.{/proszek}\n{?fluor}Preparat fluorkowy: {fluor}.{/fluor}\n' + T_END },

    /* ---------- diagnostyka ---------- */
    { id: 'diag-badanie', kat: 'diag', name: 'Badanie stomatologiczne', desc: 'Pierwsza wizyta: wywiad, badanie, plan leczenia.',
      fields: [
        { k: 'wywiad', t: 'area', l: 'Wywiad ogólny (choroby, leki, alergie)' },
        { k: 'skarg', t: 'text', l: 'Powód zgłoszenia' },
        { k: 'zewn', t: 'text', l: 'Badanie zewnątrzustne' },
        { k: 'wewn', t: 'area', l: 'Badanie wewnątrzustne (błona śluzowa, przyzębie, zgryz)' },
        { k: 'stan', t: 'area', l: 'Stan uzębienia' },
        { k: 'pro', t: 'teeth', l: 'Zęby z próchnicą' }, { k: 'braki', t: 'teeth', l: 'Braki zębowe' },
        { k: 'hig', t: 'select', l: 'Higiena jamy ustnej', opts: ['dobra', 'dostateczna', 'zła'] }, { k: 'api', t: 'num', l: 'API (%)', unit: '%' },
        { k: 'wyk', t: 'multi', l: 'Wykonano', opts: ['zdjęcie pantomograficzne', 'zdjęcie wewnątrzustne', 'CBCT', 'skan wewnątrzustny', 'dokumentacja fotograficzna'] },
        { k: 'zlec', t: 'multi', l: 'Zlecono', opts: ['zdjęcie pantomograficzne', 'zdjęcie wewnątrzustne', 'CBCT', 'konsultację specjalistyczną'] },
        { k: 'rozp', t: 'text', l: 'Rozpoznanie', sug: ['badanie stomatologiczne (Z01.2)'] },
        { k: 'planl', t: 'area', l: 'Plan leczenia' }
      ].concat(END(['instruktaż higieny jamy ustnej'])),
      tpl: 'Badanie stomatologiczne.\n{?skarg}Powód zgłoszenia: {skarg}.{/skarg}\n{?wywiad}Wywiad: {wywiad}.{/wywiad}\n{?zewn}Badanie zewnątrzustne: {zewn}.{/zewn}\n{?wewn}Badanie wewnątrzustne: {wewn}.{/wewn}\n{?stan}Stan uzębienia: {stan}.{/stan}\n{?pro}Zęby z próchnicą: {pro}.{/pro}\n{?braki}Braki zębowe: {braki}.{/braki}\n{?hig}Higiena jamy ustnej: {hig}{?api}, API {api}%{/api}.{/hig}{!hig}{?api}API {api}%.{/api}{/hig}\n{?wyk}Wykonano: {wyk}.{/wyk}\n{?zlec}Zlecono: {zlec}.{/zlec}\n{?rozp}Rozpoznanie: {rozp}.{/rozp}\n{?planl}Plan leczenia: {planl}.{/planl}\n' + T_END },
    { id: 'diag-kontrolna', kat: 'diag', name: 'Wizyta kontrolna', desc: 'Kontrola po leczeniu lub zabiegu.',
      fields: [
        { k: 'cel', t: 'text', l: 'Cel kontroli', req: 1, ph: 'np. kontrola po ekstrakcji 36' },
        { k: 'wywiad', t: 'text', l: 'Dolegliwości od ostatniej wizyty' },
        { k: 'badanie', t: 'area', l: 'Badanie' },
        { k: 'ocena', t: 'select', l: 'Ocena', opts: ['gojenie prawidłowe', 'stan bez zmian', 'poprawa', 'wymaga dalszego leczenia'] },
        { k: 'czyn', t: 'multi', l: 'Wykonano', opts: ['zdjęcie szwów', 'płukanie zębodołu', 'kontrola wypełnienia', 'korekta zwarcia', 'RTG kontrolne'] },
        { k: 'rtg', t: 'text', l: 'Wynik RTG', show: { k: 'czyn', has: 'RTG kontrolne' } }
      ].concat(END([])),
      tpl: 'Wizyta kontrolna: {cel}.\n{?wywiad}Dolegliwości: {wywiad}.{/wywiad}\n{?badanie}Badanie: {badanie}.{/badanie}\n{?ocena}Ocena: {ocena}.{/ocena}\n{?czyn}Wykonano: {czyn}.{/czyn}\n{?rtg}RTG: {rtg}.{/rtg}\n' + T_END },
    { id: 'diag-konsultacja', kat: 'diag', name: 'Konsultacja', desc: 'Konsultacja: wskazania, opcje leczenia, decyzja pacjenta.',
      fields: [
        { k: 'rodzaj', t: 'select', l: 'Rodzaj konsultacji', opts: ['protetyczna', 'implantologiczna', 'chirurgiczna', 'ortodontyczna', 'endodontyczna', 'periodontologiczna', 'ogólnostomatologiczna'] },
        { k: 'skarg', t: 'text', l: 'Powód zgłoszenia', req: 1 },
        { k: 'wywiad', t: 'area', l: 'Wywiad' }, { k: 'badanie', t: 'area', l: 'Badanie' },
        { k: 'wyk', t: 'multi', l: 'Analizowano / wykonano', opts: ['zdjęcie pantomograficzne', 'zdjęcie wewnątrzustne', 'CBCT', 'skan wewnątrzustny', 'dokumentacja fotograficzna'] },
        { k: 'rozp', t: 'text', l: 'Rozpoznanie' },
        { k: 'opcje', t: 'area', l: 'Omówione opcje leczenia, ryzyko, koszty' },
        { k: 'decyzja', t: 'text', l: 'Decyzja pacjenta' }
      ].concat(END([])),
      tpl: 'Konsultacja{?rodzaj} {rodzaj}{/rodzaj}. Powód zgłoszenia: {skarg}.\n{?wywiad}Wywiad: {wywiad}.{/wywiad}\n{?badanie}Badanie: {badanie}.{/badanie}\n{?wyk}Analizowano: {wyk}.{/wyk}\n{?rozp}Rozpoznanie: {rozp}.{/rozp}\n{?opcje}Omówiono z pacjentem: {opcje}.{/opcje}\n{?decyzja}Decyzja pacjenta: {decyzja}.{/decyzja}\n' + T_END }
  ];

  window.PRYW_KATALOG = {
    v: 1,
    kat: [
      { id: 'zach', name: 'Leczenie zachowawcze' }, { id: 'endo', name: 'Endodoncja' }, { id: 'orto', name: 'Ortodoncja' },
      { id: 'chir', name: 'Chirurgia' }, { id: 'hig', name: 'Higienizacja' }, { id: 'diag', name: 'Diagnostyka i konsultacje' }
    ],
    proc: JSON.parse(JSON.stringify(P))
  };
})();
