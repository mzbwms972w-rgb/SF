#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN patch day-livemotion: v14 (day-navglide) -> v15 (day-livemotion).

Бриф главреда 04.10.2026: «у меня не работают анимации».
Диагноз e2e (worktmp/e2e_viewers.py): опубликованный blob корректен, htmlpreview
работает, НО при prefers-reduced-motion:reduce (Windows: «Эффекты анимации» выкл.)
текущая сборка глушит ВСЁ — CSS-рубильник *{animation-duration:.01ms!important…},
ховер-медиа с no-preference и JS-ветка mqRM (мгновенное переключение).
Решение: моушен выпуска всегда жив — RM-гейтинг удалён целиком (загрузочный
каскад day-motion, кроссфейд полос, плавная прокрутка, ховер фото работают при
любой системной настройке); печать остаётся статичной. Больше НИЧЕГО не меняем.

Патч идемпотентен по результату: каждый old встречается ровно count раз,
иначе AssertionError. Запуск: python3 worktmp/patch_day_livemotion.py
"""
import os
import py_compile

ROOT = os.getcwd()
SRC = os.path.join(ROOT, 'worktmp', 'build_daily_0310_state_v14.py')
DST = os.path.join(ROOT, 'worktmp', 'build_daily_0310_state_v15.py')

src = open(SRC, encoding='utf-8').read()

REPL = []

# --- 1. шапка/докстринг -----------------------------------------------------
REPL.append((
    '"""SFN: сборщик выпуска 03.10.2026 (v14, «Единая сетка дня» — цельная концепция).',
    '"""SFN: сборщик выпуска 03.10.2026 (v15, «Единая сетка дня» — цельная концепция).',
    1))

REPL.append((
    '''прокрутка к началу новой полосы — плавная, той же кривой; без 3D-перелистывания.
Выход: anna-malboro/daily-03-10-2026.html (очередь подшивки).
Запуск из корня:  python3 worktmp/build_daily_0310_state_v14.py''',
    '''прокрутка к началу новой полосы — плавная, той же кривой; без 3D-перелистывания.
Моушен всегда жив (day-livemotion, бриф главреда 04.10.2026 «у меня не работают
анимации»): системная настройка «уменьшить движение» (prefers-reduced-motion)
больше НЕ глушит выпуск — CSS-рубильник *{animation-duration:.01ms}, RM-условие
ховера и JS-ветка mqRM мгновенного переключения удалены; загрузочный каскад
day-motion, кроссфейд полос, плавная прокрутка и ховер фото проигрываются на
любом устройстве; статичной остаётся только печать.
Выход: anna-malboro/daily-03-10-2026.html (очередь подшивки).
Запуск из корня:  python3 worktmp/build_daily_0310_state_v15.py''',
    1))

# --- 2. штамп свежести (первая строка CSS) ----------------------------------
REPL.append((
    '/* SFN-DESIGN-029: day-navglide · 03.10.2026 */',
    '/* SFN-DESIGN-029: day-livemotion · 03.10.2026 */',
    1))

# --- 3. CSS: ховер живёт всегда, RM-рубильник удалён ------------------------
REPL.append((
    '@media (hover:hover) and (prefers-reduced-motion:no-preference){.ph:hover img{transform:scale(1.02)}}',
    '@media (hover:hover){.ph:hover img{transform:scale(1.02)}}',
    1))

REPL.append((
    '\n@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;animation-delay:0s!important;transition-duration:.01ms!important}}',
    '',
    1))

# --- 4. NAV_JS: комментарий без RM-обещания ---------------------------------
REPL.append((
    '''   Флаг busy гасит повторные нажатия; prefers-reduced-motion — мгновенное
   переключение. */''',
    '''   Флаг busy гасит повторные нажатия. Анимации перехода и прокрутки работают
   ВСЕГДА — системная настройка «уменьшить движение» их больше не глушит
   (решение главреда от 04.10.2026); статичной остаётся только печать. */''',
    1))

# --- 5. NAV_JS: mqRM-переменная и ветка мгновенного переключения удалены -----
REPL.append((
    "  var mqRM=window.matchMedia?window.matchMedia('(prefers-reduced-motion: reduce)'):null;\n",
    '',
    1))

REPL.append((
    '''    if(mqRM&&mqRM.matches){
      sheets[cur].classList.remove('is-on');
      sheets[cur].classList.add('is-off');
      sheets[ni].classList.remove('is-off');
      sheets[ni].classList.add('is-on');
      cur=ni;
      window.scrollTo(0,0);
      busy=false;
      buttons(cur);
      return;
    }
    var from=cur;''',
    '    var from=cur;',
    1))

# --- 6. маркер подвала (ровно строка P.append; в ассерте маркер заменится в п.7)
REPL.append((
    "P.append('<!-- SFN · 2026 · 029 · day-navglide -->\\n</body>\\n</html>\\n')",
    "P.append('<!-- SFN · 2026 · 029 · day-livemotion -->\\n</body>\\n</html>\\n')",
    1))

# --- 7. ассерты сборки -------------------------------------------------------
REPL.append((
    "assert 'SFN-DESIGN-029: day-navglide' in html and '<!-- SFN · 2026 · 029 · day-navglide -->' in html",
    '''assert 'SFN-DESIGN-029: day-livemotion' in html and '<!-- SFN · 2026 · 029 · day-livemotion -->' in html
assert 'prefers-reduced-motion' not in html, 'вернулся RM-глушитель анимаций'
assert 'mqRM' not in html, 'в навигации осталась RM-ветка мгновенного переключения'
assert '@media (hover:hover){.ph:hover img{transform:scale(1.02)}}' in html, 'ховер фото не всегда живой'
assert '@media print{*{animation:none!important;transition:none!important}}' in html, 'печать перестала быть статичной\'''',
    1))

# --- 8. финальный print ------------------------------------------------------
REPL.append((
    "print(f'собрано v14 (day-navglide): {OUT}')",
    "print(f'собрано v15 (day-livemotion): {OUT}')",
    1))

for i, (old, new, cnt) in enumerate(REPL, 1):
    got = src.count(old)
    assert got == cnt, f'REPL#{i}: найдено {got} вхождений, ожидалось {cnt}: {old[:70]!r}'
    src = src.replace(old, new)

# контроль: в v15 не осталось РАБОЧИХ следов RM. Литеральные упоминания допустимы
# ровно в двух безопасных местах: историческая справка в докстринге и текст новых
# ассертов сборки (которые сами и не пустят RM в HTML).
occ = []
_i = src.find('prefers-reduced-motion')
while _i != -1:
    occ.append(src[max(0, _i - 70):_i + 90].replace('\n', '\\n'))
    _i = src.find('prefers-reduced-motion', _i + 1)
print('RM-вхождений в исходнике v15:', len(occ))
for _o in occ:
    print('  …', _o)
assert len(occ) == 2 and any('больше НЕ глушит' in o for o in occ) \
    and any('RM-глушитель анимаций' in o for o in occ), \
    'в исходнике v15 осталось незапланированное упоминание RM'
assert '@media (prefers-reduced-motion' not in src, 'CSS-рубильник RM уцелел'
assert 'matchMedia' not in src, 'в NAV_JS уцелел matchMedia-зонд RM'
assert 'var mqRM' not in src and 'mqRM&&' not in src, 'в NAV_JS уцелела RM-ветка'
assert src.count('day-livemotion') >= 6, 'мало упоминаний нового слага'
assert 'day-navglide' in src, 'историческое имя NAVGLIDE-блока потеряно'

with open(DST, 'w', encoding='utf-8') as fh:
    fh.write(src)
py_compile.compile(DST, doraise=True)
print('патч day-livemotion: создан', DST, f'({len(src)} байт), компилируется')
