#!/bin/zsh
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
cd "my app" 2>/dev/null || true
npm install
npm run build
rm -rf "$ROOT/backend/static"
cp -R dist "$ROOT/backend/static"
cp "$ROOT/output/app_check.html" "$ROOT/backend/static/app_check.html"
cp -R "$ROOT/output/app_check_images" "$ROOT/backend/static/app_check_images"
cd "$ROOT/backend"
python3 -m pip install -r requirements.txt
[[ -f /Users/iin3rdyii/Desktop/data/campus_customs.db ]] || { echo 'Missing campus_customs.db; see README.' >&2; exit 1; }
exec uvicorn main:app --host 0.0.0.0 --port 8000
