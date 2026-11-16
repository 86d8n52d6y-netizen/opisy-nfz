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
