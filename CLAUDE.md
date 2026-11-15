# Zasady pracy w tym repo

- Komunikacja po polsku.
- `main` = działająca strona na GitHub Pages. Zmiany rób na osobnej gałęzi, do `main` scalaj dopiero po teście.
- Pracuj etapami. Po każdym etapie: `bash sprawdz.sh` → commit → push gałęzi → aktualizacja `POSTEP.md`.
- Po przerwie (np. limit użycia) zacznij od przeczytania `POSTEP.md` i `git log --oneline -10`.
- Aplikacja jest statyczna (bez serwera i bez kroku build). Wizyty i opisy zostają tylko w przeglądarce (baza IndexedDB, awaryjnie localStorage; ustawienia w localStorage) – nie dodawaj wysyłania danych pacjentów na zewnątrz.
- Stawki rozliczeń: 1,84 zł za punkt, 350 zł za godzinę przeglądów, +10 min przy pakiecie higienizacyjnym z ekstrakcją lub leczeniem zachowawczym – nie zmieniaj bez decyzji Patryka.
- Przed scaleniem do `main`: `bash testy/uruchom.sh` (testy w przeglądarce) musi przejść bez błędów.
- W `szablony.js` uważaj na cudzysłowy i przecinki – błąd składni zatrzymuje całą aplikację.
- Stawki punktowe są w obiekcie `PTS` w `index.html`; podawaj źródło (numer zarządzenia DSOZ) przy każdej zmianie.
