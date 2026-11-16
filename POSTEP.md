# Postęp prac – Generator opisów NFZ

Plik do wznawiania pracy po przerwie (np. po wyczerpaniu limitu). Aktualizowany po każdym etapie.

## Stan na 2026-11-16 (9:40)
- `main` = `porzadek-pracy` = nowa wersja (ewidencja wizyt, statystyki, kopia zapasowa) – scalona po przejściu wszystkich testów; działa na GitHub Pages (sprawdzone 16.11.2026 ok. 9:35: nowa wersja, baza IndexedDB, 1,84 zł/pkt, 350 zł/h, generator opisów bez błędów).
- Poprzednia wersja strony: commit `e8476e8` (jej historię nowa wersja przenosi sama przy pierwszym otwarciu).
- Kopia aplikacji w Claude (artefakt) – ta sama wersja (wersja artefaktu `1794818108-906e`).
- Pliki: `index.html` (UI, logika, wycena `PTS`, zapis wizyt), `szablony.js` (stałe teksty `SEG`), `testy/` (testy w przeglądarce).

## Zadanie w toku: połączenie aplikacji – Kalendarz + Opisy NFZ + Opisy prywatne (gałąź `polaczenie`)

Specyfikacja: prompt „Rozbudowa i połączenie aplikacji gabinetu stomatologicznego” (16.11.2026). Szczegóły, decyzje Patryka i projekt: `POLACZENIE.md`.
Druga aplikacja (Grafik Gabinetów) pochodzi z repo `86d8n52d6y-netizen/grafik-gabinetow`, commit `cb9df0c`.

| Etap | Stan | Commit |
|---|---|---|
| 1. Analiza obu aplikacji | ✅ zrobione | `3eeda9b` |
| 2. Przepisy o dokumentacji medycznej | ✅ zrobione | `368161b` |
| 3. Projekt struktury i danych | ✅ zrobione | `368161b` |
| 4. Szkielet, użytkownicy i szyfrowanie, oba moduły w nowej strukturze | ✅ zrobione – 13 plików testów, 302 sprawdzenia, wszystkie OK | `e290020` |
| 5. Moduł Opisy prywatne | ✅ zrobione – 14 plików testów, 351 sprawdzeń, wszystkie OK | `9258ed6` |
| 6. Edycja szablonów, zestawy, ulubione, szybka wizyta | ✅ zrobione – 16 plików testów, 423 sprawdzenia, wszystkie OK | `99b58c9` + ten commit |
| 7. Połączenia modułów, eksport, testy całości, raport, scalenie | – | |

Jak wznowić: przeczytaj tę tabelę i `POLACZENIE.md`, potem `git log --oneline -10` na gałęzi `polaczenie`.

Stan po ETAPIE 4 (co już działa na gałęzi):
- `index.html` – zakładanie konta (hasło + kod odzyskiwania), logowanie, odzyskiwanie hasła, kafelki, okno „Zarobki – wszystkie gabinety”, konto (blokada, zmiana hasła, nowy kod, usunięcie konta).
- `wspolne.js` – użytkownicy, szyfrowanie AES-GCM, sesja z blokadą po bezczynności, pasek modułów, magazyn `G.store`, szyfrująca warstwa `G.wrapBE`, szkice, sumy dzienne, gabinety z Kalendarza, przeniesienie danych z poprzednich wersji.
- `nfz.html` – dawny `index.html` Opisów NFZ: ten sam mechanizm, dane szyfrowane, pole „Gabinet” przy wizycie (domyślnie z dyżuru), szkic wizyty przy przełączaniu modułów (starszy niż 12 h – pomijany), sumy dzienne dla strony głównej.
- `kalendarz.html` – dawny Grafik Gabinetów: dane szyfrowane w `gabinet@<id>`, sumy przychodu z dyżurów dla strony głównej, uchwyt `window.Kal` dla testów.
- Testy: nowy `t12_sejf.py` (35 sprawdzeń), T2/T6/T8 dostosowane do logowania i baz per użytkownik.

Stan po ETAPIE 5:
- `prywatne.html` + `prywatne-katalog.js` – wizyta z wieloma procedurami, silnik szablonów (`{pole}`, `{?pole}…{/pole}`, `{!pole}…{/pole}`, `[UZUPEŁNIJ]`), 19 procedur, cennik dla każdego gabinetu (domyślny % / własny % / kwota, koszty przed %), edycja tekstu, historia z wyszukiwaniem w treści, „Użyj jako szablonu”, zarobki (okresy, gabinety, rodzaje zabiegu), usuwanie treści starych opisów, szkic przy przełączaniu modułów, sumy dla strony głównej (`suma:pryw`).
- Test `t13_prywatne.py` (49 sprawdzeń, w tym 300 przypadków wynagrodzenia z wyrocznią Decimal).
- Założenia do potwierdzenia przez Patryka: „szyna bierna / aktywna” rozumiane szeroko (rodzaj do wpisania); „Procedury” w zarobkach liczone z ilością; domyślny % gabinetu pusty, dopóki go nie ustawi.

Do zapamiętania na etap 7: stara strona Grafiku (`/grafik-gabinetow/`) leży w tej samej domenie – po przeniesieniu jej dane znikają z niej; przed scaleniem zapytać Patryka o przekierowanie starej strony; rozważyć ponowne wykrywanie danych starych wersji przy logowaniu (gdy ktoś jeszcze korzysta ze starej strony).

## Zadanie: ewidencja wizyt, punktów, czasu pracy i zarobków (zakończone 16.11.2026)

| Etap | Stan | Commit |
|---|---|---|
| 1. Audyt obecnej aplikacji | ✅ zrobione | `2d9ef5e` |
| 2. Plan zmian | ✅ zrobione | `67da90b` |
| 3. Wdrożenie | ✅ zrobione (kod w repo; poprawki po testach w etapach 4–5) | `e168554` |
| 4. Testowanie | ✅ zrobione – 12 plików testów, 256 sprawdzeń, wszystkie OK | `fb535df` (cz. 1), `2db157e` (cz. 2) |
| 5. Optymalizacja | ✅ zrobione – 3 poprawki po przeglądzie zrzutów ekranu; testy: 264 sprawdzenia, wszystkie OK | `88d615f` |
| 6. Raport końcowy + scalenie do `main` | ✅ raport; scalono do `main` (fast-forward), strona na żywo i artefakt sprawdzone | `5767cd5` |

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
| `t5_statystyki.py` | 1060 wpisów z 13 miesięcy: kafelki i wszystkie tabele (Dni, Tygodnie, Miesiące, Dni tygodnia) dla 11 zakresów i obu podstaw; suma dni = tygodni = miesięcy; wpisy anonimowe; edycja i usunięcie; wykresy (od ETAPU 5 także luki w ewidencji i kolejność kolumn) | 27/27 → 35/35 po ETAPIE 5 |
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

### ETAP 5 – Optymalizacja (po testach i przeglądzie zrzutów ekranu)

Przejrzane zrzuty: telefon 320 / 390 px, tablet, komputer, jasny i ciemny motyw (`testy/zrzuty/`, poza repo). Zmiany – każda z uzasadnieniem:

| Zmiana | Dlaczego | Jak sprawdzone |
|---|---|---|
| Wykres tygodniowy i miesięczny: ciągła oś czasu – tydzień / miesiąc bez wpisów to słupek 0 zł („brak wpisów” w podpowiedzi). Bez zer sprzed pierwszego wpisu w historii (brak danych ≠ brak zarobku) i bez okresów z przyszłości; pusty, niepełny okres na początku zakresu pominięty | miesiąc bez wpisów (np. urlop) znikał z osi – po „sie 2026” od razu „lis 2026”; wykres sugerował ciągłość, której nie było | T5: wyrocznia liczby słupków w Pythonie + 6 nowych sprawdzeń (luka w marcu, tydzień 1 z wpisem i bez, nowa ewidencja od marca, „12 mies.” = „Wszystko”) |
| Tabele: „Razem” zaraz po nazwie okresu; w Miesiącach zaraz potem obie średnie (na dzień pracy / kalendarzowy) | na komputerze 4 ostatnie kolumny tabeli miesięcy – w tym obie średnie wymagane w specyfikacji – były poza kartą; na telefonie widać było tylko datę i liczbę wizyt | T5: tabele czytane po nagłówkach (wyniki niezależne od kolejności) + osobne sprawdzenie kolejności |
| Tabele szersze niż ekran: przyklejona pierwsza kolumna i cień przy prawej krawędzi, dopóki są dalsze kolumny | nic nie wskazywało, że tabelę da się przewinąć w bok, a przy przewijaniu znikała nazwa wiersza | zrzuty ekranu (telefon, komputer, ciemny motyw); T11 – nic nie wystaje poza ekran |

Rozważone i niewprowadzone: ciągła oś na wykresie dziennym – co 3.–4. słupek byłby zerem za weekend, a tytuł wykresu mówi „dni z wpisami”; wolne dni widać w tabeli dni i w kafelku „dni przepracowane na N kalendarzowych”.

Ograniczenie testów: automatyczne testy działają w Chrome. Silnika Safari (WebKit) nie dało się pobrać w tym środowisku (sieć blokuje serwer pobierania), więc zgodność z iPhone'em sprawdziłem tylko przeglądem kodu: brak składni wymagającej nowszego Safari (`?.`, `??`, `.at()`, `Object.hasOwn`, `structuredClone`, `replaceAll`), funkcje pamięci przeglądarki są w blokach z obsługą błędu, a `color-mix` (cień tabeli) w starszej przeglądarce po prostu się nie pokaże.

### ETAP 6 – Raport końcowy

**1. Co jest nowego (względem wersji z `main`, commit `e8476e8`)**

| Specyfikacja | Stan w aplikacji |
|---|---|
| 1. Zapis wizyt | Tryb **z inicjałami** (jak dotąd) i **automatyczny / anonimowy** – przełącznik na krokach 1 i 3 oraz w Ustawieniach, pamiętany po restarcie. Wpis: inicjały lub „Anonim”, numer, data, dzień tygodnia, kody, punkty, stawka, kwota, % lekarza, przeglądy, kwoty dodatkowe, czas wizyty, suma. Jedna wizyta = jeden wpis; zapis tylko po zmianie; pytanie zamiast nadpisania, gdy formularz wygląda na innego pacjenta. Edycja kwot, „Otwórz i popraw”, usuwanie; szybki wpis bez opisu |
| 2. Punkty | 1 pkt = **1,84 zł** (zmiana w Ustawieniach); każdy wpis pamięta swoją stawkę; kwoty w groszach, połówki w górę |
| 3. Dodatkowe zarobki | Dowolna liczba pozycji „kwota + opis” przy wizycie, w szybkim wpisie i w edycji; osobna kategoria w statystykach |
| 4. Przeglądy | **350 zł/h**, ułamki godzin (0,5 h = 175 zł), osobno od punktów, edytowalne |
| 5. +10 min | Pakiet higienizacyjny (ST30, ST30E, ST30G) + ekstrakcja (ST01, ST02) lub leczenie zachowawcze (1105, 1108, 1206, 1502–1505) → +10 min do czasu wizyty, **raz na wizytę** |
| 6. Statystyki | Zakresy (dziś … wszystko, dowolne od–do), kafelki (w tym średnia na dzień pracy i kalendarzowy), struktura przychodów, zakładki Dni / Tygodnie / Miesiące (zmiana do poprzedniego miesiąca) / Dni tygodnia (najlepszy dzień, średnie, tabela miesiąc × dzień), wykresy |
| 8. Dane | IndexedDB (awaryjnie localStorage, w ostateczności pamięć karty z ostrzeżeniem); stara historia przenosi się sama; kopia zapasowa .json z odtwarzaniem i scalaniem; przypomnienie o kopii |

**2. Naprawione błędy** – 6 z audytu (nadpisywanie wpisu poprzedniego pacjenta, zbędne zapisy, błąd 1 gr w zaokrągleniach, kod „23.1101”, pojemność ≈ 1100 wizyt, brak kopii danych liczbowych) oraz 14 znalezionych w testach i przeglądzie wyglądu (lista w ETAPACH 4 i 5).

**3. Wyniki testów** – `bash testy/uruchom.sh`, Chrome bez okna, 16.11.2026: **12 plików, 264 sprawdzenia, 0 błędów** (T0 9, T1 25, T2 38, T3 23, T4 27, T5 35, T6 17, T7 18, T8 19, T9 14, T10 17, T11 22).

**4. Ograniczenia techniczne**
- Dane są tylko w tej przeglądarce na tym urządzeniu; nic nie synchronizuje się samo (przenoszenie = kopia .json).
- Safari usuwa IndexedDB i localStorage strony po 7 dniach używania Safari bez wejścia na tę stronę; aplikacja dodana do ekranu początkowego ma własny licznik dni (źródło: WebKit, „Full Third-Party Cookie Blocking and More”, 2020). Prośba o trwałe przechowywanie (`navigator.storage.persist`) bywa w Safari odrzucana (WebKit, zgłoszenie 271401) – stąd przypomnienie o kopii.
- Wczytanie kopii scala dane: wpis usunięty w aplikacji wróci, jeśli jest w pliku.
- Przeniesienie starej historii jest jednokierunkowe: po pierwszym otwarciu nowej wersji wersja z `e8476e8` (gdyby ją przywrócić) nie pokaże historii – dane są w nowej bazie.
- Wpisy przeniesione ze starej wersji nie mają czasu wizyty – kafelek „Czas wizyt” pokazuje ich liczbę („N wizyt bez wpisanego czasu”); czas uzupełnia się (30 min) przy „Otwórz i popraw”.
- Testy automatyczne tylko w Chrome (silnik Safari niedostępny w środowisku testowym) – zgodność z Safari sprawdzona przeglądem kodu.
- Kopia aplikacji w Claude (artefakt) to inna domena – ma osobne dane.

**5. Założenia do potwierdzenia** (każde da się zmienić bez utraty danych)

| # | Założenie | Gdzie zmienić |
|---|---|---|
| 1 | +10 min doliczane do czasu wizyty (30 → 40 min), raz na wizytę; wywołują je ekstrakcje ST01, ST02 i 1105, 1108, 1206, 1502–1505; nie wywołują 1101, 1006, ST19, ST04, ST26 | kod (`HYG_EXTRA`) |
| 2 | Nowe wpisy po 1,84 zł; wpisy sprzed zmiany zostają po 1,81 zł | „Przelicz po aktualnych stawkach” przy wpisie |
| 3 | „Zarobek z punktów” w statystykach domyślnie = pełna wartość punktów | przełącznik w Statystykach / Ustawieniach |
| 4 | Wpis z samymi przeglądami lub kwotą dodatkową nie jest wizytą (liczy się do zarobku i dni pracy) | kod (`isVisit`) |
| 5 | Szybki wpis wizyty bez wpisanego czasu = 30 min | pole „Czas wizyty” |
| 6 | Tydzień = poniedziałek–niedziela (ISO); dzień przepracowany = dzień z co najmniej jednym wpisem | kod |

**6. Propozycje (niewdrożone – czekają na decyzję)**

| Propozycja | Uzasadnienie | Nakład |
|---|---|---|
| Pole „gabinet” przy wpisie: własny % lekarza dla gabinetu, statystyki i zestawienie miesięczne per gabinet | przy pracy w kilku miejscach z różnym udziałem przełącznik 40/35% jest dziś wspólny dla wszystkich wpisów – łatwo zapisać wizytę z niewłaściwym %; zestawienie per gabinet ułatwia sprawdzenie rozliczenia | średni |
| Instalacja na ekranie początkowym (manifest + praca bez internetu, czcionki w repo zamiast z Google Fonts) | na iPhonie aplikacja z ekranu początkowego nie podlega 7-dniowemu licznikowi Safari, tylko własnemu; działa bez sieci w gabinecie | mały–średni (do sprawdzenia na Twoim iPhonie: przeniesienie danych kopią .json) |
| Eksport zestawienia (miesiące / dni) do pliku CSV dla Excela | rozliczenie z gabinetem lub księgowość bez przepisywania; kopia .json nie jest do czytania w Excelu | mały |

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
| 2026-11-16 | `porzadek-pracy` | ETAP 5: ciągła oś wykresów tygodniowego i miesięcznego, kolejność kolumn tabel, przyklejona kolumna i cień przewijania; testy: 264 sprawdzenia, wszystkie OK |
| 2026-11-16 | `porzadek-pracy` | ETAP 6: raport końcowy (zmiany, błędy, testy, ograniczenia, założenia, propozycje) |
| 2026-11-16 | `main` | Scalenie `porzadek-pracy` → `main` (fast-forward do `5767cd5`) po 264 sprawdzeniach bez błędów; strona na żywo sprawdzona w przeglądarce; artefakt w Claude zaktualizowany |
| 2026-11-16 | `polaczenie` | Połączenie aplikacji – ETAP 1: analiza obu aplikacji, co zachować / połączyć / poprawić, 12 problemów integracji z rozwiązaniami (`POLACZENIE.md`) |
| 2026-11-16 | `polaczenie` | ETAP 2: przepisy (ustawa o prawach pacjenta, rozporządzenie o dokumentacji – t.j. Dz.U. 2026 poz. 1391, art. 34 u.z.l., NFZ, ZUS, RODO) i 10 wniosków dla szablonów; ETAP 3: projekt plików, sejfu, danych, połączeń i modułu prywatnego |
| 2026-11-16 | `polaczenie` | ETAP 4: strona główna i konta z szyfrowaniem (`index.html`, `wspolne.js/css`), Opisy NFZ → `nfz.html`, Grafik → `kalendarz.html`, przeniesienie starych danych, pasek modułów, szkice, okno Zarobki; nowy test T12; 13 plików testów, 302 sprawdzenia, wszystkie OK |
| 2026-11-16 | `polaczenie` | ETAP 5: moduł Opisy prywatne (`prywatne.html`, `prywatne-katalog.js`) – 19 procedur, cenniki gabinetów, wynagrodzenie, historia, zarobki, prywatność; poprawka: kliknięcie „Zapisz” tuż po wpisaniu pola nie ginie; test T13; razem 14 plików, 351 sprawdzeń, wszystkie OK |
| 2026-11-16 | `polaczenie` | ETAP 6, cz. 1: Opisy prywatne – edytor szablonów (pola, kody, warunki, tekst, podgląd, wersje i przywracanie, własne procedury, duplikat, ukrywanie), migawka szablonu w zapisanej wizycie, ulubione, zestawy (przeciąganie, ceny wg cennika), tryb szybkiej wizyty; test T14 (42 sprawdzenia) |
| 2026-11-16 | `polaczenie` | ETAP 6, cz. 2: Opisy NFZ – edycja gotowego tekstu przed zapisem (zapis, kopiowanie, szkic, otwarcie z historii), ulubione i ukryte kody, własne zestawy kodów (zasady NFZ bez zmian), edytor stałych tekstów z szablony.js z wersjami; poprawki wyglądu na telefonie; test T15; razem 16 plików, 423 sprawdzenia OK. Nie zrobiono: własne (nowe) procedury NFZ z ręcznymi punktami – do decyzji Patryka |
| 2026-11-16 | `polaczenie` | ETAP 7: podpowiedź w dyżurze Kalendarza (sumy z Opisów NFZ i prywatnych → „Wpisz jako obrót”, koszty → lab), CSV i druk w Zarobkach prywatnych, kopia całości (zaszyfrowana hasłem, scalanie bez dubli), sumy dnia zapisywane od razu przy zapisie i wyjściu z modułu; test T16; razem 17 plików, 439 sprawdzeń OK |
| 2026-11-16 | `polaczenie` | Decyzja Patryka: najpierw podgląd (artefakt Claude „Gabinet – podgląd połączonej aplikacji”, osobne dane; pobieranie plików w podglądzie nie działa), scalenie do `main` dopiero po jego teście; stara strona Grafiku zostaje bez zmian (bez przekierowania) |
