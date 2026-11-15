#!/usr/bin/env bash
# Testy aplikacji w prawdziwej przeglądarce (Chrome bez okna, sterowany z Pythona – Playwright).
# Użycie:  bash testy/uruchom.sh            – wszystkie testy t*.py
#          bash testy/uruchom.sh t1_calc.py – wybrany test
# Wymaga: python3 + playwright, Google Chrome (/usr/bin/google-chrome), git.
# Serwer lokalny wystawia katalog repozytorium pod http://127.0.0.1:8765/ ; wersja wyjściowa (sprzed rozbudowy,
# commit e8476e8) jest odtwarzana z historii gita do testy/.v9/ – służy do testów migracji i porównania opisów.
cd "$(dirname "$0")/.."
PORT=${OPISY_PORT:-8765}
mkdir -p testy/.v9 testy/zrzuty
[ -f testy/.v9/index.html ] || { git show e8476e8:index.html > testy/.v9/index.html && git show e8476e8:szablony.js > testy/.v9/szablony.js; }
if ! curl -sf -o /dev/null "http://127.0.0.1:$PORT/szablony.js"; then
  (python3 -m http.server "$PORT" --bind 127.0.0.1 >/tmp/opisy-http.log 2>&1 &)
  for i in $(seq 1 20); do sleep 0.3; curl -sf -o /dev/null "http://127.0.0.1:$PORT/szablony.js" && break; done
fi
export OPISY_URL="http://127.0.0.1:$PORT/index.html" OPISY_V9_URL="http://127.0.0.1:$PORT/testy/.v9/index.html"
rc=0
if [ $# -gt 0 ]; then files=("$@"); else files=(t*.py); fi
for f in "${files[@]}"; do
  python3 "testy/$(basename "$f")" 2>&1 | grep -v "agent-proxy\|connect_rejected\|Allowed domains\|For details\|^$" ; [ "${PIPESTATUS[0]}" -eq 0 ] || rc=1
done
exit $rc
