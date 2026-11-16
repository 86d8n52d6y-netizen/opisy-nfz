# Postęp prac – Generator opisów NFZ

Plik do wznawiania pracy po przerwie (np. po wyczerpaniu limitu). Aktualizowany po każdym etapie.

## Stan na 2026-11-16 (rano)
- `main` = działająca strona na GitHub Pages (commit `e8476e8`, wersja z 17:43) – **bez zmian do czasu scalenia**.
- Gałąź `porzadek-pracy` = rozbudowa aplikacji według specyfikacji „Ewidencja wizyt, punktów, czasu pracy i zarobków” (6 etapów, niżej).
- Pliki: `index.html` (UI, logika, wycena `PTS`, zapis wizyt), `szablony.js` (stałe teksty `SEG`), `testy/` (testy w przeglądarce).

## Zadanie w toku: ewidencja wizyt, punktów, czasu pracy i zarobków

| Etap | Stan | Commit |
|---|---|---|
| 1. Audyt obecnej aplikacji | ✅ zrobione | `2d9ef5e` |
| 2. Plan zmian | ✅ zrobione | `67da90b` |
| 3. Wdrożenie | ✅ zrobione (kod w repo; poprawki po testach w etapach 4–5) | `e168554` |
| 4. Testowanie | ✅ zrobione – 12 plików testów, 256 sprawdzeń, wszystkie OK | `fb535df` (cz. 1), ten commit (cz. 2) |
| 5. Optymalizacja | – | |
| 6. Raport końcowy + scalenie do `main` | – | |

Jak wznowić po przerwie: przeczytaj tę tabelę, `git log --oneline -10`, potem kontynuuj pierwszy etap bez ✅.
Testy: `bash testy/uruchom.sh` (wszystkie) albo `bash testy/uruchom.sh <plik>`; test składni: `bash sprawdz.sh`.

### ETAP 1 – Audyt (wersja z `main`, commit `e8476e8`)

**Budowa.** Dwa pliki statyczne. `index.html` (~106 kB): style, 20 kodów zabiegów w obiekcie `D` (pytania + zdania opisu),
reguły NFZ (`NFZ_MIN`, `NFZ_NOSUM`), wycena punktowa (`PTS`, współczynniki ×1,5 / ×1,2 / ×0,8), kwoty i historia.
`szablony.js`: stałe fragmenty tekstów (`SEG`). Stan w pamięci (`state`), widok budowany od nowa przy zmianach, jedna obsługa kliknięć.

**Dane (localStorage przeglądarki).** `opisyNFZ.price`, `opisyNFZ.pct` – cena punktu i % lekarza; `opisyNFZ.hidx` – lista zapisanych opisów
(inicjały, data, kody, punkty, kwoty); `opisyNFZ.h.<id>` – tekst opisu i odpowiedzi; `opisyNFZ.seg.<skrót>` – stałe fragmenty tekstów.

**Błędy i ryzyka – potwierdzone na działającej wersji** (skrypt `testy/audyt_v9.py`, wyniki z 15.11.2026):

| # | Problem | Dowód | Waga |
|---|---|---|---|
| 1 | Utrata wpisu: po zapisaniu pacjenta JK wpisanie danych kolejnego pacjenta (AB) bez kliknięcia „Nowy pacjent” **nadpisuje** wpis JK | test 1: historia `JK:189,6` → `AB:104`, JK znika | wysoka |
| 2 | Każde wyświetlenie kroku 3 zapisuje wpis od nowa, choć nic się nie zmieniło (2 zapisy na odświeżenie, zmienia się znacznik czasu) | test 2: 5 odświeżeń = 10 zapisów | średnia |
| 3 | Kwoty liczone na ułamkach binarnych – w rzadkich przypadkach błąd o 1 grosz (przy 1,81 zł: 294,5 pkt → 533,04 zł zamiast 533,05 zł; 4 przypadki na 240 tys. sprawdzonych, przy 1,84 zł – 0) | przeszukanie wszystkich sum 0–600 pkt | niska |
| 4 | Kod wpisany jako `23.1101` → komunikat „Brak w bazie: 23” | test 4 | niska |
| 5 | Pojemność localStorage ≈ 1100 wizyt (zmierzone 1129) – za mało na wieloletnią ewidencję i statystyki | pomiar z 15.11 | średnia |
| 6 | Brak kopii zapasowej danych liczbowych i brak odtwarzania (jest tylko eksport opisów do .txt) | przegląd kodu | średnia |

**Działa poprawnie:** wszystkie 20 kodów × 5 wariantów wieku × kroki 1–3 bez błędów JS (test 6); usuwanie wpisu (test 7);
szybkość przy 1000 wpisach (krok 3: ok. 3,5 ms, historia: ok. 7 ms – test 5).

**Czego brakuje względem specyfikacji:** zapis anonimowy i przełącznik zapisu automatycznego, edycja kwot zapisanego wpisu, stawka 1,84 zł
(jest 1,81 zł), godziny przeglądów (350 zł/h), dodatkowe zarobki, czas wizyty i zasada +10 min, statystyki i wykresy, kopia zapasowa.

**Stan prac.** W katalogu roboczym była już niedokończona implementacja z wcześniejszej, przerwanej sesji (nie trafiła do repozytorium).
Została przejrzana w całości, wiersz po wierszu, i przejęta jako baza Etapu 3; do repozytorium wejdzie po przejściu testów podstawowych.

### ETAP 2 – Plan zmian

**Zasada:** rozbudowa istniejącego `index.html`, bez nowej aplikacji i bez kroku budowania; żadna dotychczasowa funkcja nie znika.

**Mapa: wymaganie → rozwiązanie**

| Specyfikacja | Rozwiązanie w aplikacji |
|---|---|
| 1A. Zapis z inicjałami | Jak dotąd: wpis powstaje po wpisaniu inicjałów; dochodzą: dzień tygodnia, punkty, wartość, przeglądy, kwoty dodatkowe, czas, suma |
| 1B. Zapis anonimowy | Przełącznik „zapis automatyczny, bez inicjałów”: każda wygenerowana wizyta zapisuje się sama jako „Anonim #numer” |
| 1C. Przełącznik | Jedno kliknięcie na kroku 1, 3 i w Ustawieniach; zapamiętany w przeglądarce (działa po ponownym uruchomieniu) |
| Pamięć: edycja, usuwanie, brak dubli | „Edytuj kwoty”, „Otwórz i popraw”, „usuń”; zapis tylko gdy coś się zmieniło; blokada nadpisania innego pacjenta |
| 2. 1 pkt = 1,84 zł | Nowa stawka domyślna; szybki wpis samych punktów (bez opisu) w zakładce Historia |
| 3. Dodatkowe zarobki | Wiersze „kwota + opis” przy wizycie (krok 3), w szybkim wpisie i w edycji; osobna kategoria wszędzie |
| 4. Przeglądy 350 zł/h | Pole godzin (ułamki z przecinkiem) przy wizycie, w szybkim wpisie i w edycji; osobna kategoria |
| 5. +10 min | Czas wizyty = czas pakietów higienizacyjnych + 10 min (raz), jeśli jest ekstrakcja lub leczenie zachowawcze; ostrzeżenia NFZ |
| 6A–D. Statystyki | Nowa zakładka: zakres dat, kafelki, tabele Dni / Tygodnie / Miesiące / Dni tygodnia |
| 6E. Wykresy | Słupki dzienne, tygodniowe, miesięczne (wg źródła przychodu), pasek struktury, porównanie dni tygodnia |
| 8.10 Kopia zapasowa | Ustawienia: pobierz kopię .json / wczytaj kopię (scala, niczego nie kasuje); przypomnienie o kopii |

**Konflikty z dotychczasowym działaniem i przyjęte rozstrzygnięcia**

| # | Konflikt / niejasność | Rozstrzygnięcie |
|---|---|---|
| 1 | Stawka 1,81 zł jest zapamiętana w przeglądarce, specyfikacja: 1,84 zł | Przy pierwszym uruchomieniu nowej wersji stawka ustawia się na 1,84 zł (także gdy zapamiętano 1,81). Wpisy zapisane wcześniej zachowują stawkę, z którą powstały. Wybrany % lekarza zostaje |
| 2 | Specyfikacja: 100 pkt = 184 zł „zarobku”; aplikacja ma już udział lekarza 40% / 35% | Nic nie usuwam. Przy wizycie widać obie kwoty. W statystykach przełącznik: „pełna wartość punktów” (domyślnie – tak jak w przykładach ze specyfikacji) albo „udział lekarza (%)”. Przeglądy i kwoty dodatkowe zawsze w całości |
| 3 | localStorage mieści ok. 1100 wizyt | Wpisy i opisy w IndexedDB tej samej przeglądarki (bez limitu 5 MB), stara historia przenosi się sama; gdy IndexedDB nie działa – zapis awaryjny w localStorage. Dane nadal nie opuszczają urządzenia |
| 4 | Dotychczas: jedna wizyta = jeden wpis nadpisywany przy każdej zmianie (błąd 1 z audytu) | Zostaje „jedna wizyta = jeden wpis do »Następny pacjent«”, ale zapis jest wstrzymywany i aplikacja pyta, gdy formularz wygląda na innego pacjenta: inne inicjały, inny wiek, zamienione zabiegi albo inne API i GI |
| 5 | Zaokrąglenia (błąd 3) | Wszystkie kwoty liczone w groszach na liczbach całkowitych, połówki w górę |
| 6 | Co jest „pakietem higienizacyjnym” i „procedurą zachowawczą” | Pakiety: ST30, ST30E, ST30G. Doliczenie +10 min wywołują: ST01, ST02 (ekstrakcje) oraz 1105, 1108, 1206, 1502–1505 (grupa „Leczenie zachowawcze” w aplikacji). Nie wywołują: 1101, 1006 (profilaktyka), ST19, ST04, ST26, badania |
| 7 | Do jakiego czasu doliczać 10 min | Do **czasu wizyty**: standardowe 30 min + 10 = 40 min; gdy same pakiety zajmują więcej niż 30 min (czas z opisu, nie mniej niż minimum NFZ) – czas pakietów + 10 (np. ST30 ×4: 40 + 10 = 50 min). Pole „Czas wizyty” pozwala wpisać własną wartość. *(Zmienione w Etapie 4: pierwsza wersja doliczała 10 min do czasu pakietu z opisu, co dawało 21 + 10 = 31 min i zasada prawie nic nie zmieniała.)* |
| 8 | Wpis z samymi przeglądami lub kwotą dodatkową | Nie liczy się jako wizyta pacjenta (nie zawyża liczby wizyt ani średniej na wizytę), ale wchodzi do zarobku i czasu pracy |
| 9 | „Dzień przepracowany”, „tydzień” | Dzień przepracowany = dzień z co najmniej jednym wpisem; tydzień = poniedziałek–niedziela; średnia na dzień kalendarzowy nie liczy dni z przyszłości |
| 10 | Kopia zapasowa a istniejące dane | Wczytanie kopii scala: dodaje brakujące wpisy, istniejący zastępuje tylko nowszą wersją; ten sam plik przenosi dane między urządzeniami |

**Pliki:** zmienia się `index.html` (cała logika), opisy w `README.md` i `CLAUDE.md`; `szablony.js` bez zmian. Testy w `testy/`.

### ETAP 3 – Wdrożenie

Cała logika w `index.html` (z 106 kB do ok. 190 kB), `szablony.js` bez zmian. Co doszło:

| Obszar | Co zrobiono | Gdzie w kodzie |
|---|---|---|
| Magazyn danych | IndexedDB (`visits`, `bodies`, `segs`) + awaryjnie localStorage + pamięć tymczasowa; przeniesienie starej historii; prośba o trwałe przechowywanie | sekcja „magazyn danych”, `dbInit`, `migrateV1` |
| Ustawienia | jeden klucz `opisyNFZ.cfg`: stawka 1,84, przeglądy 350, % lekarza, tryb zapisu, podstawa statystyk | sekcja „ustawienia (localStorage)” |
| Kwoty | liczone w groszach (`centsPts`, `centsPct`, `centsHours`, `calc`) | sekcja „liczby i kwoty” |
| Zapis wizyty | `autoSave`: tryb z inicjałami / automatyczny, zapis tylko przy zmianie, pytanie przy podejrzeniu innego pacjenta | sekcja „zapis wizyty z generatora” |
| Rozliczenie wizyty | czas wizyty (+10 min), godziny przeglądów, dodatkowe zarobki | `visitTime`, `settleHTML` |
| Historia | podsumowanie dnia, szybki wpis, edycja kwot, usuwanie, wyszukiwanie | sekcje „formularz wpisu”, „historia wizyt” |
| Statystyki | zakres dat, kafelki, Dni / Tygodnie / Miesiące / Dni tygodnia, wykresy SVG | sekcja „statystyki” |
| Kopia zapasowa | eksport i scalające wczytanie pliku .json | sekcja „kopia zapasowa” |
| Poprawki z audytu | błędy 1–6 z Etapu 1 | – |

Sprawdzone przed tym commitem: `bash sprawdz.sh`, `testy/t0_dym.py` (9/9), `testy/t1_obliczenia.py` (25/25). Pełne testy – Etap 4.

### ETAP 4 – Testowanie

Testy działają na prawdziwej aplikacji w przeglądarce Chrome (bez okna): klikają i wpisują jak użytkownik, a wyniki porównują
z niezależnym liczeniem w Pythonie (ułamki dziesiętne `Decimal`, kalendarz `datetime`). Uruchomienie: `bash testy/uruchom.sh`.

| Test | Co sprawdza | Wynik |
|---|---|---|
| `t0_dym.py` | przejście przez wszystkie widoki, zapis pierwszej wizyty | 9/9 |
| `t1_obliczenia.py` | przykłady ze specyfikacji (100 pkt = 184 zł … 0,5 h = 175 zł), 10 tys. losowych przeliczeń, zaokrąglenia, parsowanie liczb, 3000 dat (tydzień ISO, dzień tygodnia) | 25/25 |
| `t2_zapis.py` | tryb z inicjałami i automatyczny, brak dubli i zbędnych zapisów, pytanie zamiast nadpisania (inne inicjały / wiek / zabiegi / API+GI), ponowne uruchomienie, usunięcie i edycja wpisu bieżącej wizyty | 38/38 |
| `t3_czas.py` | zasada +10 min (1 ząb, kilka zębów, kilka procedur – zawsze raz), które kody ją wywołują, limity NFZ, czas ręczny, zapis czasu we wpisie | 23/23 |
| `t4_wpisy.py` | szybki wpis (punkty / przeglądy / kwota), 10 rodzajów błędnych danych, edycja kwot i stawek wpisu, anulowanie, usuwanie, wyszukiwanie, sumy po każdej zmianie | 27/27 |
| `t5_statystyki.py` | 1060 wpisów z 13 miesięcy: kafelki i wszystkie tabele (Dni, Tygodnie, Miesiące, Dni tygodnia) dla 11 zakresów i obu podstaw; suma dni = tygodni = miesięcy; wpisy anonimowe; edycja i usunięcie; wykresy | 27/27 |
| `t6_migracja.py` | przeniesienie historii z wersji z `main` (prawdziwa stara wersja w tej samej przeglądarce): wpisy ze stawkami 1,81 / 1,90 zł i 40 / 35%, wpis bez treści opisu, uszkodzony indeks; teksty opisów co do znaku, kwoty co do grosza, numery, stare klucze kasowane dopiero po sprawdzeniu, „Otwórz i popraw”, przeliczenie po nowych stawkach | 17/17 |
| `t7_kopia.py` | pobranie kopii .json, utrata danych → odtworzenie 1:1, ponowne wczytanie bez dubli, starsza kopia nie cofa nowszej poprawki, nowe urządzenie (wpisy + ustawienia), zderzenie numerów, pliki uszkodzone / obce / częściowo błędne, opisy do .txt | 18/18 |
| `t8_magazyn.py` | brak IndexedDB → pamięć zapasowa (localStorage) i powrót do głównej bazy bez dubli; baza, która nie odpowiada; cała pamięć zablokowana; błąd zapisu (brak miejsca) z ponowieniem; dwie karty naraz (wpisy, numery, stawki) | 19/19 |
| `t9_regresja.py` | 684 scenariusze (każdy kod × 10 wariantów wieku, 8 planów wizyt, 400 losowych zestawów z wypełnianiem pól i diagramu zębów): opis, punkty, błędy NFZ i liczba braków identyczne jak w wersji z `main` (5,2 mln znaków); różnią się tylko komunikaty o czasie wizyty (nowa zasada +10 min) | 14/14 |
| `t10_bezpieczenstwo.py` | plik kopii z kodem HTML/JS w każdym polu (inicjały, opisy, 61 pól formularza, kody, zęby, ustawienia) – w 17 widokach nic się nie wykonuje; wpis z uszkodzonymi odpowiedziami nie zawiesza strony | 17/17 |
| `t11_wyglad_wydajnosc.py` | 5000 wpisów (czasy niżej); wygląd: telefon 320 i 390 px, tablet, komputer, jasny i ciemny motyw – nic nie wystaje poza ekran, przyciski ≥ 24 px; zrzuty ekranu w `testy/zrzuty/` (poza repo) | 22/22 |

**Wydajność przy 5000 wpisów (T11):**

| Czynność | Czas |
|---|---|
| Uruchomienie aplikacji | 0,5 s |
| Historia (40 najnowszych) / wyszukiwanie | 40 ms / 17 ms |
| Statystyki „Wszystko”, zakładka Dni (725 dni) / „Ten miesiąc” | 290 ms / 11 ms |
| Szybki wpis (od Enter do zapisu) | 53 ms |
| Kopia zapasowa (plik 4,8 MB) / wczytanie na pustym urządzeniu | 0,24 s / 0,5 s |
| Zajętość bazy przeglądarki | ok. 2,5 MB |

**Poprawki wprowadzone w trakcie testów (część 1):**
1. Zasada +10 min liczona od czasu wizyty (30 → 40 min), a nie od czasu pakietu z opisu (było 21 + 10 = 31 min).
2. Statystyki, pola „Od–Do”: zmieniane pole wygrywa, drugie się dopasowuje (wcześniej daty zamieniały się miejscami i zakres wychodził inny niż wpisany).
3. Dni kalendarzowe w zakresie sięgającym w przyszłość liczone do ostatniego wpisu (nie tylko do dziś).
4. Skrypt `testy/uruchom.sh` bez argumentów uruchamia wszystkie testy.

**Poprawki wprowadzone w trakcie testów (część 2):**
1. Historia: gdy wpis ma inną stawkę niż obecna, widać ją przy kwocie („286,8 pkt × 1,81 zł”) – T6.
2. Wczytywana kopia: godziny przeglądów w jednym wpisie najwyżej 24 h, tak jak w formularzach (wcześniej plik mógł wnieść do 1000 h) – T7.
3. Dwie karty przeglądarki: zmiana stawek / trybu zapisu w jednej karcie dociera do drugiej (wcześniej karty mogły nadpisać sobie ustawienia); licznik numerów wpisów nie cofa się; po powrocie do karty zdublowane numery są naprawiane – T8.
4. „Otwórz i popraw” wpisu z pliku kopii z uszkodzonymi odpowiedziami (np. tekst zamiast listy) zawieszało stronę – teraz odpowiedzi z pliku są czyszczone (tylko tekst, liczby i listy), a wpis, którego nie da się wyświetlić, daje komunikat; opis i kwoty zostają w Historii – T10.
5. Błąd przy rysowaniu dowolnego widoku pokazuje kartę z komunikatem i przyciskiem „Wyczyść formularz i wróć do początku” zamiast pustej strony – T10.
6. Dłuższe komunikaty na dole ekranu zostają proporcjonalnie dłużej (2,2–7 s).
7. Przyciski „usuń”, „brak”, „×” przy kodach mają co najmniej 24 × 24 px (WCAG 2.2, kryterium 2.5.8) – wygodniej na telefonie – T11.
8. Ustawienia, opis kopii zapasowej: dopisano, że wpis usunięty w aplikacji wróci po wczytaniu kopii, która go zawiera.

## Zrobione wcześniej
- [x] Szablony: pacjent poniżej i powyżej 5 r.ż., plany wizyt I–IV
- [x] Wycena punktowa (zarz. 95/2026/DSOZ, 44/2025/DSOZ), kwota i udział lekarza 40%/35%
- [x] Historia opisów w przeglądarce + kopia .txt
- [x] Organizacja pracy: `POSTEP.md`, `CLAUDE.md`, `sprawdz.sh`

## Dziennik
| Data | Gałąź | Co zrobiono |
|---|---|---|
| 2026-11-15 | `porzadek-pracy` | Dodano plik postępu, zasady pracy i test składni |
| 2026-11-15 | `porzadek-pracy` | ETAP 1: audyt wersji z `main` – 6 potwierdzonych problemów (w tym nadpisywanie wpisu), skrypt `testy/audyt_v9.py` |
| 2026-11-15 | `porzadek-pracy` | ETAP 2: plan zmian – mapa wymagań i 10 rozstrzygnięć konfliktów z dotychczasowym działaniem |
| 2026-11-15 | `porzadek-pracy` | ETAP 3: wdrożenie w `index.html` – ewidencja wizyt, dwa tryby zapisu, przeglądy, kwoty dodatkowe, +10 min, statystyki, kopia zapasowa |
| 2026-11-16 | `porzadek-pracy` | ETAP 4, część 1: testy T0–T5 (149 sprawdzeń, wszystkie OK), 3 poprawki w aplikacji |
| 2026-11-16 | `porzadek-pracy` | ETAP 4, część 2: testy T6–T11 – razem 12 plików, 256 sprawdzeń, wszystkie OK; 8 poprawek w aplikacji |
