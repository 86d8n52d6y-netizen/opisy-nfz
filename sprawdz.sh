#!/usr/bin/env bash
# Szybki test składni przed commitem: błąd w JS zatrzymuje cały moduł.
# Użycie: bash sprawdz.sh   (wymaga Node.js)
set -e
cd "$(dirname "$0")"
for f in szablony.js wspolne.js $(ls prywatne-katalog.js 2>/dev/null); do node --check "$f"; done
for f in index.html nfz.html kalendarz.html $(ls prywatne.html 2>/dev/null); do
node -e '
const fs=require("fs"),f=process.argv[1];
const h=fs.readFileSync(f,"utf8");
const s=[...h.matchAll(/<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join("\n;\n");
try{new Function(s);}catch(e){console.error(f+": "+e.message);process.exit(1);}
' "$f"
done
echo "OK – składnia stron (index, nfz, kalendarz$( [ -f prywatne.html ] && echo ', prywatne')) i skryptów wspólnych poprawna"
