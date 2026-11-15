# Generator opisów zabiegów NFZ

Aplikacja do generowania opisów do dokumentacji (wizyta 30 min) na podstawie szablonów gabinetu – pacjent poniżej i powyżej 5 r.ż. (w tym ST30E i szablony wizyt I–IV).

**Jak działa:** wiek pacjenta i kody zabiegów → pytania i diagram zębów (zęby, ćwiartki, powierzchnie) → gotowy opis z przyciskiem „Kopiuj cały opis”. Niewypełnione miejsca zostają jako `[UZUPEŁNIJ: …]`. Aplikacja niczego nie zapisuje.

## Pliki
| Plik | Co zawiera |
|---|---|
| `index.html` | wygląd, pytania, diagram i zdania z polami do uzupełnienia (obiekt `D`) |
| `szablony.js` | stałe fragmenty tekstu z pliku gabinetu (badanie, zalecenia, instruktaż wg wieku itd.) |

## Jak wprowadzić zmianę
1. Otwórz plik na GitHubie → ikona ołówka (Edit).
2. Popraw tekst → **Commit changes**.
3. Po ok. 1–2 minutach strona na GitHub Pages pokazuje nową wersję (odśwież z Ctrl+F5).

Przy zmianach w `szablony.js` pilnuj cudzysłowów i przecinków – błąd składni zatrzyma całą aplikację.

> Uwaga: strona GitHub Pages jest publiczna dla każdego, kto zna link.
