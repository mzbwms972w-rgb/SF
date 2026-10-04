#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN patch day-pageindicator: v15 (day-livemotion) -> v16 (day-pageindicator).

Бриф главреда 04.10.2026: постоянный счётчик «N / 4» рядом со стрелками убрать
ПОЛНОСТЬЮ (без пустого места в баре, без счётчика у стрелок), вместо него —
временный индикатор номера полосы, который появляется только в момент
перелистывания: по центру ВВЕРХУ экрана, «ПОЛОСА N / 4», газетный стиль
(бумажный фон, тёмный моноширинный капс, тонкая красная линейка снизу),
появление opacity 0→1 + translateY(-8px→0), пауза ~0.7–0.9s, уход
opacity 1→0 + translateY(0→-8px), весь цикл ~1.3–1.8s (1.6s), после
исчезновения не остаётся видимым, при следующем переключении анимация
запускается заново с номером реально открытой полосы. Макет газеты плашка не
занимает и .sheet не сдвигает (position:fixed, pointer-events:none).
Стрелки ← → сохранены. Дизайн, тексты, фото, сетка, цвета и типографика не
трогаются; кроссфейд полос, плавная прокрутка и «моушен всегда жив» — как были.

Патч идемпотентен по результату: каждый old встречается ровно count раз,
иначе AssertionError. Запуск: python3 worktmp/patch_day_pageindicator.py
"""
import os
import py_compile

ROOT = os.getcwd()
SRC = os.path.join(ROOT, 'worktmp', 'build_daily_0310_state_v15.py')
DST = os.path.join(ROOT, 'worktmp', 'build_daily_0310_state_v16.py')

src = open(SRC, encoding='utf-8').read()

REPL = []

# --- 1. шапка/докстринг -----------------------------------------------------
REPL.append((
    '"""SFN: сборщик выпуска 03.10.2026 (v15, «Единая сетка дня» — цельная концепция).',
    '"""SFN: сборщик выпуска 03.10.2026 (v16, «Единая сетка дня» — цельная концепция).',
    1))

REPL.append((
    '''любом устройстве; статичной остаётся только печать.
Выход: anna-malboro/daily-03-10-2026.html (очередь подшивки).
Запуск из корня:  python3 worktmp/build_daily_0310_state_v15.py''',
    '''любом устройстве; статичной остаётся только печать.
Индикатор полосы (day-pageindicator, бриф главреда 04.10.2026): постоянный
счётчик N / 4 рядом со стрелками удалён ЦЕЛИКОМ — ни в боковом поле широкого
экрана, ни в компактном мобильном баре (пустого места под ним не осталось);
стрелки ← → сохранены. Вместо счётчика — временная плашка «ПОЛОСА N / 4»: она
появляется только в момент перелистывания, по центру ВВЕРХУ экрана
(position:fixed, pointer-events:none, z-index 10000), поэтому места в макете
не занимает и .sheet не сдвигает. Стиль газетный: бумажный фон, тёмный
моноширинный капс, тонкая красная линейка снизу, без рамок и UI-глянца. Цикл
pageIndicatorInOut 1.6s ease both: появление opacity 0→1 + translateY(-8px→0)
(~0.29s), пауза ~0.83s, уход opacity 1→0 + translateY(0→-8px); по окончании
класс show снимается — плашка снова полностью невидима. Каждое следующее
переключение перезапускает анимацию заново с номером реально открытой полосы.
Выход: anna-malboro/daily-03-10-2026.html (очередь подшивки).
Запуск из корня:  python3 worktmp/build_daily_0310_state_v16.py''',
    1))

# --- 2. штамп свежести (первая строка CSS) ----------------------------------
REPL.append((
    '/* SFN-DESIGN-029: day-livemotion · 03.10.2026 */',
    '/* SFN-DESIGN-029: day-pageindicator · 03.10.2026 */',
    1))

# --- 3. CSS: комментарий NAVGLIDE-блока без обещания постоянного счётчика ----
REPL.append((
    '''   содержимое газеты не перекрывают. Счётчик N / 4 — там же, в левом поле под
   стрелкой ←. Узкий экран: боковых полей нет, поэтому весь компактный блок
   ← N / 4 → автоматически встает у верха экрана. Повторные нажатия во время
   перехода гасит блокировка busy. */''',
    '''   содержимое газеты не перекрывают. Узкий экран: боковых полей нет, поэтому
   компактный блок ← → автоматически встает у верха экрана. Повторные нажатия
   во время перехода гасит блокировка busy. Номера полосы рядом со стрелками
   больше нет — он показывается только на время перехода (блок PAGEINDICATOR
   ниже). */''',
    1))

# --- 4. CSS: базовое правило постоянного счётчика удалено --------------------
REPL.append((
    '''.sheetnav .navcount{min-width:52px;text-align:center;font-family:"PT Mono",monospace;
font-size:12px;letter-spacing:.14em;color:var(--mut);-webkit-user-select:none;user-select:none}
''',
    '',
    1))

# --- 5. CSS: десктопное правило счётчика в левом поле удалено ----------------
REPL.append((
    '''html.js-nav .sheetnav .navcount{position:fixed;left:calc(50% - 640px);top:50%;transform:translateY(38px);
width:56px;min-width:0;padding:6px 0;background:var(--paper);border:1.5px solid var(--ink);
color:var(--ink);box-shadow:0 6px 18px rgba(20,24,28,.18)}
''',
    '',
    1))

# --- 6. CSS: блок временного индикатора (после print-правил навигации) -------
IND_CSS = '''/* ==== SFN PAGEINDICATOR · day-pageindicator: временный номер полосы (бриф главреда 04.10.2026) ==== */
/* Постоянный счётчик N / 4 у стрелок удалён целиком — в навигационном баре не
   осталось ни его самого, ни пустого места под него. Номер полосы показывается
   ТОЛЬКО в момент переключения: плашка «ПОЛОСА N / 4» встаёт по центру вверху
   экрана (position:fixed, pointer-events:none, z-index 10000) — места в макете
   газеты не занимает, .sheet не сдвигает, стрелки не перекрывает и клики не
   перехватывает. Стиль газетный: бумажный фон, тёмный моноширинный капс и
   тонкая красная линейка снизу — без рамок, теней и UI-глянца. Один цикл
   pageIndicatorInOut 1.6s ease both: появление opacity 0→1 +
   translateY(-8px→0) (18% ≈ 0.29s), пауза до 70% ≈ 0.83s, уход opacity 1→0 +
   translateY(0→-8px); по окончании анимации класс show снимается — плашка
   гаснет целиком (opacity 0 + visibility:hidden), не показывается до следующего
   переключения, не попадает в выделение текста и в innerText. На
   узких экранах (<1300px), где компактный блок ← → стоит у самого верха,
   плашка опускается под него (top:60px), чтобы не ложиться на кнопки. Без
   скрипта плашки нет вовсе, в печати она скрыта. */
.page-indicator{display:none;position:fixed;top:24px;left:50%;
transform:translateX(-50%) translateY(-8px);opacity:0;pointer-events:none;z-index:10000;
visibility:hidden;font-family:"PT Mono",monospace;font-size:10px;font-weight:700;
letter-spacing:.16em;text-transform:uppercase;color:var(--ink);background:var(--paper);
border-bottom:2px solid var(--ox);padding:7px 12px;-webkit-user-select:none;user-select:none}
html.js-nav .page-indicator{display:block}
html.js-nav .page-indicator.show{visibility:visible;animation:pageIndicatorInOut 1.6s ease both}
@keyframes pageIndicatorInOut{
0%{opacity:0;transform:translateX(-50%) translateY(-8px)}
18%{opacity:1;transform:translateX(-50%) translateY(0)}
70%{opacity:1;transform:translateX(-50%) translateY(0)}
100%{opacity:0;transform:translateX(-50%) translateY(-8px)}}
@media (max-width:1299px){html.js-nav .page-indicator{top:60px}}
@media print{.page-indicator{display:none!important}}
'''

REPL.append((
    '''html.js-nav #newspaper .sheet{display:block!important;position:relative!important;
opacity:1!important;transform:none!important}
}
''',
    '''html.js-nav #newspaper .sheet{display:block!important;position:relative!important;
opacity:1!important;transform:none!important}
}
''' + IND_CSS,
    1))

# --- 7. NAV_JS: комментарий --------------------------------------------------
REPL.append((
    '''   Флаг busy гасит повторные нажатия. Анимации перехода и прокрутки работают
   ВСЕГДА — системная настройка «уменьшить движение» их больше не глушит
   (решение главреда от 04.10.2026); статичной остаётся только печать. */''',
    '''   Флаг busy гасит повторные нажатия. Анимации перехода и прокрутки работают
   ВСЕГДА — системная настройка «уменьшить движение» их больше не глушит
   (решение главреда от 04.10.2026); статичной остаётся только печать.
   Номера полосы рядом со стрелками больше нет: одновременно с переходом
   вверху экрана всплывает временная плашка «ПОЛОСА N / 4» (showPageIndicator)
   — 1.6s на весь цикл (появление → пауза → уход), после чего гаснет сама;
   следующее переключение перезапускает её заново с новым номером. */''',
    1))

# --- 8. NAV_JS: вместо счётчика — индикатор ---------------------------------
REPL.append((
    """  var btnP=document.getElementById('navPrev'),btnN=document.getElementById('navNext'),
      cnt=document.getElementById('navCount');
  if(!btnP||!btnN||!cnt)return;""",
    """  var btnP=document.getElementById('navPrev'),btnN=document.getElementById('navNext'),
      ind=document.getElementById('pageIndicator');
  if(!btnP||!btnN||!ind)return;""",
    1))

REPL.append((
    "  function counter(n){cnt.textContent=(n+1)+' / '+sheets.length;}",
    """  function showPageIndicator(n){
    ind.textContent='ПОЛОСА '+n+' / '+sheets.length;
    ind.classList.remove('show');
    void ind.offsetWidth;
    ind.classList.add('show');
  }""",
    1))

REPL.append((
    '    counter(ni);',
    '    showPageIndicator(ni+1);',
    1))

REPL.append((
    """  root.classList.add('js-nav');
  for(var i=1;i<sheets.length;i++)sheets[i].classList.add('is-off');
  counter(0);
  buttons(0);""",
    """  ind.addEventListener('animationend',function(){ind.classList.remove('show');});
  root.classList.add('js-nav');
  for(var i=1;i<sheets.length;i++)sheets[i].classList.add('is-off');
  buttons(0);""",
    1))

# --- 9. разметка: счётчик из бара убран, плашка добавлена --------------------
REPL.append((
    """P.append('<nav class="sheetnav" aria-label="Полосы выпуска">\\n'
         '<button class="navbtn" id="navPrev" type="button" aria-label="Предыдущая полоса" disabled>←</button>\\n'
         '<span class="navcount" id="navCount" aria-live="polite">1 / 4</span>\\n'
         '<button class="navbtn" id="navNext" type="button" aria-label="Следующая полоса">→</button>\\n'
         '</nav>\\n')""",
    """P.append('<nav class="sheetnav" aria-label="Полосы выпуска">\\n'
         '<button class="navbtn" id="navPrev" type="button" aria-label="Предыдущая полоса" disabled>←</button>\\n'
         '<button class="navbtn" id="navNext" type="button" aria-label="Следующая полоса">→</button>\\n'
         '</nav>\\n')
P.append('<div class="page-indicator" id="pageIndicator" role="status" aria-live="polite" '
         'aria-atomic="true"></div>\\n')""",
    1))

# --- 10. маркер подвала ------------------------------------------------------
REPL.append((
    "P.append('<!-- SFN · 2026 · 029 · day-livemotion -->\\n</body>\\n</html>\\n')",
    "P.append('<!-- SFN · 2026 · 029 · day-pageindicator -->\\n</body>\\n</html>\\n')",
    1))

# --- 11. ассерты сборки ------------------------------------------------------
REPL.append((
    "assert 'SFN-DESIGN-029: day-livemotion' in html and '<!-- SFN · 2026 · 029 · day-livemotion -->' in html",
    '''assert 'SFN-DESIGN-029: day-pageindicator' in html and '<!-- SFN · 2026 · 029 · day-pageindicator -->' in html
assert 'navcount' not in html and 'navCount' not in html, 'постоянный счётчик N / 4 у стрелок уцелел'
assert '1 / 4' not in html, 'в разметке остался текст постоянного счётчика'
assert '.page-indicator{display:none;position:fixed;top:24px;left:50%;' in html, 'нет временного индикатора полосы'
assert 'pointer-events:none;z-index:10000' in html, 'индикатор не fixed-оверлей (может занять место/перехватить клики)'
assert 'visibility:hidden' in html and 'user-select:none' in html, 'погасшая плашка остаётся в выделении/innerText'
assert 'html.js-nav .page-indicator{display:block}' in html, 'индикатор не включается в режиме навигации'
assert 'html.js-nav .page-indicator.show{visibility:visible;animation:pageIndicatorInOut 1.6s ease both}' in html, 'нет анимации индикатора'
assert html.count('translateX(-50%) translateY(-8px)') == 3 and html.count('translateX(-50%) translateY(0)') == 2, \\
    'кейфреймы индикатора сбиты (нужно 0/18/70/100% с центровкой)'
assert 'border-bottom:2px solid var(--ox)' in html, 'у индикатора нет тонкой красной линейки'
assert '@media (max-width:1299px){html.js-nav .page-indicator{top:60px}}' in html, 'на узких экранах индикатор ляжет на кнопки'
assert '@media print{.page-indicator{display:none!important}}' in html, 'индикатор не скрыт в печати'
assert 'function showPageIndicator(n){' in html and 'showPageIndicator(ni+1);' in html, \\
    'индикатор не вызывается при переключении полосы'
assert 'counter(' not in html, 'старая функция счётчика уцелела\'''',
    1))

REPL.append((
    "assert 'id=\"newspaper\"' in html and 'id=\"navPrev\"' in html and 'id=\"navNext\"' in html and 'id=\"navCount\"' in html",
    "assert 'id=\"newspaper\"' in html and 'id=\"navPrev\"' in html and 'id=\"navNext\"' in html and 'id=\"pageIndicator\"' in html",
    1))

# --- 12. финальный print -----------------------------------------------------
REPL.append((
    "print(f'собрано v15 (day-livemotion): {OUT}')",
    "print(f'собрано v16 (day-pageindicator): {OUT}')",
    1))

for i, (old, new, cnt) in enumerate(REPL, 1):
    got = src.count(old)
    assert got == cnt, f'REPL#{i}: найдено {got} вхождений, ожидалось {cnt}: {old[:70]!r}'
    src = src.replace(old, new)

# --- контроль: рабочий код счётчика удалён, литералы остались только в ассертах
for lit in ('navcount', 'navCount'):
    occ, pos = [], src.find(lit)
    while pos != -1:
        line = src[src.rfind('\n', 0, pos) + 1:src.find('\n', pos)]
        occ.append(line.strip())
        pos = src.find(lit, pos + 1)
    assert occ and all(o.startswith('assert') for o in occ), \
        f'в исходнике v16 осталось незапланированное упоминание {lit}: {occ}'
    assert len(occ) == 1, f'{lit}: ожидалось 1 упоминание (в ассерте), найдено {len(occ)}'
assert "'1 / 4'" in src and src.count("'1 / 4'") == 1, 'литерал 1 / 4 должен остаться только в ассерте'
assert 'function counter(' not in src and 'counter(ni)' not in src and 'counter(0)' not in src, \
    'в NAV_JS уцелела функция счётчика'
assert '.sheetnav .navcount' not in src, 'CSS постоянного счётчика уцелел'
assert src.count('page-indicator') >= 8, 'мало правил индикатора'
assert src.count('day-pageindicator') >= 6, 'мало упоминаний нового слага'
assert 'day-livemotion' in src and 'day-navglide' in src, 'исторические имена блоков потеряны'
assert 'showPageIndicator' in src and "ind.classList.remove('show')" in src \
    and 'void ind.offsetWidth;' in src, 'нет перезапуска анимации индикатора'

with open(DST, 'w', encoding='utf-8') as fh:
    fh.write(src)
py_compile.compile(DST, doraise=True)
print('патч day-pageindicator: создан', DST, f'({len(src)} байт), компилируется')
