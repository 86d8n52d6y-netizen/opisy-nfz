# Postęp prac – Generator opisów NFZ

Plik do wznawiania pracy po przerwie (np. po wyczerpaniu limitu). Aktualizowany po każdym etapie.

## Stan na 2026-11-15 (wieczór)
- `main` = działająca strona na GitHub Pages (commit `e8476e8`, wersja z 17:43) – **bez zmian do czasu scalenia**.
- Gałąź `porzadek-pracy` = rozbudowa aplikacji według specyfikacji „Ewidencja wizyt, punktów, czasu pracy i zarobków” (6 etapów, niżej).
- Pliki: `index.html` (UI, logika, wycena `PTS`, zapis wizyt), `szablony.js` (stałe teksty `SEG`), `testy/` (testy w przeglądarce).

## Zadanie w toku: ewidencja wizyt, punktów, czasu pracy i zarobków

| Etap | Stan | Commit |
|---|---|---|
| 1. Audyt obecnej aplikacji | ✅ zrobione | ten commit |
| 2. Plan zmian | ⏳ następny | |
| 3. Wdrożenie | – | |
| 4. Testowanie | – | |
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
