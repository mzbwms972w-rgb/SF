#!/usr/bin/env python3
"""SFN: хэш-манифест опубликованных страниц.

Запуск из корня репозитория:  python3 protection/scripts/make_manifest.py
Пишет manifest.json: для каждого опубликованного .html (кроме template_*) —
sha256, размер и дату генерации манифеста. Коммитится тем же коммитом, что и выпуск:
получаем tamper-evident индекс «файл X с хэшем Y существовал на коммите/теге Z».
"""
import glob, hashlib, json, os, sys
from datetime import date

ROOT = os.getcwd()
entries = []
for f in sorted(glob.glob('*.html')):
    if f.startswith('template'):
        continue
    p = os.path.join(ROOT, f)
    data = open(p, 'rb').read()
    entries.append({
        'file': f,
        'bytes': len(data),
        'sha256': hashlib.sha256(data).hexdigest(),
    })

out = {
    'generated': date.today().isoformat(),
    'repo': 'Wereskkk/San-Fierro-News-Evolve-RP',
    'branch': 'main',
    'issues': len(entries),
    'files': entries,
}
target = sys.argv[1] if len(sys.argv) > 1 else 'manifest.json'
with open(target, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(f'manifest: {len(entries)} files -> {target}')
for e in entries[:5]:
    print('  ', e['file'], e['sha256'][:16])
