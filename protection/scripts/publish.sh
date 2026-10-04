#!/bin/sh
# SFN PUBLISH — единственная дверь, через которую редакция пушит в GitHub.
# Использование:  sh protection/scripts/publish.sh "текст коммита" [--tag] [--manifest]
# Никаких push мимо этого скрипта: сначала guard, только потом коммит и fast-forward push.
set -e
MSG="$1"; shift || true
cd "$(git rev-parse --show-toplevel)"
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "== fetch origin main =="
git fetch -q origin main

echo "== guard =="
python3 "$HERE/guard.py" || { echo "ПУБЛИКАЦИЯ ОСТАНОВЛЕНА guard'ом."; exit 1; }

echo "== commit =="
git add -A
if git diff --cached --quiet >/dev/null; then
  echo "нечего коммитить"; exit 0
fi
git commit -q -m "$MSG"

echo "== push (только fast-forward) =="
if ! git push -q origin main 2>/tmp/sfn_push_err; then
  echo "push отклонён (не fast-forward или нет прав). FORCE-ПУШ ЗАПРЕЩЁН — разбираемся вручную."
  cat /tmp/sfn_push_err; exit 1
fi

for flag in "$@"; do
  case "$flag" in
    --manifest) python3 "$HERE/make_manifest.py"; git add manifest.json;
                git commit -q -m "San Fierro News: манифест выпуска"; git push -q origin main ;;
    --tag)      sh "$HERE/make_release_tags.sh" apply ;;
  esac
done
echo "ОПУБЛИКОВАНО. Ссылки проверки:"
echo "  https://htmlpreview.github.io/?https://github.com/Wereskkk/San-Fierro-News-Evolve-RP/blob/main/newsroom.html"
