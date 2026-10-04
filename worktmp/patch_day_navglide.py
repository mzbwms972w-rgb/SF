#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN patch day-navglide (бриф главреда 04.10.2026): v13 (day-navfade) → v14 (day-navglide).

Меняются ТОЛЬКО положение стрелок, логика навигации, анимация перехода и прокрутка:
— стрелки ← → больше не прибиты к краям монитора: на широком экране (≥1300px)
  они стоят вплотную к газете — в 24px от краёв листа (лист 1120px, отсчёт от
  центральной оси полосы через calc(50% ∓ 640px)), вертикально по центру видимой
  области, фиксированы (доступны при прокрутке), содержимое не перекрывают;
  счётчик N / 4 — там же, в левом поле под ←; на узких экранах — прежний
  компактный блок ← N / 4 → у верха экрана;
— переход между полосами — настоящий одновременный кроссфейд: уходящая полоса
  становится слоем поверх сцены (.pages-stage = #newspaper, position:relative;
  page-exit → pageExit: opacity 1→0, .6s) и после анимации уходит из активного
  состояния (is-off), входящая появляется в потоке: вперёд — page-enter-next →
  pageEnterNext (opacity 0→1 + translateY(14px→0)), назад — page-enter-prev →
  pageEnterPrev (opacity 0→1 + translateY(-14px→0)), обе .6s
  cubic-bezier(.22,.61,.36,1); без 3D, без горизонтальных слайдов, без мгновенной
  замены через display:none;
— вид плавно (rAF, та же кривая, 600мс) прокручивается к началу новой полосы —
  новая полоса всегда открывается сверху, без резкого скачка; minHeight сцены на
  время перехода фиксирует диапазон прокрутки; в js-nav у полос margin-top:0 —
  начало полосы совпадает с началом документа (ровно scrollY=0);
— busy-блокировка повторных нажатий, prefers-reduced-motion — мгновенно,
  печать — 4 полосы в потоке, без скрипта — обычный поток.

Дизайн, тексты, фото, размеры, сетка, цвета, типографика не тронуты.
Патч создает worktmp/build_daily_0310_state_v14.py (v13 не трогает) и обновляет
слаг строки 029 в protection/snippets.md. Все замены assert-защищены.
Запуск из корня репо:  python3 worktmp/patch_day_navglide.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'worktmp', 'build_daily_0310_state_v13.py')
DST = os.path.join(ROOT, 'worktmp', 'build_daily_0310_state_v14.py')
SNIP = os.path.join(ROOT, 'protection', 'snippets.md')

src = open(SRC, encoding='utf-8').read()
assert 'day-navfade' in src, 'v13 не содержит day-navfade — источник неожиданно изменён'


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
src = rep(src, '/* SFN-DESIGN-029: day-navfade · 03.10.2026 */',
          '/* SFN-DESIGN-029: day-navglide · 03.10.2026 */')

# ------------------------------------------------------------------ 2. CSS-блок
NEW_CSS = '''/* ==== SFN NAVGLIDE · day-navglide: стрелки вплотную к газете + живой кроссфейд полос (бриф главреда 04.10.2026) ==== */
/* Меняются только положение стрелок, логика навигации, анимация перехода между
   полосами и прокрутка; дизайн, тексты, фото, размеры материалов, сетка, цвета,
   типографика и композиция не тронуты. Режим одной полосы включает скрипт в
   конце body (html.js-nav): из полос #p1–#p4 в потоке только текущая.
   Переход — настоящий кроссфейд: уходящая и входящая полосы существуют
   одновременно. Уходящая становится слоем поверх сцены (.pages-stage =
   #newspaper, position:relative; page-exit → pageExit: opacity 1→0, .6s) и
   после анимации снимается из активного состояния (is-off); входящая плавно
   появляется в потоке: вперёд — page-enter-next → pageEnterNext (opacity 0→1 +
   translateY(14px→0)), назад — page-enter-prev → pageEnterPrev (opacity 0→1 +
   translateY(-14px→0)), обе .6s cubic-bezier(.22,.61,.36,1). Одновременно вид
   плавно (та же кривая, 600мс, rAF) возвращается к началу новой полосы — она
   всегда открывается сверху, без резкого скачка. Никаких 3D-поворотов,
   горизонтальных слайдов и мгновенной замены. Без скрипта полосы остаются в
   обычном потоке, как раньше, навигация скрыта.
   Навигация фиксирована рядом с газетой и доступна при прокрутке. Широкий
   экран (≥1300px): ← и → стоят не у краёв монитора, а вплотную к листу — в
   боковых полях, в 24px от краёв полосы (отсчёт от центральной оси: лист
   1120px, calc(50% ∓ 640px)), вертикально по центру видимой области;
   содержимое газеты не перекрывают. Счётчик N / 4 — там же, в левом поле под
   стрелкой ←. Узкий экран: боковых полей нет, поэтому весь компактный блок
   ← N / 4 → автоматически встает у верха экрана. Повторные нажатия во время
   перехода гасит блокировка busy. */
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
html.js-nav #newspaper.pages-stage{position:relative}
html.js-nav #newspaper .sheet{margin-top:0}
html.js-nav #newspaper .sheet.is-off{display:none}
html.js-nav #newspaper .sheet.is-on{animation:none}
html.js-nav #newspaper .sheet.is-on *{animation:none}
html.js-nav #newspaper .sheet.page-exit{position:absolute;top:0;left:0;right:0;z-index:3;
pointer-events:none;animation:pageExit .6s cubic-bezier(.22,.61,.36,1) both}
html.js-nav #newspaper .sheet.page-enter-next{z-index:2;
animation:pageEnterNext .6s cubic-bezier(.22,.61,.36,1) both}
html.js-nav #newspaper .sheet.page-enter-prev{z-index:2;
animation:pageEnterPrev .6s cubic-bezier(.22,.61,.36,1) both}
@keyframes pageEnterNext{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes pageEnterPrev{from{opacity:0;transform:translateY(-14px)}to{opacity:1;transform:translateY(0)}}
@keyframes pageExit{from{opacity:1}to{opacity:0}}
@media (min-width:1300px){
html.js-nav .sheetnav{display:contents}
html.js-nav .sheetnav #navPrev{position:fixed;left:calc(50% - 640px);top:50%;transform:translateY(-50%);
width:56px;height:56px;font-size:20px;padding:0 0 4px;box-shadow:0 6px 18px rgba(20,24,28,.18)}
html.js-nav .sheetnav #navNext{position:fixed;right:calc(50% - 640px);top:50%;transform:translateY(-50%);
width:56px;height:56px;font-size:20px;padding:0 0 4px;box-shadow:0 6px 18px rgba(20,24,28,.18)}
html.js-nav .sheetnav .navcount{position:fixed;left:calc(50% - 640px);top:50%;transform:translateY(38px);
width:56px;min-width:0;padding:6px 0;background:var(--paper);border:1.5px solid var(--ink);
color:var(--ink);box-shadow:0 6px 18px rgba(20,24,28,.18)}
}
@media print{
.sheetnav{display:none!important}
html.js-nav #newspaper{min-height:0!important}
html.js-nav #newspaper .sheet{display:block!important;position:relative!important;
opacity:1!important;transform:none!important}
}'''

src = rep_slice(src, '/* ==== SFN NAVFADE · day-navfade:', '\n/* ==== мобильная версия', NEW_CSS)

# ------------------------------------------------------------------ 3. JS-блок
NEW_JS = """NAV_JS = '''<script>
/* SFN · 2026 · day-navglide: живое переключение полос выпуска. Уходящая и
   входящая полосы существуют одновременно: уходящая становится слоем поверх
   сцены и плавно исчезает (page-exit → pageExit: opacity 1→0, 600мс), входящая
   появляется в потоке — вперёд снизу вверх (page-enter-next → pageEnterNext:
   opacity 0→1 + translateY(14px→0)), назад сверху вниз (page-enter-prev →
   pageEnterPrev: opacity 0→1 + translateY(-14px→0)), обе 600мс
   cubic-bezier(.22,.61,.36,1). Вид параллельно плавно возвращается к началу
   новой полосы (rAF, та же кривая, 600мс) — она всегда открывается сверху,
   без резкого скачка. Высота сцены на время перехода фиксируется minHeight,
   чтобы диапазон прокрутки не схлопывался; после завершения анимации уходящая
   полоса снимается из активного состояния (is-off), классы перехода чистятся.
   Флаг busy гасит повторные нажатия; prefers-reduced-motion — мгновенное
   переключение. */
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
  var DUR=600;
  var cur=0,busy=false,raf=0;
  function counter(n){cnt.textContent=(n+1)+' / '+sheets.length;}
  function buttons(n){btnP.disabled=(n===0);btnN.disabled=(n===sheets.length-1);}
  function cb(t,a,b){var u=1-t;return 3*u*u*t*a+3*u*t*t*b+t*t*t;}
  function ease(x){var lo=0,hi=1,t,i;
    for(i=0;i<20;i++){t=(lo+hi)/2;if(cb(t,.22,.36)<x)lo=t;else hi=t;}
    return cb((lo+hi)/2,.61,1);}
  function glideTop(){
    var y0=window.pageYOffset||root.scrollTop||0,t0=null;
    if(y0<=0)return;
    if(raf)cancelAnimationFrame(raf);
    function step(ts){
      if(t0===null)t0=ts;
      var p=(ts-t0)/DUR;
      if(p>=1){window.scrollTo(0,0);raf=0;return;}
      window.scrollTo(0,Math.round(y0*(1-ease(p))));
      raf=requestAnimationFrame(step);
    }
    raf=requestAnimationFrame(step);
  }
  function settle(from,to){
    if(raf){cancelAnimationFrame(raf);raf=0;}
    window.scrollTo(0,0);
    sheets[from].classList.remove('is-on','page-exit');
    sheets[from].classList.add('is-off');
    sheets[to].classList.remove('page-enter-next','page-enter-prev');
    wrap.style.minHeight='';
    busy=false;
    buttons(to);
  }
  function go(dir){
    if(busy)return;
    var ni=cur+dir;
    if(ni<0||ni>=sheets.length)return;
    busy=true;
    btnP.disabled=true;btnN.disabled=true;
    counter(ni);
    if(mqRM&&mqRM.matches){
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
    var from=cur;
    cur=ni;
    var vh=window.innerHeight||root.clientHeight;
    var y0=window.pageYOffset||root.scrollTop||0;
    var oldH=sheets[from].offsetHeight;
    sheets[ni].classList.remove('is-off');
    sheets[ni].classList.add('is-on',dir>0?'page-enter-next':'page-enter-prev');
    var newH=sheets[ni].offsetHeight;
    wrap.style.minHeight=Math.max(oldH,newH,y0+vh)+'px';
    sheets[from].classList.add('page-exit');
    glideTop();
    setTimeout(function(){settle(from,ni);},DUR+120);
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

src = rep_slice(src, "NAV_JS = '''<script>", '\nP = []', NEW_JS)

# ------------------------------------------------- 4. assert'ы (до маркера!)
OLD_ASSERTS = """assert 'SFN-DESIGN-029: day-navfade' in html and '<!-- SFN · 2026 · 029 · day-navfade -->' in html
assert 'pageFadeIn' in html and 'pageFadeOut' in html and 'page-enter' in html, 'нет фейдов полос'
assert 'translateY(8px)' in html, 'нет лёгкого сдвига появления'
assert '.4s ease both' in html and '.45s ease both' in html, 'нет длительностей фейда'
for _bad in ('rotateY', 'perspective', 'backface-visibility', 'transform-origin',
             'flipshade', 'js-flip', 'transitionend'):
    assert _bad not in html, f'3D-перелистывание уцелело: {_bad}'
assert 'position:fixed' in html and 'display:contents' in html, 'навигация не фиксирована'
assert 'id="newspaper"' in html and 'id="navPrev"' in html and 'id="navNext"' in html and 'id="navCount"' in html
assert '<script>' in html and 'setTimeout' in html and 'busy' in html and 'js-nav' in html"""
NEW_ASSERTS = """assert 'SFN-DESIGN-029: day-navglide' in html and '<!-- SFN · 2026 · 029 · day-navglide -->' in html
assert '@keyframes pageEnterNext{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}' in html, 'нет входа вперёд (translateY 14px→0)'
assert '@keyframes pageEnterPrev{from{opacity:0;transform:translateY(-14px)}to{opacity:1;transform:translateY(0)}}' in html, 'нет входа назад (translateY -14px→0)'
assert '@keyframes pageExit{from{opacity:1}to{opacity:0}}' in html, 'нет слоя исчезновения'
assert html.count('.6s cubic-bezier(.22,.61,.36,1) both') == 3, 'длительность/кривая перехода сбиты'
assert 'page-enter-next' in html and 'page-enter-prev' in html and 'page-exit' in html, 'нет состояний перехода полос'
assert 'class="pages-stage"' in html and 'html.js-nav #newspaper.pages-stage{position:relative}' in html, 'нет сцены полос'
assert 'left:calc(50% - 640px)' in html and 'right:calc(50% - 640px)' in html, 'стрелки не вплотную к листу'
for _bad in ('rotateY', 'perspective', 'backface-visibility', 'transform-origin',
             'flipshade', 'js-flip', 'transitionend', 'pageFadeIn', 'pageFadeOut',
             'is-turn', 'left:18px', 'right:18px'):
    assert _bad not in html, f'старая навигация/3D уцелели: {_bad}'
for _kf in ('pageEnterNext', 'pageEnterPrev', 'pageExit'):
    _i = html.find('@keyframes ' + _kf)
    assert _i != -1 and 'translateX' not in html[_i:_i + 200] \\
        and 'rotate' not in html[_i:_i + 200] and 'scale' not in html[_i:_i + 200], \\
        f'слайд/поворот/масштаб в {_kf}'
assert 'position:fixed' in html and 'display:contents' in html, 'навигация не фиксирована'
assert 'requestAnimationFrame' in html and 'minHeight' in html and 'DUR=600' in html, 'нет плавной прокрутки к началу полосы'
assert 'id="newspaper"' in html and 'id="navPrev"' in html and 'id="navNext"' in html and 'id="navCount"' in html
assert '<script>' in html and 'setTimeout' in html and 'busy' in html and 'js-nav' in html"""
src = rep(src, OLD_ASSERTS, NEW_ASSERTS)

# ---------------------------------------------------- 5. маркер в конце документа
src = rep(src, '· 029 · day-navfade -->', '· 029 · day-navglide -->')

# ------------------------------------------------- 6. сцена в разметке (div)
src = rep(src, """P.append('<div id="newspaper">\\n')""",
          """P.append('<div id="newspaper" class="pages-stage">\\n')""")

# ---------------------------------------------------- 7. docstring и печать
src = rep(src, '(v13, «Единая сетка дня»', '(v14, «Единая сетка дня»')
src = rep(src, '''Навигация полос (day-navfade, бриф главреда 04.10.2026): фиксированные стрелки
← → по сторонам листа (на узких экранах — компактный блок у верха экрана),
счётчик N / 4; переход — плавное исчезновение старой полосы и появление
новой (opacity + translateY(8px→0), 400–450мс, ease), без 3D-перелистывания.''',
          '''Навигация полос (day-navglide, бриф главреда 04.10.2026): фиксированные стрелки
← → вплотную к газете — в 24px от краёв листа, по центру видимой области (на
узких экранах — компактный блок у верха экрана), счётчик N / 4; переход —
одновременный кроссфейд: уходящая полоса исчезает слоем поверх сцены, входящая
появляется (opacity 0→1 + translateY(±14px→0), 600мс, cubic-bezier(.22,.61,.36,1)),
прокрутка к началу новой полосы — плавная, той же кривой; без 3D-перелистывания.''')
src = rep(src, 'Запуск из корня:  python3 worktmp/build_daily_0310_state_v12.py',
          'Запуск из корня:  python3 worktmp/build_daily_0310_state_v14.py')
src = rep(src, "print(f'собрано v13 (day-navfade): {OUT}')",
          "print(f'собрано v14 (day-navglide): {OUT}')")

# ---------------------------------------------------- 8. самопроверка v14
# NEW_ASSERTS легально содержит запрещённые токены как строковые литералы —
# проверяем исходник без этого блока.
assert src.count(NEW_ASSERTS) == 1
src_wo = src.replace(NEW_ASSERTS, '')
for bad in ('day-navfade', 'pageFadeIn', 'pageFadeOut', 'is-turn', '.sheet.page-enter{',
            'left:18px', 'right:18px', 'js-flip', 'FLIP_JS', 'rotateY', 'perspective',
            'backface-visibility', 'transform-origin', 'flipshade', 'transitionend'):
    assert bad not in src_wo, f'в v14 уцелело: {bad}'
for need in ('day-navglide', 'pageEnterNext', 'pageEnterPrev', 'pageExit',
             'page-enter-next', 'page-enter-prev', 'page-exit', 'pages-stage',
             'calc(50% - 640px)', 'requestAnimationFrame', 'minHeight', 'DUR=600',
             'translateY(14px)', 'translateY(-14px)', 'cubic-bezier(.22,.61,.36,1)',
             'js-nav', 'display:contents', 'NAV_JS', 'position:fixed', 'v14'):
    assert need in src, f'в v14 не хватает: {need}'
assert src.count('SFN-DESIGN-029: day-navglide') >= 2

with open(DST, 'w', encoding='utf-8') as fh:
    fh.write(src)
print('v14 собран:', DST)

# ------------------------------------------------------------- 9. snippets
sn = open(SNIP, encoding='utf-8').read()
if '| 029 | daily-03-10-2026.html | day-navfade |' in sn:
    sn = sn.replace('| 029 | daily-03-10-2026.html | day-navfade |',
                    '| 029 | daily-03-10-2026.html | day-navglide |')
    with open(SNIP, 'w', encoding='utf-8') as fh:
        fh.write(sn)
    print('snippets: строка 029 → day-navglide')
else:
    assert '| 029 | daily-03-10-2026.html | day-navglide |' in sn, 'строка 029 в неожиданном состоянии'
    print('snippets: уже day-navglide (идемпотентно)')
