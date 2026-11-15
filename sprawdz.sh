#!/usr/bin/env bash
# Szybki test składni przed commitem: błąd w JS zatrzymuje całą aplikację.
# Użycie: bash sprawdz.sh   (wymaga Node.js)
set -e
cd "$(dirname "$0")"
node --check szablony.js
node -e '
const fs=require("fs");
const h=fs.readFileSync("index.html","utf8");
const s=[...h.matchAll(/<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join("\n;\n");
new Function(s);
'
echo "OK – składnia index.html i szablony.js poprawna"
