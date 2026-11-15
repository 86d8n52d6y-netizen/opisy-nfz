# Zasady pracy w tym repo

- Komunikacja po polsku.
- `main` = działająca strona na GitHub Pages. Zmiany rób na osobnej gałęzi, do `main` scalaj dopiero po teście.
- Pracuj etapami. Po każdym etapie: `bash sprawdz.sh` → commit → push gałęzi → aktualizacja `POSTEP.md`.
- Po przerwie (np. limit użycia) zacznij od przeczytania `POSTEP.md` i `git log --oneline -10`.
- Aplikacja jest statyczna (bez serwera i bez kroku build). Historia opisów zostaje tylko w localStorage przeglądarki – nie dodawaj wysyłania danych pacjentów na zewnątrz.
- W `szablony.js` uważaj na cudzysłowy i przecinki – błąd składni zatrzymuje całą aplikację.
- Stawki punktowe są w obiekcie `PTS` w `index.html`; podawaj źródło (numer zarządzenia DSOZ) przy każdej zmianie.
