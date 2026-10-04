#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN: патч day-flip — реалистичное перелистывание полос выпуска 03.10.2026.

Бриф главреда (04.10.2026): меняется ТОЛЬКО способ перехода между полосами —
дизайн, тексты, фотографии, размеры материалов, сетка, цвета и композиция не
трогаются. Механика: #p1–#p4 складываются в стопку внутри обёртки #newspaper
(режим включает скрипт классом html.js-flip; без скрипта полосы идут обычным
потоком, как раньше, навигация скрыта). Перелистывание — поворот листа вокруг
левого края (transform-origin:left center, rotateY), perspective на обёртке,
800мс, backface-visibility убирает лист за вертикалью — полоса физически
уходит, а не гаснет через opacity. Лёгкая тень во время переворота, блокировка
повторных нажатий (busy + disabled), счётчик «N / 4», кнопки ← →.
Патч идемпотентен: повторный запуск ничего не ломает.
Запуск из корня:  python3 worktmp/patch_day_flip.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, 'worktmp', 'build_daily_0310_state_v12.py')
S = os.path.join(ROOT, 'protection', 'snippets.md')

src = open(B, encoding='utf-8').read()
if 'day-flip' in src:
    print('patch_day_flip: уже применён, пропускаю')
    raise SystemExit(0)

# ============================== CSS переворота ==============================
FLIP_CSS = """/* ==== SFN FLIP · day-flip: перелистывание полос (бумажный лист, петля слева) ==== */
/* Меняется только способ перехода между полосами; дизайн, тексты, фото,
   размеры материалов, сетка, цвета и композиция не тронуты. Стопочный режим
   включает скрипт в конце body (html.js-flip): полосы #p1–#p4 лежат в общей
   стопке, высота обёртки равна высоте текущей полосы и плавно ведётся к
   следующей. Без скрипта полосы остаются в обычном потоке, навигация скрыта.
   Перелистывание: rotateY вокруг левого края (transform-origin:left center)
   в perspective обёртки, 800мс, плавная кривая; за вертикалью лист физически
   уходит из стопки (backface-visibility:hidden) — не fade и не слайдер.
   Лёгкая тень переворота: двойной box-shadow листа в воздухе + градиент
   #flipshade на открываемой полосе. Повторные нажатия гасит блокировка busy. */
.sheetnav{display:none;max-width:1120px;margin:30px auto 0;padding:0 12px;
align-items:center;justify-content:center;gap:22px}
.sheetnav .navbtn{width:58px;height:42px;background:var(--paper);border:1.5px solid var(--ink);
color:var(--ink);font-family:"PT Mono",monospace;font-size:18px;line-height:1;padding:0 0 4px;
cursor:pointer;transition:background .2s,color .2s,opacity .2s}
.sheetnav .navbtn:hover:not(:disabled){background:var(--ink);color:var(--paper)}
.sheetnav .navbtn:focus-visible{outline:2px solid var(--ox);outline-offset:3px}
.sheetnav .navbtn:disabled{opacity:.28;cursor:default}
.sheetnav .navcount{min-width:72px;text-align:center;font-family:"PT Mono",monospace;
font-size:12px;letter-spacing:.16em;color:var(--mut);-webkit-user-select:none;user-select:none}
html.js-flip .sheetnav{display:flex}
html.js-flip #newspaper{position:relative;perspective:4800px;overflow-x:clip;
transition:height .8s cubic-bezier(.4,.1,.25,1)}
html.js-flip #newspaper .sheet{position:absolute;top:0;left:0;right:0;margin:0 auto;z-index:1;
transform-origin:left center;backface-visibility:hidden;
box-shadow:0 16px 40px rgba(20,24,28,.22),-22px 18px 56px rgba(26,23,20,0);
transition:transform .8s cubic-bezier(.4,.1,.25,1),box-shadow .5s ease,visibility 0s}
html.js-flip #newspaper .sheet.is-on{z-index:2}
html.js-flip #newspaper .sheet.is-turn{z-index:4;will-change:transform;
box-shadow:0 16px 40px rgba(20,24,28,.22),-22px 18px 56px rgba(26,23,20,.3);
transition:transform .8s cubic-bezier(.4,.1,.25,1),box-shadow .35s ease,visibility 0s}
html.js-flip #newspaper .sheet.turn-next{transform:rotateY(-95deg)}
html.js-flip #newspaper .sheet.is-off{visibility:hidden;transform:rotateY(-95deg)}
html.no-anim #newspaper,html.no-anim #newspaper .sheet{transition:none!important}
#flipshade{position:absolute;top:0;left:0;right:0;bottom:0;z-index:3;pointer-events:none;
opacity:0;background:linear-gradient(to right,rgba(26,23,20,.22),rgba(26,23,20,.1) 30%,rgba(26,23,20,0) 60%)}
#flipshade.shading{animation:flipshade .8s cubic-bezier(.4,.1,.25,1)}
@keyframes flipshade{0%{opacity:0}40%{opacity:1}100%{opacity:0}}
@media (prefers-reduced-motion:reduce){#flipshade.shading{animation:none;opacity:0}}
@media print{
.sheetnav,#flipshade{display:none!important}
html.js-flip #newspaper{height:auto!important;perspective:none;overflow:visible;transition:none}
html.js-flip #newspaper .sheet{position:static;visibility:visible!important;transform:none!important;
margin:0 auto 26px;box-shadow:0 16px 40px rgba(20,24,28,.22);transition:none}
html.js-flip #newspaper .sheet+.sheet{margin-top:34px}
}
"""

# ============================== JS переворота ==============================
JS = r'''<script>
/* SFN · 2026 · day-flip: перелистывание полос выпуска. Бумажный лист на петле
   у левого края: rotateY вокруг left center в perspective обёртки; за 90° лист
   убирает backface-visibility — полоса физически уходит за следующую. Состояние
   защищает флаг busy: повторные нажатия во время переворота игнорируются. */
(function(){
  var wrap=document.getElementById('newspaper');
  if(!wrap)return;
  var sheets=[].slice.call(wrap.querySelectorAll('.sheet'));
  if(sheets.length!==4)return;
  var btnP=document.getElementById('navPrev'),btnN=document.getElementById('navNext'),
      cnt=document.getElementById('navCount');
  if(!btnP||!btnN||!cnt)return;
  var RM=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var DUR=800,FALL=DUR+250;
  var cur=0,busy=false;
  var shade=document.createElement('div');
  shade.id='flipshade';
  shade.setAttribute('aria-hidden','true');
  wrap.appendChild(shade);
  var root=document.documentElement;
  function fit(){
    if(!busy&&sheets[cur])wrap.style.height=sheets[cur].offsetHeight+'px';
  }
  function navState(n){
    cnt.textContent=(n+1)+' / '+sheets.length;
    btnP.disabled=(n===0);
    btnN.disabled=(n===sheets.length-1);
  }
  function scrollUp(){
    var y=Math.max(0,Math.round(wrap.getBoundingClientRect().top+
      (window.scrollY||window.pageYOffset))-14);
    if(Math.abs((window.scrollY||window.pageYOffset)-y)>8){
      window.scrollTo({top:y,behavior:RM?'auto':'smooth'});
    }
  }
  function go(dir){
    if(busy)return;
    var ni=cur+dir;
    if(ni<0||ni>=sheets.length)return;
    busy=true;
    btnP.disabled=true;btnN.disabled=true;
    var A=sheets[cur],B=sheets[ni];
    var hB=B.offsetHeight;
    A.style.animation='none';B.style.animation='none';
    wrap.style.height=hB+'px';
    scrollUp();
    cur=ni;
    navState(ni);
    shade.classList.remove('shading');
    void shade.offsetWidth;
    shade.classList.add('shading');
    var moving;
    if(dir>0){
      B.classList.add('is-on');
      A.classList.add('is-turn');
      void A.offsetWidth;
      A.classList.add('turn-next');
      moving=A;
    }else{
      B.classList.add('is-on','is-turn');
      void B.offsetWidth;
      B.classList.remove('is-off');
      moving=B;
    }
    var done=false;
    function settle(){
      if(done)return;
      done=true;
      shade.classList.remove('shading');
      A.style.transition='none';
      A.classList.remove('is-turn','turn-next','is-on');
      A.classList.add('is-off');
      void A.offsetWidth;
      A.style.transition='';
      if(dir<0)B.classList.remove('is-turn');
      busy=false;
      navState(cur);
      fit();
    }
    moving.addEventListener('transitionend',function(ev){
      if(ev.target===moving&&ev.propertyName==='transform')settle();
    });
    setTimeout(settle,FALL);
  }
  btnP.addEventListener('click',function(){go(-1);});
  btnN.addEventListener('click',function(){go(1);});
  window.addEventListener('resize',fit);
  window.addEventListener('load',fit);
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fit);
  root.classList.add('no-anim');
  root.classList.add('js-flip');
  sheets[0].classList.add('is-on');
  for(var i=1;i<sheets.length;i++)sheets[i].classList.add('is-off');
  fit();
  navState(0);
  void wrap.offsetWidth;
  requestAnimationFrame(function(){
    requestAnimationFrame(function(){root.classList.remove('no-anim');});
  });
})();
</script>
'''

NAV = """P.append('</div>\\n')
P.append('<nav class="sheetnav" aria-label="Полосы выпуска">\\n'
         '<button class="navbtn" id="navPrev" type="button" aria-label="Предыдущая полоса" disabled>←</button>\\n'
         '<span class="navcount" id="navCount" aria-live="polite">1 / 4</span>\\n'
         '<button class="navbtn" id="navNext" type="button" aria-label="Следующая полоса">→</button>\\n'
         '</nav>\\n')
P.append(FLIP_JS)
"""

Q3 = chr(39) * 3


def rep(old, new):
    global src
    c = src.count(old)
    assert c == 1, f'якорь найден {c} раз(а) вместо 1: {old[:80]!r}'
    src = src.replace(old, new)


# 1) слаг штампа SFN-DESIGN-029
rep(r'''CSS = """/* SFN-DESIGN-029: day-motion · 03.10.2026 */''',
    r'''CSS = """/* SFN-DESIGN-029: day-flip · 03.10.2026 */''')

# 2) CSS переворота — перед мобильным блоком
rep('/* ==== мобильная версия: одна колонка, сценарии складываются ==== */',
    FLIP_CSS + '/* ==== мобильная версия: одна колонка, сценарии складываются ==== */')

# 3) константа FLIP_JS — перед сборкой страницы
rep('\nP = []\n', '\nFLIP_JS = ' + Q3 + JS + Q3 + '\n\nP = []\n')

# 4) обёртка стопки сразу после <body>
rep(r"""P.append('</style>\n</head>\n<body>\n')""",
    r"""P.append('</style>\n</head>\n<body>\n')""" + '\n'
    + r"""P.append('<div id="newspaper">\n')""")

# 5) закрытие обёртки + навигация + скрипт перед маркером
rep(r"""P.append('<!-- SFN · 2026 · 029 · day-motion -->\n</body>\n</html>\n')""",
    NAV + r"""P.append('<!-- SFN · 2026 · 029 · day-flip -->\n</body>\n</html>\n')""")

# 6) самопроверка сборщика: штамп/маркер day-flip + обязательные свойства переворота
rep("assert 'SFN-DESIGN-029: day-motion' in html and '<!-- SFN · 2026 · 029 · day-motion -->' in html",
    """assert 'SFN-DESIGN-029: day-flip' in html and '<!-- SFN · 2026 · 029 · day-flip -->' in html
assert 'perspective:4800px' in html, 'нет perspective на обёртке'
assert 'transform-origin:left center' in html, 'нет петли левого края'
assert 'backface-visibility:hidden' in html, 'нет backface-visibility'
assert html.count('rotateY(-95deg)') >= 2, 'нет поворота листа'
assert 'id="newspaper"' in html and 'id="navPrev"' in html and 'id="navNext"' in html and 'id="navCount"' in html
assert '<script>' in html and 'transitionend' in html and 'setTimeout(settle' in html
for _pid in ('p1', 'p2', 'p3', 'p4'):
    assert '<section class="sheet" id="' + _pid + '">' in html, 'нет полосы ' + _pid""")

open(B, 'w', encoding='utf-8').write(src)

# 7) строка 029 в снаппетах
sn = open(S, encoding='utf-8').read()
old_row = '| 029 | daily-03-10-2026.html | day-motion |'
assert sn.count(old_row) == 1, 'строка 029 в snippets.md не найдена'
sn = sn.replace(old_row, '| 029 | daily-03-10-2026.html | day-flip |')
open(S, 'w', encoding='utf-8').write(sn)

print('patch_day_flip: применён (builder v12 + snippets.md, слаг day-flip)')
