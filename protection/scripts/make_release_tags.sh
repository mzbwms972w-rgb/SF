#!/bin/sh
# SFN: ретро-теги на все опубликованные выпуски.
# Тег ставится на ПЕРВЫЙ коммит, добавивший файл: дата коммита = дата первенства.
# По умолчанию DRY-RUN. Применение:  sh make_release_tags.sh apply
# Теги не удалять и не двигать никогда (HANDOVER §2).
set -e
cd "$(git rev-parse --show-toplevel)"
MODE="${1:-dry}"
for f in $(git ls-files '*.html' | grep -v '^template' | grep -v '^worktmp/' | grep -v '^anna-malboro/' | sort); do
  sha=$(git log --diff-filter=A --format=%H -- "$f" | tail -1)
  [ -z "$sha" ] && continue
  tag="v-$(echo "$f" | sed 's/\.html$//')"
  cdate=$(git log -1 --format=%cs "$sha")
  if git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
    echo "skip  $tag (уже есть)"
    continue
  fi
  echo "tag   $tag -> $sha ($cdate)  $f"
  if [ "$MODE" = "apply" ]; then
    git tag -a "$tag" "$sha" -m "San Fierro News: выпуск $f от $cdate"
  fi
done
if [ "$MODE" = "apply" ]; then
  echo "push tags..."
  git push -q origin --tags
  echo "done"
else
  echo "(dry-run: для применения запусти  sh $0 apply)"
fi
