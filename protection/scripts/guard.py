#!/usr/bin/env python3
"""SFN GUARD — предохранитель публикации. Запускается ПЕРЕД каждым push (publish.sh).

Инварианты редакции (HANDOVER §2 «URL вечные», §6 RP-чистота):
  G1  Ни один опубликованный .html/.png не удален и не переименован (ссылки вечные).
  G2  Все локальные href/src во всех опубликованных страницах указывают на существующие файлы.
  G3  Хаб newsroom.html консистентен: счётчик выпусков = числу карточек, «свежий номер» ровно один,
      каждая карточка указывает на существующий файл.
  G4  RP-чистота: проверяются ТОЛЬКО изменённые в этом пуше файлы (видимый текст):
      запрещены «Evolve Role Play/Evolve RP», «Saint-Louis», слово «чат», underscores в именах.
  G5  Целостность base64: все data:-блобы изменённых файлов декодируются.
  G6  Изменённые опубликованные страницы имеют <title> и viewport.
Предупреждения (не блокируют): нет meta description; нет штампа SFN-DESIGN- (до внедрения ритуала).

Выход: 0 = можно публиковать, 1 = СТОП, публиковать нельзя.
"""
import glob, os, re, subprocess, sys, base64, io

FAIL, WARN = [], []
def fail(m): FAIL.append(m)
def warn(m): WARN.append(m)

def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout

def visible(s):
    s = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'base64,[A-Za-z0-9+/=]+', '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return s

def published_set():
    out = set(glob.glob('*.html')) - set(glob.glob('template_*.html'))
    out |= set(glob.glob('flyers/*.png')) | set(glob.glob('assets/**/*.png', recursive=True))
    out |= set(glob.glob('assets/**/*.jpg', recursive=True))
    return out

# ---- G1: удаления/переименования опубликованного ----
# anna-malboro/ — очередь на подшивку (anna-malboro/README.md): файлы оттуда легально
# исчезают после подшивки в корень, поэтому G1 на папку не распространяется.
STAGING_PREFIXES = ('anna-malboro/',)
on_main = set(sh('git', 'ls-tree', '-r', '--name-only', 'origin/main').split())
protected_on_main = {p for p in on_main if not p.startswith(STAGING_PREFIXES)
                     and ((p.endswith('.html') and not p.startswith('template'))
                     or p.endswith('.png') or (p.startswith('assets/') and p.endswith('.jpg')))}
here = published_set() | {p for p in glob.glob('*.html')} | set(glob.glob('flyers/*.png'))
for p in sorted(protected_on_main - here):
    if os.path.exists(p):
        continue
    fail(f'G1: опубликованный файл ИСЧЕЗ из дерева: {p} (URL вечные — удалять/переименовывать нельзя)')

# ---- G2: битые локальные ссылки во всех опубликованных страницах ----
for f in sorted(glob.glob('*.html')):
    if f.startswith('template'):
        continue
    s = open(f, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'(?:href|src)="([^"]+)"', s):
        u = m.group(1)
        if u.startswith(('http', 'data:', 'mailto:', '#', '//')):
            continue
        if not os.path.exists(u.split('#')[0]):
            fail(f'G2: битая ссылка в {f}: {u}')

# ---- G3: консистентность хаба ----
hub = 'newsroom.html'
if os.path.exists(hub):
    s = open(hub, encoding='utf-8').read()
    cards = len(re.findall(r'class="card"', s))
    mstat = re.search(r'stats mono"><span>(\d+)\s*выпуск', s)
    if mstat and int(mstat.group(1)) != cards:
        fail(f'G3: счётчик хаба {mstat.group(1)} не равен числу карточек {cards}')
    if s.count('свежий номер') != 1:
        fail(f'G3: пометка «свежий номер» встречается {s.count("свежий номер")} раз (должна ровно 1)')
    for m in re.finditer(r'class="card"[^>]*href="([^"]+)"', s):
        if not os.path.exists(m.group(1)):
            fail(f'G3: карточка хаба указывает на несуществующий файл: {m.group(1)}')

# ---- изменяемые файлы относительно origin/main ----
diff = sh('git', 'diff', '--name-only', 'origin/main').split() + \
       sh('git', 'diff', '--cached', '--name-only', 'origin/main').split() + \
       sh('git', 'ls-files', '--others', '--exclude-standard').split()
changed = sorted(set(x for x in diff if x.endswith('.html')))

# ---- G4/G5/G6 по изменённым ----
FORBID = [('Evolve Role Play', re.compile(r'Evolve\s+Role\s+Play', re.I)),
          ('Evolve RP', re.compile(r'Evolve\s+RP', re.I)),
          ('Saint-Louis', re.compile(r'Saint[- ]Louis', re.I)),
          ('слово «чат»', re.compile(r'\bчат[а-я]*\b', re.I)),
          ('underscore в имени', re.compile(r'[A-Z][a-z]+_[A-Z][a-z]+'))]
for f in changed:
    if not os.path.exists(f) or f.startswith('template'):
        continue
    s = open(f, encoding='utf-8', errors='replace').read()
    v = visible(s)
    for name, rx in FORBID:
        for m in rx.finditer(v):
            fail(f'G4: {f}: запрещённое «{name}»: …{v[max(0,m.start()-40):m.end()+40].strip()}…')
    for i, blob in enumerate(re.findall(r'data:[a-z/+]+;base64,([A-Za-z0-9+/=]+)', s)):
        try:
            base64.b64decode(blob, validate=True)
        except Exception:
            fail(f'G5: {f}: base64-блоб #{i} не декодируется')
            break
    head = s[:4000]
    if '<title>' not in head:
        fail(f'G6: {f}: нет <title>')
    if 'viewport' not in head:
        fail(f'G6: {f}: нет meta viewport')
    if 'name="description"' not in head:
        warn(f'{f}: нет meta description (превью ссылок в Discord/VK будет пустым)')
    import re as _re
    if not f.startswith('template') and not _re.search(r'SFN-(DESIGN|WEEKLY)-', s):
        warn(f'{f}: нет штампа SFN-DESIGN- (ритуал защиты ещё не внедрён)')

print('SFN GUARD: изменённых html:', len(changed))
for w in WARN:
    print('  WARN:', w)
if FAIL:
    print('SFN GUARD: СТОП, публикация запрещена:')
    for x in FAIL:
        print('  FAIL:', x)
    sys.exit(1)
print('SFN GUARD: OK, публиковать можно')
