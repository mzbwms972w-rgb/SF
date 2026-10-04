#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN patch day-navfade (бриф главреда 04.10.2026): v12 (day-flip) → v13 (day-navfade).

Меняются ТОЛЬКО навигация между полосами и анимация переключения:
— 3D-перелистывание удалено полностью (rotateY / perspective / backface-visibility /
  тень листа #flipshade / стопка absolute); полосы возвращаются в обычный поток;
— переход: текущая полоса плавно исчезает (pageFadeOut, opacity 1→0, .4s ease),
  следующая мягко появляется на её месте (page-enter → pageFadeIn: opacity 0→1 +
  очень лёгкий translateY(8px→0), .45s ease); без резких скачков и слайдов;
— в момент смены вид возвращается к началу газеты: новая полоса всегда открывается
  с того же положения экрана, прокрутка после переключения не нужна;
— навигация фиксированная, рядом с газетой: ≥1300px — ← слева от листа и → справа
  (вертикальный центр видимой области, в боковых полях, лист не перекрывают),
  счётчик N / 4 — под левой стрелкой; на узких экранах компактный блок ← N / 4 →
  у верха экрана; без скрипта полосы обычным потоком, навигация скрыта;
— в печати все 4 полосы в потоке, prefers-reduced-motion — мгновенно.

Патч создает worktmp/build_daily_0310_state_v13.py (v12 не трогает) и обновляет
слаг строки 029 в protection/snippets.md. Все замены assert-защищены.
Запуск из корня репо:  python3 worktmp/patch_day_navfade.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'worktmp', 'build_daily_0310_state_v12.py')
DST = os.path.join(ROOT, 'worktmp', 'build_daily_0310_state_v13.py')
SNIP = os.path.join(ROOT, 'protection', 'snippets.md')

src = open(SRC, encoding='utf-8').read()
assert 'day-flip' in src, 'v12 не содержит day-flip — источник неожиданно изменён'


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, f'маркер найден {c} раз (нужно {n}): {old[:80]!r}'
    return s.replace(old, new)


def rep_slice(s, start, end, new):
    i = s.find(start)
    assert i != -1, f'нет начала блока: {start[:60]!r}'
    assert s.find(start, i + 1) == -1, f'начало не уникально: {start[:60]!r}'
    j = s.find(end, i)
    assert j != -1, f'нет конца блока: {end[:60]!r}'
    return s[:i] + new + s[j:]


# ---------------------------------------------------------------- 1. штамп CSS
src = rep(src, '/* SFN-DESIGN-029: day-flip · 03.10.2026 */',
          '/* SFN-DESIGN-029: day-navfade · 03.10.2026 */')

# ---------------------------------------------------------------- 2. CSS-блок
NEW_CSS = '''/* ==== SFN NAVFADE · day-navfade: спокойное переключение полос (бриф главреда 04.10.2026) ==== */
/* Меняются только навигация и способ перехода между полосами; дизайн, тексты,
   фото, размеры материалов, сетка, цвета и композиция не тронуты. Режим одной
   полосы включает скрипт в конце body (html.js-nav): из полос #p1–#p4 видна
   только текущая. Переход: текущая полоса плавно исчезает (pageFadeOut,
   opacity 1→0, .4s ease), затем следующая мягко появляется на её месте
   (page-enter → pageFadeIn: opacity 0→1 + очень лёгкий translateY(8px→0),
   .45s ease). Никаких 3D-поворотов, эффекта бумажного листа, горизонтальных
   слайдов и резких скачков. Без скрипта полосы остаются в обычном потоке,
   как раньше, навигация скрыта.
   Навигация фиксирована рядом с газетой и всегда под рукой во время чтения.
   Широкий экран (≥1300px): ← закреплена слева от листа, → справа, обе примерно
   по центру видимой области, в боковых полях — содержимое газеты не перекрывают;
   счётчик N / 4 — там же, под левой стрелкой. Узкий экран: боковых полей нет,
   поэтому весь компактный блок ← N / 4 → автоматически встает у верха экрана,
   рядом с верхней частью газеты. Повторные нажатия во время перехода гасит
   блокировка busy. */
.sheetnav{display:none;position:fixed;z-index:120;top:8px;left:50%;
transform:translateX(-50%);align-items:center;gap:8px;
background:var(--paper);border:1.5px solid var(--ink);padding:4px 6px;
box-shadow:0 6px 18px rgba(20,24,28,.18)}
.sheetnav .navbtn{width:44px;height:34px;background:var(--paper);border:1.5px solid var(--ink);
color:var(--ink);font-family:"PT Mono",monospace;font-size:16px;line-height:1;padding:0 0 3px;
cursor:pointer;transition:background .2s,color .2s,opacity .2s}
.sheetnav .navbtn:hover:not(:disabled){background:var(--ink);color:var(--paper)}
.sheetnav .navbtn:focus-visible{outline:2px solid var(--ox);outline-offset:2px}
.sheetnav .navbtn:disabled{opacity:.28;cursor:default}
.sheetnav .navcount{min-width:52px;text-align:center;font-family:"PT Mono",monospace;
font-size:12px;letter-spacing:.14em;color:var(--mut);-webkit-user-select:none;user-select:none}
html.js-nav .sheetnav{display:flex}
html.js-nav{overflow-anchor:none}
html.js-nav #newspaper .sheet.is-off{display:none}
html.js-nav #newspaper .sheet.is-on{animation:none}
html.js-nav #newspaper .sheet.is-on *{animation:none}
html.js-nav #newspaper .sheet.is-turn{animation:pageFadeOut .4s ease both}
html.js-nav #newspaper .sheet.page-enter{animation:pageFadeIn .45s ease both}
@keyframes pageFadeOut{from{opacity:1}to{opacity:0}}
@keyframes pageFadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@media (min-width:1300px){
html.js-nav .sheetnav{display:contents}
html.js-nav .sheetnav #navPrev{position:fixed;left:18px;top:50%;transform:translateY(-50%);
width:56px;height:56px;font-size:20px;padding:0 0 4px;box-shadow:0 6px 18px rgba(20,24,28,.18)}
html.js-nav .sheetnav #navNext{position:fixed;right:18px;top:50%;transform:translateY(-50%);
width:56px;height:56px;font-size:20px;padding:0 0 4px;box-shadow:0 6px 18px rgba(20,24,28,.18)}
html.js-nav .sheetnav .navcount{position:fixed;left:18px;top:50%;transform:translateY(38px);
width:56px;min-width:0;padding:6px 0;background:var(--paper);border:1.5px solid var(--ink);
color:var(--ink);box-shadow:0 6px 18px rgba(20,24,28,.18)}
}
@media print{
.sheetnav{display:none!important}
html.js-nav #newspaper .sheet{display:block!important;opacity:1!important;transform:none!important}
}'''

src = rep_slice(src, '/* ==== SFN FLIP · day-flip:', '\n/* ==== мобильная версия', NEW_CSS)

# ------------------------------------------------------------------ 3. JS-блок
NEW_JS = """NAV_JS = '''<script>
/* SFN · 2026 · day-navfade: спокойное переключение полос выпуска. Без бумаги
   и 3D: текущая полоса плавно исчезает (pageFadeOut, 400мс, ease), в момент
   смены вид возвращается к началу газеты, и на её месте с того же положения
   экрана мягко появляется следующая (page-enter → pageFadeIn: opacity 0→1 +
   очень лёгкий translateY(8px→0), 450мс, ease). Прокручивать страницу после
   переключения не нужно: навигация фиксирована и всегда под рукой. Флаг busy
   гасит повторные нажатия во время перехода; prefers-reduced-motion —
   мгновенное переключение. */
(function(){
  var wrap=document.getElementById('newspaper');
  if(!wrap)return;
  var sheets=[].slice.call(wrap.querySelectorAll('.sheet'));
  if(sheets.length!==4)return;
  var btnP=document.getElementById('navPrev'),btnN=document.getElementById('navNext'),
      cnt=document.getElementById('navCount');
  if(!btnP||!btnN||!cnt)return;
  var root=document.documentElement;
  var mqRM=window.matchMedia?window.matchMedia('(prefers-reduced-motion: reduce)'):null;
  var OUT=420,IN=510;
  var cur=0,busy=false;
  function counter(n){cnt.textContent=(n+1)+' / '+sheets.length;}
  function buttons(n){btnP.disabled=(n===0);btnN.disabled=(n===sheets.length-1);}
  function swap(from,to){
    sheets[from].classList.remove('is-turn');
    sheets[from].classList.add('is-off');
    sheets[to].classList.remove('is-off');
    sheets[to].classList.add('is-on','page-enter');
    cur=to;
    window.scrollTo(0,0);
  }
  function go(dir){
    if(busy)return;
    var ni=cur+dir;
    if(ni<0||ni>=sheets.length)return;
    busy=true;
    btnP.disabled=true;btnN.disabled=true;
    counter(ni);
    if(mqRM&&mqRM.matches){
      swap(cur,ni);
      sheets[cur].classList.remove('page-enter');
      buttons(cur);
      busy=false;
      return;
    }
    sheets[cur].classList.add('is-turn');
    setTimeout(function(){
      swap(cur,ni);
      setTimeout(function(){
        sheets[cur].classList.remove('page-enter');
        busy=false;
        buttons(cur);
      },IN);
    },OUT);
  }
  btnP.addEventListener('click',function(){go(-1);});
  btnN.addEventListener('click',function(){go(1);});
  root.classList.add('js-nav');
  for(var i=1;i<sheets.length;i++)sheets[i].classList.add('is-off');
  counter(0);
  buttons(0);
})();
</script>
'''
"""

src = rep_slice(src, "FLIP_JS = '''<script>", '\nP = []', NEW_JS)
src = rep(src, 'P.append(FLIP_JS)', 'P.append(NAV_JS)')

# ------------------------------------------------- 4. assert'ы (до маркера!)
OLD_ASSERTS = """assert 'SFN-DESIGN-029: day-flip' in html and '<!-- SFN · 2026 · 029 · day-flip -->' in html
assert 'perspective:4800px' in html, 'нет perspective на обёртке'
assert 'transform-origin:left center' in html, 'нет петли левого края'
assert 'backface-visibility:hidden' in html, 'нет backface-visibility'
assert html.count('rotateY(-95deg)') >= 2, 'нет поворота листа'
assert 'id="newspaper"' in html and 'id="navPrev"' in html and 'id="navNext"' in html and 'id="navCount"' in html
assert '<script>' in html and 'transitionend' in html and 'setTimeout(settle' in html"""
NEW_ASSERTS = """assert 'SFN-DESIGN-029: day-navfade' in html and '<!-- SFN · 2026 · 029 · day-navfade -->' in html
assert 'pageFadeIn' in html and 'pageFadeOut' in html and 'page-enter' in html, 'нет фейдов полос'
assert 'translateY(8px)' in html, 'нет лёгкого сдвига появления'
assert '.4s ease both' in html and '.45s ease both' in html, 'нет длительностей фейда'
for _bad in ('rotateY', 'perspective', 'backface-visibility', 'transform-origin',
             'flipshade', 'js-flip', 'transitionend'):
    assert _bad not in html, f'3D-перелистывание уцелело: {_bad}'
assert 'position:fixed' in html and 'display:contents' in html, 'навигация не фиксирована'
assert 'id="newspaper"' in html and 'id="navPrev"' in html and 'id="navNext"' in html and 'id="navCount"' in html
assert '<script>' in html and 'setTimeout' in html and 'busy' in html and 'js-nav' in html"""
src = rep(src, OLD_ASSERTS, NEW_ASSERTS)

# ---------------------------------------------------- 5. маркер в конце документа
src = rep(src, '· 029 · day-flip -->', '· 029 · day-navfade -->')

# ---------------------------------------------------- 6. docstring и печать
src = rep(src, '(v12, «Единая сетка дня»', '(v13, «Единая сетка дня»')
src = rep(src, 'Выход: anna-malboro/daily-03-10-2026.html (очередь подшивки).',
          'Навигация полос (day-navfade, бриф главреда 04.10.2026): фиксированные стрелки\n'
          '← → по сторонам листа (на узких экранах — компактный блок у верха экрана),\n'
          'счётчик N / 4; переход — плавное исчезновение старой полосы и появление\n'
          'новой (opacity + translateY(8px→0), 400–450мс, ease), без 3D-перелистывания.\n'
          'Выход: anna-malboro/daily-03-10-2026.html (очередь подшивки).')
src = rep(src, "print(f'собрано v12 (day-grid): {OUT}')",
          "print(f'собрано v13 (day-navfade): {OUT}')")

# ---------------------------------------------------- 7. самопроверка v13
# NEW_ASSERTS легально содержит запрещённые токены как строковые литералы —
# проверяем исходник без этого блока.
assert src.count(NEW_ASSERTS) == 1
src_wo = src.replace(NEW_ASSERTS, '')
for bad in ('js-flip', 'FLIP_JS', 'rotateY', 'perspective', 'backface-visibility',
            'transform-origin', 'flipshade', 'transitionend', 'day-flip', 'no-anim'):
    assert bad not in src_wo, f'в v13 уцелело: {bad}'
for need in ('day-navfade', 'pageFadeIn', 'pageFadeOut', 'page-enter', 'js-nav',
             'display:contents', 'NAV_JS', 'position:fixed', 'v13'):
    assert need in src, f'в v13 не хватает: {need}'
assert src.count('SFN-DESIGN-029: day-navfade') >= 2

with open(DST, 'w', encoding='utf-8') as fh:
    fh.write(src)
print('v13 собран:', DST)

# ------------------------------------------------------------- 8. snippets
sn = open(SNIP, encoding='utf-8').read()
if '| 029 | daily-03-10-2026.html | day-flip |' in sn:
    sn = sn.replace('| 029 | daily-03-10-2026.html | day-flip |',
                    '| 029 | daily-03-10-2026.html | day-navfade |')
    with open(SNIP, 'w', encoding='utf-8') as fh:
        fh.write(sn)
    print('snippets: строка 029 → day-navfade')
else:
    assert '| 029 | daily-03-10-2026.html | day-navfade |' in sn, 'строка 029 в неожиданном состоянии'
    print('snippets: уже day-navfade (идемпотентно)')
print('PATch day-navfade: OK')
