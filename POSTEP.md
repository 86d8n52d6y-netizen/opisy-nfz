# Postęp prac – Generator opisów NFZ

Plik do wznawiania pracy po przerwie (np. po wyczerpaniu limitu). Aktualizowany po każdym etapie.

## Stan na 2026-11-15 (wieczór)
- `main` = działająca strona na GitHub Pages (commit `e8476e8`, wersja z 17:43) – **bez zmian do czasu scalenia**.
- Gałąź `porzadek-pracy` = rozbudowa aplikacji według specyfikacji „Ewidencja wizyt, punktów, czasu pracy i zarobków” (6 etapów, niżej).
- Pliki: `index.html` (UI, logika, wycena `PTS`, zapis wizyt), `szablony.js` (stałe teksty `SEG`), `testy/` (testy w przeglądarce).

## Zadanie w toku: ewidencja wizyt, punktów, czasu pracy i zarobków

| Etap | Stan | Commit |
|---|---|---|
| 1. Audyt obecnej aplikacji | ✅ zrobione | `2d9ef5e` |
| 2. Plan zmian | ✅ zrobione | `67da90b` |
| 3. Wdrożenie | ✅ zrobione (kod w repo; poprawki po testach w etapach 4–5) | ten commit |
| 4. Testowanie | ⏳ następny | |
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
| 7 | Do jakiego czasu doliczać 10 min | Do czasu pakietów wpisanego w opisie (nie mniej niż minimum NFZ); wizyta nie krótsza niż standardowe 30 min; pole „Czas wizyty” pozwala wpisać własną wartość |
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
