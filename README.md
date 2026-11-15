# Generator opisów zabiegów NFZ

Aplikacja do generowania opisów do dokumentacji (wizyta 30 min) na podstawie szablonów gabinetu – pacjent poniżej i powyżej 5 r.ż. (w tym ST30E i szablony wizyt I–IV).

**Jak działa:** wiek pacjenta i kody zabiegów → pytania i diagram zębów (zęby, ćwiartki, powierzchnie) → gotowy opis z przyciskiem „Kopiuj cały opis”. Niewypełnione miejsca zostają jako `[UZUPEŁNIJ: …]`. Bez inicjałów pacjenta aplikacja niczego nie zapisuje.

## Wycena punktowa
Na kroku 3 obok opisu widać sumę punktów wizyty, a niżej tabelę wyceny. Punkty pakietów (ST…) wg zał. 1c – Zarządzenie 95/2026/DSOZ (od 1.09.2026), świadczeń jednostkowych (1101, 1006, 1105, 1108, 1206, 1502–1505, znieczulenia 23.0401–0403) wg zał. 1b – Zarządzenie 44/2025/DSOZ. Współczynniki z zarządzenia 60/2023/DSOZ z późn. zm.: ×1,5 do 18 r.ż. (bez ST30D–ST30G), ×1,2 ciąża/połóg, kolejne pakiety na wizycie ×0,8 (bez ST30E, ST30G). Wartości są w obiekcie `PTS` w `index.html`.

## Kwoty i udział lekarza
Pod tabelą wyceny: cena punktu (domyślnie 1,81 zł, można zmienić w polu), kwota za wizytę = punkty × cena punktu oraz kwota dla lekarza – 40% (domyślnie) albo 35% od całej kwoty wizyty, przełączane jednym kliknięciem. Cena punktu i wybrany % są zapamiętywane w przeglądarce.

## Historia opisów
Po wpisaniu inicjałów pacjenta (krok 1 albo 3) gotowy opis zapisuje się sam w zakładce **Historia** – z inicjałami, datą wizyty, kodami i kwotami. Bez inicjałów nic się nie zapisuje. Wpis można skopiować, podejrzeć, otworzyć do poprawy albo usunąć; jest też wyszukiwanie po inicjałach/dacie, kopia do pliku `.txt` i usuwanie wpisów starszych niż 3 miesiące.

Historia jest trzymana **wyłącznie w pamięci tej przeglądarki na tym urządzeniu** (localStorage) – nie trafia na GitHuba ani na żaden serwer, nie przenosi się między komputerem a telefonem, a wyczyszczenie danych przeglądarki ją usuwa. Mieści ok. 1000 typowych opisów (Chrome/Edge/Firefox).

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
