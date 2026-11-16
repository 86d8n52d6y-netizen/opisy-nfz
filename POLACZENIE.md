# Połączenie aplikacji: Kalendarz + Opisy NFZ + Opisy prywatne

Dokument projektu (gałąź `polaczenie`). Specyfikacja: „PROMPT – rozbudowa i połączenie aplikacji gabinetu stomatologicznego” (16.11.2026).
Postęp prac: `POSTEP.md`.

## Decyzje Patryka (16.11.2026)

| Pytanie | Decyzja |
|---|---|
| Gdzie działa połączona aplikacja | repo `opisy-nfz`, adres `…/opisy-nfz/` zostaje; praca na gałęzi `polaczenie`, na `main` po testach |
| Cennik prywatny i % lekarza | osobno dla każdego gabinetu; osobne okno z sumą zarobków ze wszystkich gabinetów |
| Ochrona danych | hasło i szyfrowanie; każdy użytkownik ma własne hasło i dostęp tylko do własnych danych |
| Kalendarz a wizyty | podpowiedź w dyżurze: suma wizyt z dnia (NFZ i prywatne osobno), przeniesienie do obrotu jednym kliknięciem |

---

## ETAP 1 – Analiza obu aplikacji

### 1.1. Generator opisów NFZ (`index.html` + `szablony.js`, commit `5f54bd8`)

| Obszar | Funkcje |
|---|---|
| Generator | 20 kodów (pakiety ST…, świadczenia jednostkowe 1101…1505), plany wizyt I–IV (poniżej i powyżej 5 r.ż.), wpisywanie kodów z klawiatury; krok 2: pytania do każdego kodu, diagram zębów FDI z powierzchniami, ćwiartki; krok 3: pełny opis, kopiowanie całości i pojedynczych kodów |
| Zasady NFZ | minimalne czasy pakietów, kody niełączone, wymagane znieczulenie, komunikaty o częstotliwości – błędy i ostrzeżenia na bieżąco |
| Wycena | punkty wg zarządzeń DSOZ (95/2026, 44/2025) ze współczynnikami ×1,5 / ×1,2 / ×0,8; 1 pkt = 1,84 zł; udział lekarza 40% / 35% |
| Rozliczenie wizyty | przeglądy 350 zł/h, dodatkowe zarobki (kwota + opis), czas wizyty z zasadą +10 min |
| Zapis | tryb z inicjałami i automatyczny (anonimowy); jedna wizyta = jeden wpis; ochrona przed nadpisaniem innego pacjenta |
| Historia | wyszukiwanie, „Otwórz i popraw”, edycja kwot, usuwanie, szybki wpis bez opisu, opisy do .txt, kasowanie starych tekstów |
| Statystyki | zakresy dat, kafelki, struktura przychodu, Dni / Tygodnie / Miesiące / Dni tygodnia z wykresami |
| Dane | IndexedDB `opisyNFZ` (wpisy, opisy, fragmenty tekstów), ustawienia w localStorage `opisyNFZ.cfg`; kopia .json; przenoszenie historii ze starszej wersji |
| Testy | 12 plików, 264 sprawdzenia (`testy/`) |

### 1.2. Grafik Gabinetów (`grafik-gabinetow`, commit `cb9df0c`, 21.10.2026)

| Obszar | Funkcje |
|---|---|
| Gabinety | nazwa, skrót, kolor, adres; model rozliczenia: % po odjęciu labu, % z udziałem labu, % od obrotu, stawka godzinowa, dzienna, kwota; minimum za dzień; termin wypłaty |
| Grafik | zmiany (rano / popołudnie / własne), stały grafik dzień × zmiana (co tydzień / co 2 tyg.), automatyczne wpisywanie dyżurów na 1–12 mies., dni wolne (urlop, L4), święta, kolizje, dodawanie wielu dni naraz |
| Widoki | rok, miesiące i tygodnie przewijane w dół, lista do szybkiego wpisywania obrotu i labu, panel dnia i edytor dyżuru |
| Dyżur | status zaplanowany / odbyty / odwołany, obrót, lab, kwota, korekta kwoty |
| Podsumowanie | netto miesiąca, rozbicie (przychód, ZUS, zdrowotna, podatek, koszty), tabela gabinetów (obrót, lab, udział, zł/h), wykres i tabela roku, kursy, punkty edukacyjne, ostrzeżenia |
| Podatki i ZUS | skala 12/32%, liniowy, ryczałt; okresy ZUS (własna kwota, preferencyjny, Mały ZUS Plus, pełny), wakacje składkowe, zdrowotna, parametry roczne 2026/2027 (część oznaczona jako szacunek), dochód z etatu |
| Pozostałe zakładki | Rozliczenia (wyliczenie gabinetu ↔ własny zapis), Terminy (ZUS, PIT, roczne), Porównaj formy, Ustawienia |
| Kursy | nazwa, miejsce, typ, daty, godziny, koszt (do kosztów firmowych), punkty edukacyjne |
| Eksport | .ics (Apple / Google, z przypomnieniami i terminami), CSV dyżurów i miesięcy, kopia .json i jej wczytanie |
| Dane | localStorage `grafik-gabinetow-v1` (ustawienia + miesiące), preferencje widoku `grafik-ui`; w wersji z Claude – chmura Claude |
| Inne | tryb „Zobacz przykład” bez zapisu, „Pierwsze kroki”, manifest i ikony do ekranu początkowego |
| Testy | brak w repozytorium (w październiku testowane skryptami poza repo) |

### 1.3. Co zachować, połączyć, poprawić

| Element | Decyzja | Uzasadnienie |
|---|---|---|
| Mechanizm generatora NFZ (kody, pytania, diagram, zasady NFZ, punkty, teksty) | **zachować bez zmian** | działa i jest pokryty testami (684 scenariusze identyczne ze starą wersją) |
| Widoki, automatyczny grafik, podatki, terminy, kursy, eksport kalendarza | **zachować** | pełne, sprawdzone w październiku |
| Gabinety | **połączyć** – jedno źródło: gabinety z Kalendarza; z nich korzystają Opisy NFZ (przypisanie wizyty) i Opisy prywatne (cennik i % per gabinet) | dziś Opisy NFZ nie wiedzą, w którym gabinecie była wizyta |
| Zapis danych | **połączyć** – jedna zaszyfrowana przestrzeń na użytkownika dla wszystkich modułów | wymóg: hasło, szyfrowanie, dostęp tylko do własnych danych |
| Kopia zapasowa | **połączyć** – jedna „kopia całości” (zaszyfrowana); wczytywanie starych kopii obu aplikacji zostaje | dziś dwa osobne pliki .json |
| Nawigacja i wygląd | **połączyć** – wspólny górny pasek modułów, wspólne kolory, czcionki i przyciski | dwie różne stylistyki |
| Zarobki | **rozdzielić czytelnie**: NFZ (punkty), prywatne (cennik), dyżury (rozliczenie gabinetu) – osobno; okno sumy ze wszystkich gabinetów | wymóg: nie łączyć NFZ i prywatnych w jeden przychód; uniknąć liczenia dwa razy |
| Opis NFZ | **poprawić** – edycja gotowego tekstu przed zapisem, edytowalne stałe fragmenty z wersjami, własne zestawy obok planów I–IV, ulubione | wymóg 3 i 5 specyfikacji |
| Tryb chmury Claude w grafiku | **wyłączyć w wersji połączonej** | dane muszą być zaszyfrowane per użytkownik; chmura Claude nie działa na GitHub Pages |

### 1.4. Problemy z połączeniem i rozwiązania

| # | Problem | Rozwiązanie |
|---|---|---|
| 1 | Oba programy mają globalne nazwy (`render`, `state`, `esc`, `toast`…) i style o tych samych klasach – w jednej stronie by się nadpisały | osobna strona na moduł (`nfz.html`, `kalendarz.html`, `prywatne.html`) + wspólne pliki `wspolne.js` / `wspolne.css`; strona główna `index.html` |
| 2 | Przejście do innego modułu przeładowuje stronę – niezapisany formularz by zniknął | szkic bieżącej wizyty zapisywany na bieżąco (zaszyfrowany) i odtwarzany po powrocie |
| 3 | Szyfrowanie jest asynchroniczne, a oba programy zapisują synchronicznie | NFZ: warstwa szyfrująca w istniejącym `DB.be` (zapis już jest asynchroniczny); Kalendarz: szyfrowanie całego zbioru przy zapisie (zapis już jest opóźniany o 0,65 s) |
| 4 | Klucz szyfrujący musi przetrwać przejście między stronami, ale nie może leżeć jawnie | klucz niewyciągalny (`CryptoKey`, nieeksportowalny) w sesji IndexedDB z limitem bezczynności; blokada = przeładowanie strony (dane znikają z pamięci) |
| 5 | Stare dane są jawne (IndexedDB `opisyNFZ`, localStorage `grafik-gabinetow-v1`) | przy pierwszym uruchomieniu: pierwszy użytkownik przejmuje stare dane, są szyfrowane i sprawdzane, dopiero potem kasowane wersje jawne |
| 6 | Stara strona `…/grafik-gabinetow/` (ten sam adres przeglądarki) po przeniesieniu danych pokazałaby pusty kalendarz | po akceptacji: zamienić ją na przekierowanie do nowego Kalendarza |
| 7 | Wizyty NFZ nie mają gabinetu | nowe pole `gabinet` (domyślnie gabinet z dyżuru danego dnia); stare wpisy bez gabinetu liczą się w „nieprzypisane” |
| 8 | Ten sam zarobek mógłby być liczony w Kalendarzu (obrót) i w wizytach | Kalendarz tylko podpowiada sumę wizyt; przeniesienie do obrotu – świadomie, jednym kliknięciem |
| 9 | Teksty NFZ są częściowo kodem (logika zdań) | edytowalne są stałe fragmenty (`szablony.js`) i własne procedury; logika zdań bez zmian |
| 10 | Zmiana szablonu nie może zmienić zapisanych opisów | wizyta zapisuje gotowy tekst (już tak jest w NFZ); szablony mają historię wersji |
| 11 | Testy NFZ zakładają brak logowania | wspólny pomocnik testów loguje użytkownika testowego; nowe testy dla Kalendarza i modułu prywatnego |
| 12 | Kopie aplikacji w Claude (artefakty) mają inne adresy i własne dane | poza połączeniem; zostają bez zmian |

---

## ETAP 2 – Przepisy: co jest wymogiem prawnym, co wymogiem NFZ / ZUS, a co dobrą praktyką

Stan prawny sprawdzony 16.11.2026. To zestawienie robocze do projektowania szablonów – **nie jest opinią prawną** i nie przesądza o zgodności konkretnego wpisu z przepisami. Ostateczna treść wpisu należy do lekarza.

### 2.1. Co mówią przepisy

| Źródło | Co wynika (skrót) | Kogo dotyczy |
|---|---|---|
| Ustawa o prawach pacjenta i RPP (t.j. Dz.U. 2024 poz. 581), **art. 25 ust. 1** | dokumentacja zawiera co najmniej: oznaczenie pacjenta (imię i nazwisko, data urodzenia, płeć, adres, PESEL…), oznaczenie podmiotu z komórką organizacyjną, **opis stanu zdrowia lub udzielonych świadczeń**, **datę sporządzenia** | każde świadczenie – NFZ i prywatne |
| ta sama ustawa, **art. 29 ust. 1** | podmiot przechowuje dokumentację **20 lat** od końca roku ostatniego wpisu (wyjątki: 30 lat, 22 lata, RTG 10 lat) | podmiot leczniczy (gabinet) |
| Rozporządzenie MZ w sprawie rodzajów, zakresu i wzorów dokumentacji medycznej (t.j. **Dz.U. 2026 poz. 1391**), **§ 1** | dokumentację prowadzi podmiot, w postaci elektronicznej | gabinet (system EDM) |
| to samo, **§ 4** | wpis **niezwłocznie po udzieleniu świadczenia**, chronologicznie; wpis i jego zmiana oznaczone osobą, która ich dokonała; podpis (kwalifikowany, zaufany, osobisty, ZUS lub mechanizm systemu); błędnego wpisu nie usuwa się | każdy wpis |
| to samo, **§ 10 pkt 3** | oznaczenie osoby udzielającej świadczenia: imię i nazwisko, tytuł zawodowy, numer prawa wykonywania zawodu, podpis | każdy wpis |
| to samo, **§ 38 ust. 4** (historia zdrowia i choroby w opiece ambulatoryjnej) | przy każdej poradzie: **data**, **wywiad i badanie przedmiotowe**, **rozpoznanie**, zlecone badania i konsultacje, zalecone zabiegi oraz leki (z dawkowaniem i numerami e-recept), wyniki badań i konsultacji, **opis innych udzielonych świadczeń**, adnotacja o zleceniu transportu, **adnotacja o orzeczonej czasowej niezdolności do pracy**, oznaczenie osoby udzielającej świadczeń | wizyta w gabinecie – NFZ i prywatna |
| to samo – przepisy o stomatologii | w przejrzanej części rozporządzenia (do § 68a) **diagram zębowy** występuje tylko w wykazie pracowni protetycznej i ortodontycznej (§ 48 ust. 2 pkt 4); brak odrębnego wzoru wpisu stomatologicznego | – |
| Ustawa o zawodach lekarza i lekarza dentysty (t.j. Dz.U. 2026 poz. 37), **art. 34 ust. 1** | **zabieg operacyjny** albo metoda o **podwyższonym ryzyku** – po uzyskaniu **pisemnej zgody** pacjenta; ocena ryzyka jest medyczna i dotyczy konkretnego pacjenta | np. ekstrakcje, zwłaszcza zęba zatrzymanego |
| ta sama ustawa, **art. 31 ust. 3** | okoliczności ograniczenia informacji lekarz odnotowuje w dokumentacji | wyjątkowe sytuacje |
| NFZ: ogólne warunki umów (rozporządzenie MZ z 8.09.2015) + zarządzenie Prezesa NFZ dla leczenia stomatologicznego | świadczenie sprawozdane do NFZ musi wynikać z dokumentacji; w kontroli NFZ świadczenia „niezasadnie sprawozdane” podlegają zwrotowi, a za uchybienia nakłada się kary umowne | **tylko świadczenia NFZ** |
| ZUS: ustawa zasiłkowa, **art. 59**; rozporządzenie o dokumentacji § 38 ust. 4 pkt 10 | prawidłowość orzekania o niezdolności do pracy kontrolują lekarze orzecznicy ZUS; ZUS może odebrać uprawnienie do wystawiania zwolnień m.in. przy zwolnieniu **bez udokumentowania rozpoznania**; w dokumentacji – adnotacja o zwolnieniu | **tylko gdy wystawiasz e-ZLA** |
| RODO: **art. 9** (dane o zdrowiu – szczególna kategoria; podstawa w opiece zdrowotnej: art. 9 ust. 2 lit. h + tajemnica zawodowa), **art. 5 ust. 1 lit. c i f**, **art. 32** (bezpieczeństwo przetwarzania) | minimalizacja danych, poufność i integralność, środki techniczne (np. szyfrowanie) | każdy, kto zapisuje dane pacjentów – także ta aplikacja |

### 2.2. Wnioski dla aplikacji

| # | Wniosek | Rodzaj | Jak to uwzględniam |
|---|---|---|---|
| 1 | Aplikacja **przygotowuje propozycję wpisu**; dokumentacją medyczną jest wpis w systemie gabinetu (EDM), który dodaje dane pacjenta, podmiotu, autora, podpis i datę oraz przechowuje go 20 lat | prawny | w aplikacji nie ma pól na imię i nazwisko ani PESEL – tylko inicjały (opcjonalnie); dopisek o autorze jest opcjonalny |
| 2 | Wpis „niezwłocznie po świadczeniu”, z datą | prawny (§ 4, § 38) | data wizyty uzupełnia się sama; opis powstaje w trakcie wizyty |
| 3 | Treść porady: wywiad i badanie, rozpoznanie, opis świadczeń, zalecenia i leki, zlecone badania, ewentualne zwolnienie | prawny (§ 38 ust. 4) | szablony prywatne mają te pola; puste pole nie trafia do opisu albo jest oznaczone [UZUPEŁNIJ], jeśli jest wymagane |
| 4 | **Żadnych dopisanych automatycznie czynności, których nie było** | prawny (rzetelność dokumentacji) + wymóg specyfikacji | każde zdanie o czynności powstaje z elementu, który lekarz widzi i może odznaczyć; elementy dodatkowe są domyślnie odznaczone |
| 5 | Zabieg operacyjny / podwyższone ryzyko → pisemna zgoda | prawny (art. 34), ale **zastosowanie zależy od oceny lekarza** | w szablonach chirurgicznych pole „Zgoda pisemna pacjenta: uzyskana” – do zaznaczenia; aplikacja nie wystawia formularza zgody |
| 6 | Zasady NFZ (punkty, łączenie, częstotliwość) | **tylko NFZ** | wyłącznie w module NFZ; moduł prywatny ich nie stosuje i nie pokazuje punktów |
| 7 | Adnotacja o e-ZLA | **tylko ZUS, gdy wystawiono zwolnienie** | pole opcjonalne „Wystawiono zwolnienie lekarskie (e-ZLA): od–do” |
| 8 | Numer zęba wg FDI, diagram, materiały i ich partie, opis powikłań lub ich braku, plan leczenia | **dobra praktyka** (nie wymóg rozporządzenia) | pola w szablonach; brak powikłań wpisuje się tylko po zaznaczeniu |
| 9 | Dane o zdrowiu w przeglądarce = przetwarzanie danych szczególnej kategorii | RODO | szyfrowanie per użytkownik, hasło, blokada po bezczynności, same inicjały, opcja automatycznego kasowania treści opisów po ustalonym czasie (kwoty zostają) |
| 10 | Kopie opisów poza systemem gabinetu | **do sprawdzenia z gabinetem / IOD** – administratorem danych pacjentów jest zwykle podmiot leczniczy | aplikacja działa także bez zapisywania treści opisów (tylko kwoty); w raporcie zaznaczam, że tego nie da się rozstrzygnąć technicznie |

### 2.3. Źródła
- Ustawa o prawach pacjenta i RPP, art. 25 i 29 – https://arslege.pl/ustawa-o-prawach-pacjenta-i-rzeczniku-praw-pacjenta/k478/s5709/ , https://nil.org.pl/articleToPdf/4263 , RPP: https://www.gov.pl/web/rpp/dostep-do-dokumentacji-medycznej-likwidacja-placowki-medycznej-smierc-lekarza-czas-przechowywania
- Rozporządzenie MZ o dokumentacji medycznej, tekst jednolity Dz.U. 2026 poz. 1391 – https://api.sejm.gov.pl/eli/acts/DU/2026/1391/text/O/D20261391.pdf
- Ustawa o zawodach lekarza i lekarza dentysty, art. 34 – https://lexlege.pl/ustawa-o-zawodach-lekarza-i-lekarza-dentysty/art-34/ ; art. 31 ust. 3 – https://arslege.pl/ustawa-o-zawodach-lekarza-i-lekarza-dentysty/k607/s5724/
- NFZ, wynik kontroli (zwrot za świadczenia niezasadnie sprawozdane, kara umowna) – https://nfz.gov.pl/download/gfx/nfz/pl/defaultaktualnosci/631/292/1/kontrola_nr_15.7310.191.2018.wkon-lo.pdf
- ZUS, kontrola zwolnień (art. 59 ustawy zasiłkowej) – https://www.prawo.pl/zdrowie/kiedy-lekarz-traci-uprawnienia-do-wystawiania-zwolnien-lekarskich,520450.html , https://www.zus.pl/eZLA
- RODO a dane o zdrowiu (art. 9 ust. 2 lit. h, art. 32) – UODO: https://uodo.gov.pl/pl/file/6384

---

## ETAP 3 – Projekt struktury

### 3.1. Pliki (statyczna strona, bez kroku budowania)

| Plik | Rola |
|---|---|
| `index.html` | strona główna: logowanie / nowy użytkownik / kod odzyskiwania; trzy duże kafelki (Kalendarz, Opisy NFZ, Opisy prywatne); okno **Zarobki** (suma ze wszystkich gabinetów, NFZ i prywatne w osobnych kolumnach); kopia całości; konto (hasło, blokada) |
| `nfz.html` | Opisy NFZ – dotychczasowy `index.html`; mechanizm generatora bez zmian |
| `szablony.js` | stałe teksty NFZ (bez zmian; poprawki użytkownika zapisywane w jego danych) |
| `kalendarz.html` | Kalendarz – dotychczasowy Grafik Gabinetów |
| `prywatne.html` | Opisy prywatne – nowy moduł |
| `prywatne-katalog.js` | domyślny katalog procedur prywatnych: kategorie, pola, szablony tekstu, przykładowy zestaw |
| `wspolne.js` | sejf (użytkownicy, klucze, szyfrowanie, sesja, blokada), pasek modułów, wspólne dane (gabinety, sumy dzienne wizyt), szkice, kopia całości |
| `wspolne.css` | wspólne kolory, czcionki, pasek modułów, ekran logowania |
| `manifest.webmanifest`, ikony | z Grafiku (ikona na ekranie początkowym) |

Każdy moduł to osobna strona → brak konfliktów nazw i stylów między programami. Górny pasek (wspólny) prowadzi bezpośrednio do pozostałych modułów i do strony głównej. Stare adresy: `…/opisy-nfz/` = strona główna; generator NFZ: `…/opisy-nfz/nfz.html`.

### 3.2. Użytkownicy, hasła, szyfrowanie

| Element | Rozwiązanie |
|---|---|
| Użytkownik | imię / nazwa, własne hasło, własna przestrzeń danych we wszystkich modułach (gabinety, grafik, wizyty, cenniki, zestawy, szablony, statystyki) |
| Klucz danych | losowy klucz AES-GCM 256 bit na użytkownika; zapisany tylko w postaci zaszyfrowanej: kluczem z hasła (PBKDF2-SHA-256, 600 000 iteracji, losowa sól) i osobno kluczem z kodu odzyskiwania |
| Kod odzyskiwania | pokazywany raz przy zakładaniu konta (24 znaki w grupach); pozwala ustawić nowe hasło; bez hasła i bez kodu danych nie da się odczytać – świadomie |
| Rekordy | każdy zapis szyfrowany osobno (AES-GCM, losowy IV, nazwa rekordu jako dane uwierzytelniające); na dysku: `v1:<iv>:<szyfrogram>` |
| Sesja | po zalogowaniu klucz jako **niewyciągalny** `CryptoKey` w IndexedDB `gabinet-sesja` z czasem ostatniej aktywności; każda strona modułu wznawia sesję bez hasła, dopóki nie minie limit bezczynności (domyślnie 15 min, do ustawienia) |
| Blokada | po bezczynności lub ręcznie: moduł zapisuje szkic, sesja jest kasowana, strona przechodzi do logowania (dane znikają z pamięci); po zalogowaniu powrót do tego samego modułu i szkicu |
| Izolacja | dane użytkownika A są w osobnych bazach (`opisyNFZ@A`, `gabinet@A`) i zaszyfrowane jego kluczem – użytkownik B ich nie odczyta, także narzędziami przeglądarki |

### 3.3. Gdzie leżą dane (na użytkownika `u`)

| Dane | Miejsce | Szyfrowane |
|---|---|---|
| lista użytkowników (nazwy, sole, zaszyfrowane klucze) | localStorage `gabinet.users` | klucze – tak |
| Opisy NFZ: wpisy, treści, fragmenty | IndexedDB `opisyNFZ@u` (te same magazyny co dziś) | tak – warstwa w `DB.be` |
| Opisy NFZ: ustawienia (stawki, tryb zapisu) | localStorage `opisyNFZ@u.cfg` | nie (bez danych pacjentów) |
| Kalendarz (ustawienia, gabinety, miesiące, kursy) | IndexedDB `gabinet@u`, rekord `grafik` | tak |
| Opisy prywatne: katalog i jego wersje, cenniki, zestawy, ulubione, ustawienia | IndexedDB `gabinet@u`, magazyn `kv` | tak |
| Opisy prywatne: wizyty i treści | IndexedDB `gabinet@u`, magazyny `wizyty`, `opisy` | tak |
| sumy dzienne wizyt (data → gabinet → liczba, wartość, zarobek) – NFZ i prywatne osobno | `gabinet@u`, rekordy `suma:nfz`, `suma:pryw` | tak |
| szkice niezapisanych formularzy | `gabinet@u`, magazyn `szkice` | tak |

### 3.4. Połączenia między modułami

| Połączenie | Jak działa |
|---|---|
| Gabinety | jedno źródło: gabinety z Kalendarza; Opisy NFZ i prywatne pobierają listę z niego |
| Gabinet wizyty | domyślnie gabinet z dyżuru danego dnia (gdy dyżurów jest kilka – ten, którego godziny obejmują teraz); zawsze do zmiany |
| Podpowiedź obrotu | moduły po każdej zmianie zapisują **sumy dzienne**; edytor dyżuru w Kalendarzu pokazuje: NFZ (wartość punktów), prywatne (wartość zabiegów) i przycisk „Wpisz jako obrót” |
| Okno Zarobki (strona główna) | z sum dziennych: wiersze = gabinety + „bez gabinetu”, kolumny NFZ (udział lekarza), prywatne (wynagrodzenie lekarza), razem z wizyt; osobno – przychód z dyżurów wg rozliczeń Kalendarza (do porównania, nie dodawany) |
| Kopia całości | jeden plik z zaszyfrowanymi danymi wszystkich modułów i zaszyfrowanym kluczem; odtworzenie wymaga hasła lub kodu odzyskiwania |

### 3.5. Moduł Opisy prywatne

| Element | Projekt |
|---|---|
| Procedura | nazwa, kategoria, pola (tekst, liczba, wybór, wielokrotny wybór, zęby FDI, ząb, tak/nie, data), szablon tekstu, historia wersji, ulubiona, ukryta |
| Szablon tekstu | `{pole}` – wartość; `{?pole}…{/pole}` – fragment tylko gdy pole wypełnione; `{!pole}…{/pole}` – gdy puste; pole wymagane i puste → `[UZUPEŁNIJ: …]`; czynności jako pole wielokrotnego wyboru: domyślnie zaznaczone tylko kroki, które są istotą procedury |
| Cennik | dla każdego gabinetu: cena, wynagrodzenie lekarza **%** albo **kwota**; domyślny % gabinetu; przy wizycie cenę i wynagrodzenie można zmienić; ilość (np. kilka zębów) |
| Wizyta | gabinet, data, inicjały (opcjonalnie), procedury i zestawy (ulubione, wyszukiwarka, kategorie), formularz każdej procedury, kolejność, suma wartości i wynagrodzenia, wspólny opis, „Edytuj tekst”, „Kopiuj opis”, „Zapisz wizytę”, szkic zapisywany na bieżąco |
| Tryb szybkiej wizyty | widać tylko pola wymagane; zestaw albo ulubione jednym kliknięciem; kopiuj + zapisz |
| Historia | wyszukiwanie (inicjały, procedura, tekst), filtr gabinetu i rodzaju zabiegu, otwórz, „użyj jako szablonu” (nowa wizyta z tymi procedurami i wartościami), kopiuj, usuń |
| Zarobki | dzień / tydzień / miesiąc / zakres; tabela gabinetów i suma; liczba wizyt i procedur; średnie wynagrodzenie na wizytę; zarobki według rodzaju zabiegu; filtr rodzaju; CSV i wydruk (PDF) |
| Zestawy | nazwa, kategoria, lista procedur (przeciąganie, dodaj / usuń), ulubiony, wyszukiwanie, duplikat; wybór zestawu dodaje jego procedury do wizyty – dalej w pełni edytowalne |
| Zapis | wizyta przechowuje gotowy tekst i wartości z chwili zapisu – zmiana szablonu, cennika lub zestawu nie zmienia zapisanych wizyt |

### 3.6. Zmiany w Opisach NFZ (mechanizm generatora bez zmian)

| Zmiana | Szczegóły |
|---|---|
| Logowanie i szyfrowanie | baza `opisyNFZ@u`, warstwa szyfrująca w `DB.be`; reszta kodu bez zmian |
| Gabinet przy wizycie | nowe pole `gab` w wpisie (stare wpisy: „bez gabinetu”) |
| Edycja gotowego tekstu | „Edytuj tekst” na kroku 3; zapisany tekst ma znacznik „edytowany ręcznie”; zmiana formularza nie nadpisuje go bez pytania |
| Edytowalne stałe teksty | edytor fragmentów z `szablony.js` z historią wersji i przywracaniem domyślnego |
| Zestawy NFZ | własne zestawy kodów obok planów I–IV; zasady NFZ sprawdzane jak dziś |
| Ulubione i ukryte kody | gwiazdka przy kodzie; kody ukryte znikają z listy, nie z bazy |
| Własne procedury NFZ | edytor jak w module prywatnym + kod i punkty wpisane ręcznie, wyraźnie oznaczone jako niesprawdzane przez zasady NFZ |

### 3.7. Przeniesienie dotychczasowych danych

Przy zakładaniu **pierwszego** użytkownika aplikacja wykrywa stare dane (IndexedDB `opisyNFZ`, localStorage `opisyNFZ.*` i `grafik-gabinetow-v1`), szyfruje je do przestrzeni tego użytkownika, **sprawdza** (liczba rekordów, odczyt próbny) i dopiero potem kasuje wersje jawne. Po akceptacji strona `…/grafik-gabinetow/` dostanie przekierowanie do nowego Kalendarza.

### 3.8. Kolejność budowy i testy

| Etap | Zakres | Testy |
|---|---|---|
| 4 | `wspolne.js/css`, strona główna z logowaniem, NFZ i Kalendarz w nowej strukturze, przeniesienie danych | dotychczasowe 264 sprawdzenia (po zalogowaniu) + sejf (hasła, kod odzyskiwania, blokada, izolacja użytkowników, szyfrogram na dysku) + Kalendarz (zapis, odczyt) + nawigacja |
| 5 | moduł prywatny z katalogiem 19 procedur, cenniki, wizyta, historia, zarobki | wyliczenia (Decimal), łączenie procedur, cenniki per gabinet, sumy dzienne |
| 6 | edytor szablonów (NFZ i prywatne), wersje, zestawy, ulubione, szybka wizyta | szablon zmieniony ≠ zmiana zapisanej wizyty; przywracanie wersji; zestawy |
| 7 | podpowiedź obrotu, okno Zarobki, eksport CSV / wydruk, kopia całości, testy całości, wygląd komputer / tablet, raport, scalenie | pełny zestaw |

---

## ETAP 5 – Opisy prywatne: decyzje przy wdrożeniu

| Kwestia | Rozstrzygnięcie | Dlaczego |
|---|---|---|
| Czynności w opisie | pola wielokrotnego wyboru; domyślnie zaznaczona tylko istota zabiegu (np. „opracowanie ubytku”, „usunięcie zęba”, „piaskowanie”) | wniosek 4 z etapu 2 – brak czynności dopisanych samoczynnie |
| „Bez powikłań”, zgoda, zalecenia, znieczulenie | zawsze puste na starcie | j.w.; zgoda pisemna (art. 34 u.z.l.) – decyzja lekarza |
| Pola zależne | np. środek i dawka znieczulenia widoczne dopiero po wyborze rodzaju (nie przy „nie stosowano”); szwy – po zaznaczeniu „szycie”; pole ukryte nie trafia do opisu | opis nie może zawierać danych z pól, których nie widać |
| Kody ICD-10 | tylko jako podpowiedzi w polu „Rozpoznanie” (pole tekstowe), wg WHO; do sprawdzenia ze słownikiem systemu gabinetu | rozpoznanie stawia lekarz; polskie wydanie i słowniki systemów mogą się różnić |
| Szyna bierna / aktywna | rodzaj szyny wpisywany (podpowiedzi: relaksacyjna, ochronna, stabilizacyjna / nakładki, repozycyjna) | w specyfikacji nie doprecyzowano – do potwierdzenia |
| Wynagrodzenie | % od (cena × ilość − koszty) albo stała kwota × ilość; koszty > wartość → 0; połówki grosza w górę | model rozliczenia Patryka (% obrotu po odjęciu kosztów laboratorium i implantów) |
| Cennik | osobny dla każdego gabinetu + „bez gabinetu”; procedura bez ceny – ostrzeżenie, nie zero „po cichu” | decyzja Patryka: „każdy ma swój cennik” |
| Zapisana wizyta | przechowuje tekst, pola, ceny i nazwy procedur z chwili zapisu | zmiana cennika lub szablonu nie zmienia historii |
| Treść opisów | opcjonalne automatyczne usuwanie po 30–365 dniach (kwoty zostają) | RODO – minimalizacja, wniosek 9–10 z etapu 2 |
