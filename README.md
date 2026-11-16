# Gabinet – Kalendarz, Opisy NFZ i Opisy prywatne

Jedna aplikacja w przeglądarce dla lekarza dentysty, złożona z trzech modułów:

| Moduł | Plik | Co robi |
|---|---|---|
| Strona główna | `index.html` | logowanie, trzy kafelki modułów, okno **Zarobki – wszystkie gabinety**, konto i bezpieczeństwo |
| Kalendarz | `kalendarz.html` | dyżury w kilku gabinetach, rozliczenia, przychód netto, ZUS i podatek (dawny „Grafik Gabinetów”) |
| Opisy NFZ | `nfz.html` | generator opisów zabiegów NFZ z wyceną punktową, ewidencją wizyt i statystykami |
| Opisy prywatne | `prywatne.html` | generator opisów zabiegów prywatnych z cennikiem (w przygotowaniu – etap 5) |

Pasek u góry każdej strony przełącza moduły bez wracania na stronę główną; rozpoczęta wizyta w Opisach NFZ zostaje (szkic) i wraca po powrocie do modułu.

## Konto, hasło i szyfrowanie
- Każdy użytkownik ma **własne hasło** (min. 6 znaków) i widzi **wyłącznie swoje dane**. Kolejnego użytkownika dodaje się na ekranie logowania.
- Dane (wizyty, opisy, kalendarz, szkice, sumy dzienne) są **zaszyfrowane** (AES-GCM 256) losowym kluczem użytkownika. Klucz jest zapisany tylko w postaci zaszyfrowanej: hasłem (PBKDF2-SHA-256, 600 000 iteracji) i osobno **kodem odzyskiwania** (24 znaki, pokazywany raz przy zakładaniu konta). Bez hasła i bez kodu danych nie da się odczytać – także dla autora aplikacji.
- **Blokada po bezczynności** (domyślnie 15 min, do zmiany w „Konto i bezpieczeństwo”), przycisk „Zablokuj” i „Zmień użytkownika” w menu użytkownika na pasku. Po ponownym zalogowaniu aplikacja wraca do modułu i niezapisanej wizyty.
- „Konto i bezpieczeństwo”: zmiana hasła, nowy kod odzyskiwania, usunięcie konta ze wszystkimi jego danymi.
- Przy pierwszym założeniu konta dane z poprzednich wersji (Generator opisów NFZ, Grafik Gabinetów – jeśli były otwierane w tej przeglądarce pod tym adresem) przenoszą się do konta i szyfrują; jawne kopie są usuwane dopiero po sprawdzeniu, że zaszyfrowane dane dają się odczytać.

## Opisy NFZ – jak działa
**Wiek pacjenta i kody zabiegów → pytania i diagram zębów (zęby, ćwiartki, powierzchnie) → gotowy opis** z przyciskiem „Kopiuj cały opis”. Niewypełnione miejsca zostają jako `[UZUPEŁNIJ: …]`. Każda wizyta może zapisać się w ewidencji (z inicjałami albo anonimowo) – z punktami, kwotami, czasem i gabinetem (domyślnie z dyżuru w Kalendarzu) – a zakładka **Statystyki** liczy z tego zarobki dzienne, tygodniowe i miesięczne.

## Wycena punktowa
Na kroku 3 obok opisu widać sumę punktów wizyty, a niżej tabelę wyceny. Punkty pakietów (ST…) wg zał. 1c – Zarządzenie 95/2026/DSOZ (od 1.09.2026), świadczeń jednostkowych (1101, 1006, 1105, 1108, 1206, 1502–1505, znieczulenia 23.0401–0403) wg zał. 1b – Zarządzenie 44/2025/DSOZ. Współczynniki z zarządzenia 60/2023/DSOZ z późn. zm.: ×1,5 do 18 r.ż. (bez ST30D–ST30G), ×1,2 ciąża/połóg, kolejne pakiety na wizycie ×0,8 (bez ST30E, ST30G). Wartości są w obiekcie `PTS` w `nfz.html`.

## Kwoty i udział lekarza
Pod tabelą wyceny: stawka za punkt (domyślnie **1,84 zł**, zmienisz ją w polu albo w Ustawieniach), wartość punktów = punkty × stawka oraz kwota dla lekarza – 40% (domyślnie) albo 35% od wartości punktów, przełączane jednym kliknięciem. Kwoty liczone są w groszach (liczby całkowite), połówki grosza w górę.

## Rozliczenie wizyty (krok 3)
Pod wyceną jest „Rozliczenie wizyty” – trafia do ewidencji, nie do opisu:
- **Czas wizyty** – podpowiadany sam: standardowo 30 min; gdy na wizycie jest pakiet higienizacyjny (ST30, ST30E, ST30G) **i** ekstrakcja (ST01, ST02) albo leczenie zachowawcze (1105, 1108, 1206, 1502–1505), do czasu wizyty dolicza się **10 min – raz**, niezależnie od liczby zębów i procedur (30 + 10 = 40 min; gdy same pakiety zajmują więcej niż 30 min, np. ST30 w 4 ćwiartkach = 40 min, to 40 + 10 = 50 min). Można wpisać własny czas.
- **Przeglądy** – liczba godzin (także ułamki, np. 1,5) × **350 zł/h**.
- **Dodatkowe zarobki** – dowolna liczba pozycji „kwota + opis”, osobna kategoria przychodu (nie mieszają się z punktami).

## Ewidencja wizyt (zakładka Historia)
Dwa tryby zapisu, przełączane jednym kliknięciem (krok 1, krok 3 albo Ustawienia) i zapamiętywane w przeglądarce:
- **z inicjałami** – wizyta zapisuje się sama po wpisaniu inicjałów pacjenta; bez inicjałów nic się nie zapisuje;
- **automatyczny, bez inicjałów** – każda wygenerowana wizyta zapisuje się sama jako wpis anonimowy z własnym numerem (`Anonim #12`).

Każdy wpis ma: datę i dzień tygodnia, punkty, wartość punktów, udział lekarza, godziny przeglądów, dodatkowe zarobki, czas wizyty i sumę. Jedna wizyta = jeden wpis aż do „Następny pacjent”; zapis następuje tylko wtedy, gdy coś się zmieniło. Gdy formularz wygląda na innego pacjenta (inne inicjały, inny wiek, zamienione zabiegi albo inne API i GI), aplikacja niczego nie nadpisuje i pyta: „nowy pacjent” czy „poprawka”.

W Historii: **szybki wpis** (same punkty, godziny przeglądów albo dodatkowa kwota – bez generowania opisu), podsumowanie dnia, wyszukiwanie, „Kopiuj opis”, „Pokaż opis”, „Otwórz i popraw” (wraca do generatora), „Edytuj kwoty” (punkty, stawki, przeglądy, dodatkowe zarobki, czas, data) i „usuń”. Wpis z samymi przeglądami lub kwotą dodatkową nie jest liczony jako wizyta pacjenta.

## Statystyki
Zakres dat: gotowe przyciski (dziś, tydzień, miesiąc, poprzedni miesiąc, 12 miesięcy, rok, wszystko) albo dowolne „od–do”. Kafelki: zarobek razem, punkty, przeglądy, dodatkowe, liczba wizyt i średnia na wizytę, dni przepracowane, średnia na dzień pracy i na dzień kalendarzowy, czas wizyt i czas pracy. Zakładki z wykresem i tabelą: **Dni**, **Tygodnie** (poniedziałek–niedziela), **Miesiące** (ze zmianą do poprzedniego miesiąca), **Dni tygodnia** (który dzień jest najbardziej dochodowy i jak to się zmienia w kolejnych miesiącach). Dzień przepracowany = dzień z co najmniej jednym wpisem – dni wolne nie zaniżają średniej. Na wykresie tygodniowym i miesięcznym oś czasu jest ciągła: tydzień lub miesiąc bez wpisów (np. urlop) ma słupek 0 zł; nie ma za to zer sprzed pierwszego wpisu ani okresów z przyszłości. Wykres dzienny pokazuje tylko dni z wpisami. W szerokich tabelach nazwa okresu zostaje przyklejona przy przewijaniu w bok, a cień przy prawej krawędzi pokazuje, że są dalsze kolumny.

„Zarobek z punktów” można liczyć jako **pełną wartość punktów** (domyślnie, 100 pkt = 184 zł) albo jako **udział lekarza** (% zapisany przy wizycie); przeglądy i kwoty dodatkowe zawsze wchodzą w całości.

## Dane, kopia zapasowa, prywatność
- Wszystkie dane są zapisane **wyłącznie w tej przeglądarce na tym urządzeniu**, zaszyfrowane kluczem zalogowanego użytkownika (bazy IndexedDB `gabinet@<id>` i `opisyNFZ@<id>`; nieszyfrowane zostają tylko ustawienia stawek i wyglądu w localStorage). Nic nie trafia na GitHuba ani na żaden serwer i nic nie przenosi się samo między komputerem a telefonem.
- **Opisy NFZ → Ustawienia → Pobierz kopię zapasową (.json)** zapisuje wpisy, opisy i ustawienia do pliku; **Wczytaj kopię** scala plik z danymi (dodaje brakujące wpisy, istniejący zastępuje tylko nowszą wersją, niczego nie kasuje). Ten plik **nie jest szyfrowany** – przechowuj go jak dokumentację medyczną. Kalendarz ma własny eksport w swoich Ustawieniach.
- Wyczyszczenie danych przeglądarki usuwa dane. Safari (iPhone, Mac) może samo usunąć dane strony nieotwieranej przez 7 dni – tam kopia zapasowa jest szczególnie ważna.
- Gdy baza przeglądarki dla Opisów NFZ jest niedostępna, wpisy zapisują się (też zaszyfrowane) w pamięci zapasowej i wracają do bazy, gdy będzie dostępna. Przeglądarka bez bazy danych lub z zablokowaną pamięcią (np. niektóre tryby prywatne) nie założy konta – strona główna wyjaśnia dlaczego.

## Pliki
| Plik | Co zawiera |
|---|---|
| `index.html` | strona główna: logowanie, kafelki, okno Zarobki, konto |
| `wspolne.js`, `wspolne.css` | wspólne: użytkownicy, szyfrowanie, sesja i blokada, pasek modułów, magazyn danych, przeniesienie starych danych |
| `nfz.html` | Opisy NFZ: wygląd, pytania, diagram i zdania z polami do uzupełnienia (obiekt `D`), wycena `PTS`, ewidencja |
| `szablony.js` | stałe fragmenty tekstu z pliku gabinetu (badanie, zalecenia, instruktaż wg wieku itd.) |
| `kalendarz.html` | Kalendarz (dyżury, rozliczenia, podatki) |
| `POLACZENIE.md` | analiza, przepisy o dokumentacji i projekt połączenia aplikacji |
| `POSTEP.md` | co zrobione, co w toku, co dalej – do wznawiania pracy po przerwie |
| `CLAUDE.md` | zasady pracy w repo (gałęzie, etapy, test przed commitem) |
| `sprawdz.sh` | test składni JS przed commitem: `bash sprawdz.sh` |
| `testy/` | testy w prawdziwej przeglądarce (Chrome bez okna): `bash testy/uruchom.sh` |

## Jak wprowadzić zmianę
1. Otwórz plik na GitHubie → ikona ołówka (Edit).
2. Popraw tekst → **Commit changes**.
3. Po ok. 1–2 minutach strona na GitHub Pages pokazuje nową wersję (odśwież z Ctrl+F5).

Przy zmianach w `szablony.js` pilnuj cudzysłowów i przecinków – błąd składni zatrzyma całą aplikację.

> Uwaga: strona GitHub Pages jest publiczna dla każdego, kto zna link.
