# Postęp prac – Generator opisów NFZ

Plik do wznawiania pracy po przerwie (np. po wyczerpaniu limitu). Aktualizowany po każdym etapie.

## Stan na 2026-11-15
- Aplikacja działa na GitHub Pages z gałęzi `main`.
- Pliki: `index.html` (UI, logika, wycena `PTS`, historia w localStorage), `szablony.js` (stałe teksty `SEG`).
- Składnia obu plików sprawdzona (`bash sprawdz.sh`) – OK.

## Zrobione
- [x] Szablony: pacjent poniżej i powyżej 5 r.ż., plany wizyt I–IV
- [x] Wycena punktowa (zarz. 95/2026/DSOZ, 44/2025/DSOZ), kwota i udział lekarza 40%/35%
- [x] Historia opisów w przeglądarce + kopia .txt
- [x] Organizacja pracy: `POSTEP.md`, `CLAUDE.md`, `sprawdz.sh`

## W toku
- (brak)

## Następne (do ustalenia z Patrykiem)
- [ ] …

## Dziennik
| Data | Gałąź | Co zrobiono |
|---|---|---|
| 2026-11-15 | `porzadek-pracy` | Dodano plik postępu, zasady pracy i test składni |
