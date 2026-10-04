#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN QA day-pageindicator: временный номер полосы вместо постоянного счётчика.

Проверяет статику HTML (штамп day-pageindicator; постоянный счётчик N / 4 удалён
целиком — ни разметки, ни CSS, ни JS; кроссфейд pageEnterNext/pageEnterPrev/
pageExit и calc-позиции стрелок сохранены; плашка .page-indicator: fixed,
top:24px, центр, pointer-events:none, z-index 10000, газетный стиль, цикл
pageIndicatorInOut 1.6s ease both, в печати скрыта) и поведение в Chromium:
— в покое: счётчика нет нигде (ни у стрелок, ни в левом поле, ни в мобильном
  баре), плашка невидима (opacity 0, без класса show), пустого места в баре нет;
— плашка не занимает места в макете и не сдвигает .sheet (геометрия полосы
  идентична при видимой и невидимой плашке и совпадает с потоковой версией без JS);
— при клике → и ← плашка появляется ВВЕРХУ по центру с номером реально открытой
  полосы («ПОЛОСА 2 / 4», «ПОЛОСА 3 / 4»…), покадровым rAF-сэмплером замерены
  появление (opacity 0→1 + translateY(-8px→0)), пауза ~0.7–0.9s и уход
  (opacity 1→0 + translateY(0→-8px)), весь цикл 1.3–1.8s; после исчезновения
  класс show снят, opacity 0, экран в этой области байт-в-байт как до перехода;
— следующее переключение перезапускает анимацию заново с новым номером;
— кроссфейд полос, плавная прокрутка, hammer, края, ширины 1300/1100/390,
  печать, «моушен всегда жив» (в т.ч. при prefers-reduced-motion:reduce) —
  сохранены; консоль чиста;
— идентичность полос в покое синхронному контролю day-livemotion (bea6f5f).
В конце — рендеры v20_* (в т.ч. плашка в момент перехода) и композит preview-all.png.
Запуск из корня репо:  python3 worktmp/qa_pageindicator.py
"""
import os
import re
import subprocess
import sys

ROOT = os.getcwd()
HTML = os.path.join(ROOT, 'anna-malboro', 'daily-03-10-2026.html')
REND = os.path.join(os.path.dirname(ROOT), 'renders')
SCRATCH = os.path.join(os.path.dirname(ROOT), 'scratch_qa')
URL = 'file://' + HTML

OK, BAD = [], []


def chk(name, cond, detail=''):
    (OK if cond else BAD).append(name)
    print(('PASS  ' if cond else 'FAIL  ') + name + (('  · ' + str(detail)) if detail else ''))


h = open(HTML, encoding='utf-8').read()

# контрольная версия (day-livemotion, опубликована) — из истории git
OLD_SHA = 'bea6f5f'
os.makedirs(SCRATCH, exist_ok=True)
os.makedirs(REND, exist_ok=True)
OLD_HTML = os.path.join(SCRATCH, 'old_day_livemotion.html')
HAVE_OLD = True
try:
    blob = subprocess.run(['git', '-C', ROOT, 'show',
                           f'{OLD_SHA}:anna-malboro/daily-03-10-2026.html'],
                          capture_output=True, check=True).stdout
    with open(OLD_HTML, 'wb') as fh:
        fh.write(blob)
except Exception as e:  # noqa: BLE001
    HAVE_OLD = False
    print('WARN: контрольная версия day-livemotion недоступна:', e)

# ------------------------------ статика -------------------------------------
chk('S1 штамп day-pageindicator', '/* SFN-DESIGN-029: day-pageindicator · 03.10.2026 */' in h)
chk('S2 маркер day-pageindicator', '<!-- SFN · 2026 · 029 · day-pageindicator -->' in h)
chk('S3 вход вперёд: pageEnterNext translateY(14px→0)',
    '@keyframes pageEnterNext{from{opacity:0;transform:translateY(14px)}'
    'to{opacity:1;transform:translateY(0)}}' in h
    and 'animation:pageEnterNext .6s cubic-bezier(.22,.61,.36,1) both' in h)
chk('S4 вход назад: pageEnterPrev translateY(-14px→0)',
    '@keyframes pageEnterPrev{from{opacity:0;transform:translateY(-14px)}'
    'to{opacity:1;transform:translateY(0)}}' in h
    and 'animation:pageEnterPrev .6s cubic-bezier(.22,.61,.36,1) both' in h)
chk('S5 уход: page-exit — слой absolute поверх сцены, pageExit opacity 1→0',
    '@keyframes pageExit{from{opacity:1}to{opacity:0}}' in h
    and 'html.js-nav #newspaper .sheet.page-exit{position:absolute;top:0;left:0;right:0;z-index:3;' in h
    and 'animation:pageExit .6s cubic-bezier(.22,.61,.36,1) both' in h)
chk('S6 сцена и durations: pages-stage position:relative, ровно 3×.6s',
    '<div id="newspaper" class="pages-stage">' in h
    and 'html.js-nav #newspaper.pages-stage{position:relative}' in h
    and h.count('.6s cubic-bezier(.22,.61,.36,1) both') == 3)
chk('S7 3D/слайды/старые фейды удалены полностью',
    all(t not in h for t in ('rotateY', 'perspective', 'backface-visibility',
                             'transform-origin', 'flipshade', 'js-flip', 'transitionend',
                             'pageFadeIn', 'pageFadeOut', 'is-turn',
                             'left:18px', 'right:18px')))
kf_wins = []
for kf in ('pageEnterNext', 'pageEnterPrev', 'pageExit'):
    i = h.find('@keyframes ' + kf)
    kf_wins.append(h[i:i + 200])
chk('S8 в кейфреймах полос только opacity/translateY (нет translateX/rotate/scale)',
    len(kf_wins) == 3 and all(('translateX' not in w and 'rotate' not in w
                               and 'scale' not in w) for w in kf_wins))
_mb_i = h.index('@media (min-width:1300px)')
mb = h[_mb_i:h.index('.page-indicator', _mb_i)]
chk('S9 стрелки у краёв листа через calc от центральной оси (не left:0/right:0)',
    'left:calc(50% - 640px)' in mb and 'right:calc(50% - 640px)' in mb
    and 'top:50%;transform:translateY(-50%)' in mb
    and 'left:0' not in mb and 'right:0;' not in mb)
chk('S10 навигация фиксирована; мобильный компактный блок сохранён',
    '.sheetnav{display:none;position:fixed;z-index:120;top:8px;left:50%;' in h
    and 'html.js-nav .sheetnav{display:flex}' in h
    and 'html.js-nav .sheetnav{display:contents}' in mb)
chk('S11 ПОСТОЯННЫЙ счётчик N / 4 удалён целиком (разметка+CSS+JS)',
    'navcount' not in h and 'navCount' not in h and '1 / 4' not in h
    and 'counter(' not in h and h.count('class="navbtn"') == 2)
chk('S12 полосы и стрелки на месте, плашка в разметке есть',
    'id="newspaper"' in h and h.count('<section class="sheet" id="p') == 4
    and all(x in h for x in ('id="navPrev"', 'id="navNext"', 'id="pageIndicator"'))
    and '<div class="page-indicator" id="pageIndicator" role="status" aria-live="polite" '
        'aria-atomic="true"></div>' in h)
chk('S13 нет inline-стилей', 'style="' not in h)
chk('S14 12 кадров на месте', h.count('data:image/jpeg;base64,') == 12
    and all(f'id="a{n:02d}"' in h for n in range(1, 13)))
chk('S15 оболочка/палитра не тронуты',
    ':root{--paper:#f2ede3;--ink:#1a1714;--ox:#9e2b25' in h
    and '.sheet{max-width:1120px' in h and h.count(':root{') == 2)
chk('S16 day-motion загрузки сохранён',
    'sfn-rise' in h and '#p4.sheet{animation-delay:.18s}' in h
    and '.ph:hover img{transform:scale(1.02)}' in h)
chk('S17 печать: полосы в потоке, сцена без minHeight, навигация и плашка скрыты',
    '.sheetnav{display:none!important}' in h
    and '@media print{.page-indicator{display:none!important}}' in h
    and 'html.js-nav #newspaper{min-height:0!important}' in h
    and 'html.js-nav #newspaper .sheet{display:block!important;position:relative!important;' in h
    and 'opacity:1!important;transform:none!important' in h)
chk('S18 логика переключения и плавной прокрутки сохранена',
    all(x in h for x in ('js-nav', 'busy', 'setTimeout', 'requestAnimationFrame',
                         'cancelAnimationFrame', 'minHeight', 'DUR=600', 'cb(t,.22,.36)',
                         'scrollTo(0,0)', "querySelectorAll('.sheet')",
                         'page-exit', 'page-enter-next', 'page-enter-prev', 'is-off',
                         'html.js-nav #newspaper .sheet{margin-top:0}')))
chk('S19 RM-гейтинг по-прежнему отсутствует (моушен жив всегда)',
    'prefers-reduced-motion' not in h and 'mqRM' not in h and 'matchMedia' not in h)
chk('S20 плашка: fixed-оверлей вверху по центру, место в макете не занимает, в покое скрыта',
    '.page-indicator{display:none;position:fixed;top:24px;left:50%;\n'
    'transform:translateX(-50%) translateY(-8px);opacity:0;pointer-events:none;z-index:10000;\n'
    'visibility:hidden;' in h
    and 'html.js-nav .page-indicator{display:block}' in h
    and '-webkit-user-select:none;user-select:none}' in h)
chk('S21 плашка в газетном стиле: PT Mono 10px капс, бумага, тёмный текст, красная линейка',
    'font-family:"PT Mono",monospace;font-size:10px;font-weight:700;\n'
    'letter-spacing:.16em;text-transform:uppercase;color:var(--ink);background:var(--paper);\n'
    'border-bottom:2px solid var(--ox);padding:7px 12px;' in h
    and 'box-shadow' not in h[h.index('.page-indicator{'):h.index('@keyframes pageIndicatorInOut')])
chk('S22 цикл плашки 1.6s ease both: 0→18→70→100% (появление, пауза, уход)',
    'html.js-nav .page-indicator.show{visibility:visible;'
    'animation:pageIndicatorInOut 1.6s ease both}' in h
    and '@keyframes pageIndicatorInOut{\n'
        '0%{opacity:0;transform:translateX(-50%) translateY(-8px)}\n'
        '18%{opacity:1;transform:translateX(-50%) translateY(0)}\n'
        '70%{opacity:1;transform:translateX(-50%) translateY(0)}\n'
        '100%{opacity:0;transform:translateX(-50%) translateY(-8px)}}' in h
    and h.count('translateX(-50%) translateY(-8px)') == 3
    and h.count('translateX(-50%) translateY(0)') == 2)
chk('S23 плашка вызывается при переключении и перезапускается заново',
    "function showPageIndicator(n){\n    ind.textContent='ПОЛОСА '+n+' / '+sheets.length;\n"
    "    ind.classList.remove('show');\n    void ind.offsetWidth;\n    ind.classList.add('show');\n  }" in h
    and 'showPageIndicator(ni+1);' in h
    and "ind.addEventListener('animationend',function(){ind.classList.remove('show');});" in h)
chk('S24 на узких экранах плашка под компактным блоком (не на кнопках)',
    '@media (max-width:1299px){html.js-nav .page-indicator{top:60px}}' in h)

# ------------------------------ браузер -------------------------------------
from playwright.sync_api import sync_playwright

STATE = """() => {
  const g = i => document.getElementById('p' + i);
  const cs = el => getComputedStyle(el);
  const wrap = document.getElementById('newspaper');
  const ind = document.getElementById('pageIndicator');
  return {
    jsnav: document.documentElement.classList.contains('js-nav'),
    cls: [1,2,3,4].map(i => g(i).className),
    disp: [1,2,3,4].map(i => cs(g(i)).display),
    op:  [1,2,3,4].map(i => cs(g(i)).opacity),
    tr:  [1,2,3,4].map(i => cs(g(i)).transform),
    pos: [1,2,3,4].map(i => cs(g(i)).position),
    tops:[1,2,3,4].map(i => +g(i).getBoundingClientRect().top.toFixed(1)),
    hasCounter: !!document.getElementById('navCount'),
    counterNodes: [].slice.call(document.querySelectorAll('body *'))
      .filter(e => /^\\d+\\s*\\/\\s*4$/.test((e.textContent||'').trim()) && e.children.length===0).length,
    bodyCount: /\\d\\s*\\/\\s*4/.test(document.body.innerText),
    prevD: document.getElementById('navPrev').disabled,
    nextD: document.getElementById('navNext').disabled,
    heights: [1,2,3,4].map(i => g(i).offsetHeight),
    a01top: document.getElementById('a01').offsetTop,
    a05top: document.getElementById('a05').offsetTop,
    a12top: document.getElementById('a12').offsetTop,
    scrollW: document.documentElement.scrollWidth,
    innerW: window.innerWidth,
    scrollY: Math.round(window.scrollY || window.pageYOffset),
    minH: wrap.style.minHeight,
    busyCls: [1,2,3,4].map(i => /page-enter-next|page-enter-prev|page-exit/.test(g(i).className)),
    indCls: ind.className, indText: ind.textContent, indOp: cs(ind).opacity,
    indDisp: cs(ind).display, indPos: cs(ind).position, indPE: cs(ind).pointerEvents,
    indZ: cs(ind).zIndex, indDur: cs(ind).animationDuration, indName: cs(ind).animationName,
    indVis: cs(ind).visibility, indTop: cs(ind).top, indSel: cs(ind).userSelect,
  };
}"""

NAVRECT = """() => {
  const r = el => { const b = el.getBoundingClientRect();
    return {t:+b.top.toFixed(1),l:+b.left.toFixed(1),r:+b.right.toFixed(1),b:+b.bottom.toFixed(1),
            cx:+(b.left+b.width/2).toFixed(1),cy:+(b.top+b.height/2).toFixed(1),
            w:+b.width.toFixed(1),h:+b.height.toFixed(1)}; };
  const nav = document.querySelector('.sheetnav');
  const ind = document.getElementById('pageIndicator');
  const fixed = [];
  document.querySelectorAll('body *').forEach(e => {
    const cs = getComputedStyle(e);
    if (cs.position !== 'fixed') return;
    const b = e.getBoundingClientRect();
    if (!b.width && !b.height) return;            // display:contents — бокса нет
    fixed.push({id: e.id || ('.' + e.className), t:+b.top.toFixed(1), b:+b.bottom.toFixed(1),
                l:+b.left.toFixed(1), r:+b.right.toFixed(1)});
  });
  return {
    sheet: r(document.getElementById('p1')),
    prev: r(document.getElementById('navPrev')),
    next: r(document.getElementById('navNext')),
    ind: r(ind),
    bar: r(nav),
    barKids: nav.children.length,
    fixed: fixed,
    dispNav: getComputedStyle(nav).display,
    posPrev: getComputedStyle(document.getElementById('navPrev')).position,
    posNext: getComputedStyle(document.getElementById('navNext')).position,
    posInd: getComputedStyle(ind).position, cssTopInd: getComputedStyle(ind).top,
    vw: window.innerWidth, vh: window.innerHeight,
  };
}"""

STATIC = """() => {
  const g = i => document.getElementById('p' + i);
  const ind = document.getElementById('pageIndicator');
  return {
    jscls: document.documentElement.className,
    heights: [1,2,3,4].map(i => g(i).offsetHeight),
    tops: [1,2,3,4].map(i => g(i).offsetTop),
    a01top: document.getElementById('a01').offsetTop,
    a05top: document.getElementById('a05').offsetTop,
    a12top: document.getElementById('a12').offsetTop,
    navDisp: getComputedStyle(document.querySelector('.sheetnav')).display,
    indDisp: ind ? getComputedStyle(ind).display : 'ABSENT',
  };
}"""

GEO = """(pid) => {
  const s = document.getElementById(pid);
  const b = s.getBoundingClientRect();
  return {top:+b.top.toFixed(2), h:s.offsetHeight,
          a01: document.getElementById('a01').offsetTop,
          a05: document.getElementById('a05').offsetTop,
          a12: document.getElementById('a12').offsetTop,
          gridTop: +s.querySelector('.grid').getBoundingClientRect().top.toFixed(2)};
}"""

# покадровый сэмплер перехода + плашки: пишет состояние каждый кадр rAF,
# на 3-м кадре диспатчит клик (t=0 — момент клика) — никаких гонок между вызовами
SAMPLER = """(cfg) => new Promise(res => {
  const g = i => document.getElementById('p' + i);
  const ind = document.getElementById('pageIndicator');
  window.scrollTo(0, cfg.y0);
  const rec = [];
  let t0 = null;
  requestAnimationFrame(function tick(){
    const now = performance.now();
    if (t0 === null) t0 = now;
    const ci = getComputedStyle(ind);
    const fr = {t: +(now - t0).toFixed(1), y: Math.round(window.scrollY),
                sw: document.documentElement.scrollWidth,
                mh: document.getElementById('newspaper').style.minHeight,
                io: +(+ci.opacity).toFixed(3), it: ci.transform, itx: ind.textContent,
                ic: ind.className, s: []};
    for (let i = 1; i <= 4; i++){
      const c = getComputedStyle(g(i));
      fr.s.push({d: c.display, o: +(+c.opacity).toFixed(3), t: c.transform,
                 p: c.position, c: g(i).className});
    }
    rec.push(fr);
    if (rec.length === 3){
      t0 = performance.now();
      document.getElementById(cfg.btn).dispatchEvent(new MouseEvent('click', {bubbles: true}));
    }
    if ((now - t0) > cfg.tmax || rec.length > 400) res(rec);
    else requestAnimationFrame(tick);
  });
})"""


def ty_of(tr):
    m = re.match(r'matrix\(([^)]+)\)', tr or '')
    return float(m.group(1).split(',')[5]) if m else None


with sync_playwright() as pw:
    br = pw.chromium.launch()

    # --- эталон: версия без JS (потоковая раскладка всех полос) ---
    ctx_ns = br.new_context(viewport={'width': 1440, 'height': 900}, java_script_enabled=False)
    ns = ctx_ns.new_page()
    ns.goto(URL, wait_until='load')
    ns.wait_for_timeout(2200)
    base = ns.evaluate(STATIC)
    chk('NJ1 без JS: навигация скрыта, режима нет, плашки нет вовсе',
        base['navDisp'] == 'none' and 'js-nav' not in base['jscls']
        and base['indDisp'] == 'none')
    chk('NJ2 без JS: все 4 полосы в потоке',
        all(x > 1000 for x in base['heights'])
        and all(base['tops'][i] < base['tops'][i + 1] for i in range(3)), base['tops'])
    chk('NJ3 без JS: геометрия материалов есть',
        base['a01top'] > 0 and base['a05top'] > 0 and base['a12top'] > 0)
    ctx_ns.close()

    pg = br.new_page(viewport={'width': 1440, 'height': 900})
    errs = []
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL, wait_until='load')
    pg.wait_for_timeout(1800)

    s0 = pg.evaluate(STATE)
    nr = pg.evaluate(NAVRECT)
    gapL = nr['sheet']['l'] - nr['prev']['r']
    gapR = nr['next']['l'] - nr['sheet']['r']
    chk('B1 режим одной полосы включён, p1 в самом верху документа',
        s0['jsnav'] and abs(s0['tops'][0]) <= 2, s0['tops'][0])
    chk('B2 постоянного счётчика нет: ни узла navCount, ни текста «N / 4» в DOM',
        not s0['hasCounter'] and s0['counterNodes'] == 0 and not s0['bodyCount']
        and s0['prevD'] and not s0['nextD'],
        (s0['hasCounter'], s0['counterNodes'], s0['bodyCount']))
    chk('B3 p1 видна, p2–p4 скрыты', s0['disp'] == ['block', 'none', 'none', 'none'], s0['disp'])
    chk('B4 ← вплотную к газете: 20–35px от края листа, по центру видимой области',
        nr['posPrev'] == 'fixed' and 20 <= gapL <= 35
        and abs(nr['prev']['cy'] - nr['vh'] / 2) <= 3 and nr['prev']['w'] == 56,
        (round(gapL, 1), round(nr['prev']['cy'] - nr['vh'] / 2, 1)))
    chk('B5 → вплотную к газете: 20–35px от края листа, по центру видимой области',
        nr['posNext'] == 'fixed' and 20 <= gapR <= 35
        and abs(nr['next']['cy'] - nr['vh'] / 2) <= 3 and nr['next']['w'] == 56,
        (round(gapR, 1), round(nr['next']['cy'] - nr['vh'] / 2, 1)))
    chk('B6 стрелки не у краёв монитора и не перекрывают лист',
        nr['prev']['l'] >= 30 and nr['next']['r'] <= nr['vw'] - 30
        and nr['prev']['r'] <= nr['sheet']['l'] and nr['next']['l'] >= nr['sheet']['r'],
        (round(nr['prev']['l']), round(nr['next']['r']), nr['vw']))
    lefties = [f for f in nr['fixed'] if f['r'] <= nr['sheet']['l'] + 1]
    chk('B7 в левом поле под ← больше ничего нет (фиксированы только стрелки и плашка)',
        [f['id'] for f in nr['fixed']] == ['navPrev', 'navNext', 'pageIndicator']
        and [f['id'] for f in lefties] == ['navPrev'],
        [f['id'] for f in nr['fixed']])
    chk('B8 плашка в покое невидима и не мешает: opacity 0 + visibility hidden, без show, '
        'pointer-events none, текст не выделяется',
        s0['indDisp'] == 'block' and s0['indPos'] == 'fixed' and s0['indOp'] == '0'
        and s0['indVis'] == 'hidden' and s0['indSel'] == 'none'
        and s0['indCls'] == 'page-indicator' and s0['indText'] == ''
        and s0['indPE'] == 'none' and s0['indZ'] == '10000'
        and s0['indDur'] == '0s' and s0['indName'] == 'none',
        (s0['indOp'], s0['indVis'], s0['indCls'], s0['indZ'], s0['indPE']))
    chk('B9 плашка ВВЕРХУ по центру экрана (top:24px) и не пересекает стрелки',
        nr['posInd'] == 'fixed' and nr['cssTopInd'] == '24px'
        and abs(nr['ind']['t'] - 16) <= 1.5          # в покое сдвинута на -8px (translateY)
        and abs(nr['ind']['cx'] - nr['vw'] / 2) <= 2
        and nr['ind']['b'] < nr['prev']['t'] and nr['ind']['b'] < nr['next']['t']
        and nr['ind']['h'] < 40,
        (nr['cssTopInd'], nr['ind']['t'], nr['ind']['cx'], nr['ind']['h']))
    pg.evaluate("window.scrollTo(0,1200)")
    pg.wait_for_timeout(350)
    nr2 = pg.evaluate(NAVRECT)
    same = all(abs(nr[k]['t'] - nr2[k]['t']) <= 1 and abs(nr[k]['l'] - nr2[k]['l']) <= 1
               for k in ('prev', 'next', 'ind'))
    chk('B10 навигация и плашка доступны при прокрутке — стоят на месте', same)
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(250)
    chk('B11 нет горизонт. переполнения, стрелки в экране',
        s0['scrollW'] <= s0['innerW'] + 1
        and nr['prev']['l'] >= 0 and nr['next']['r'] <= nr['vw']
        and nr['prev']['t'] >= 0 and nr['prev']['b'] <= nr['vh'])
    geo_rest = pg.evaluate(GEO, 'p1')
    pg.evaluate("""() => { const i=document.getElementById('pageIndicator');
        i.textContent='ПОЛОСА 2 / 4'; i.classList.add('show');
        const a=i.getAnimations(); a.forEach(x=>{x.pause(); x.currentTime=500;}); }""")
    pg.wait_for_timeout(200)
    geo_show = pg.evaluate(GEO, 'p1')
    ind_vis = pg.evaluate("""() => { const i=document.getElementById('pageIndicator');
        const c=getComputedStyle(i); const b=i.getBoundingClientRect();
        return {op:c.opacity, vis:c.visibility, anim:c.animationName, dur:c.animationDuration,
                t:+b.top.toFixed(1), h:+b.height.toFixed(1), w:+b.width.toFixed(1),
                cx:+(b.left+b.width/2).toFixed(1), vw:innerWidth}; }""")
    pg.screenshot(path=os.path.join(REND, 'v20_indicator.png'),
                  clip={'x': 0, 'y': 0, 'width': 1440, 'height': 260})
    pg.screenshot(path=os.path.join(REND, 'v20_indicator_desktop.png'))
    chk('PI1 плашка не занимает места в макете и не сдвигает .sheet',
        geo_rest == geo_show, (geo_rest, geo_show))
    chk('PI2 плашка видна: opacity 1 + visibility visible, pageIndicatorInOut 1.6s, центр',
        ind_vis['op'] == '1' and ind_vis['vis'] == 'visible' and ind_vis['anim'] == 'pageIndicatorInOut'
        and ind_vis['dur'] == '1.6s' and abs(ind_vis['cx'] - ind_vis['vw'] / 2) <= 2
        and 20 <= ind_vis['h'] <= 40 and 100 <= ind_vis['w'] <= 260, ind_vis)
    chk('R1 рендеры плашки сделаны',
        os.path.exists(os.path.join(REND, 'v20_indicator.png'))
        and os.path.exists(os.path.join(REND, 'v20_indicator_desktop.png')))
    # вариант «у самого края» (top:6px) — только для показа главреду, в файл не идёт
    pg.evaluate("""() => { const i=document.getElementById('pageIndicator');
        i.style.top='6px'; const a=i.getAnimations(); a.forEach(x=>{x.currentTime=500;}); }""")
    pg.wait_for_timeout(150)
    pg.screenshot(path=os.path.join(REND, 'v20_indicator_alt6.png'),
                  clip={'x': 0, 'y': 0, 'width': 1440, 'height': 260})
    pg.evaluate("""() => { const i=document.getElementById('pageIndicator');
        i.style.top=''; i.getAnimations().forEach(x=>x.cancel()); i.classList.remove('show');
        i.textContent=''; }""")
    pg.wait_for_timeout(300)
    s0b = pg.evaluate(STATE)
    chk('PI3 после уборки плашки состояние покоя восстановлено (opacity 0, текста нет)',
        s0b['indOp'] == '0' and s0b['indVis'] == 'hidden' and s0b['indText'] == ''
        and s0b['indCls'] == 'page-indicator')
    pg.screenshot(path=os.path.join(REND, 'v20_nav_desktop.png'))
    chk('R2 рендер десктоп-навигации (стрелки без счётчика)',
        os.path.exists(os.path.join(REND, 'v20_nav_desktop.png')))

    # --- переход ВПЕРЁД: покадровый сэмплер из глубокой прокрутки ---
    p1h = pg.evaluate("document.getElementById('p1').offsetHeight")
    y0f = min(2500, p1h - 1000)
    rec_f = pg.evaluate(SAMPLER, {'y0': y0f, 'btn': 'navNext', 'tmax': 2400})
    pre, post = rec_f[:3], rec_f[2:]
    chk('F1 до клика: вид внизу p1, p2 скрыта, плашка пуста и невидима',
        all(abs(f['y'] - y0f) <= 2 for f in rec_f[:2])
        and rec_f[0]['s'][0]['d'] == 'block' and rec_f[0]['s'][1]['d'] == 'none'
        and rec_f[0]['io'] == 0 and rec_f[0]['itx'] == '', y0f)
    sim = [f for f in post if f['s'][0]['d'] == 'block' and f['s'][1]['d'] == 'block'
           and 0.02 < f['s'][0]['o'] < 0.98 and 0.02 < f['s'][1]['o'] < 0.98]
    ok_layer = any(f['s'][0]['p'] == 'absolute' and f['s'][0]['t'] == 'none'
                   and 'page-exit' in f['s'][0]['c'] for f in sim)
    chk('F2 кроссфейд: старая и новая полоса существуют одновременно (слой absolute)',
        len(sim) >= 5 and ok_layer, f'кадров вместе: {len(sim)}')
    ent = [f for f in post if 'page-enter-next' in f['s'][1]['c']]
    tys = [ty_of(f['s'][1]['t']) for f in ent]
    tys = [v for v in tys if v is not None]
    nom3d = all('matrix3d' not in f['s'][i]['t'] for f in rec_f for i in range(4))
    chk('F3 вперёд: новая полоса едет снизу вверх translateY(14px→0), без 3D',
        len(ent) >= 5 and sum(1 for v in tys if 0.2 < v < 14.6) >= 2
        and all(-0.5 <= v <= 14.6 for v in tys) and nom3d,
        [round(v, 1) for v in tys[:6]])
    ys = [f['y'] for f in post]
    mids = {y for y in ys if 0 < y < y0f}
    drops = [ys[i] - ys[i + 1] for i in range(len(ys) - 1)]
    chk('F4 прокрутка к началу новой полосы плавная (много промежуточных, без скачка)',
        all(drops[i] >= 0 for i in range(len(drops))) and len(mids) >= 4
        and max(drops) < 900 and ys[-1] == 0,
        (len(mids), max(drops), ys[-1]))
    chk('F5 во время перехода нет горизонт. переполнения',
        max(f['sw'] for f in rec_f) <= s0['innerW'] + 1)
    chk('F6 minHeight сцены держит диапазон прокрутки и вычищается',
        any(str(f['mh']).endswith('px') for f in post[:40]) and rec_f[-1]['mh'] == '')

    # --- плашка в момент перехода (главный блок брифа) ---
    vis = [f for f in post if f['io'] > 0.02]
    t_first = vis[0]['t'] if vis else None
    t_last = vis[-1]['t'] if vis else None
    full = [f for f in post if f['io'] >= 0.99]
    t_full = full[0]['t'] if full else None
    t_hold_end = full[-1]['t'] if full else None
    itys = [ty_of(f['it']) for f in post]
    itys = [v for v in itys if v is not None]
    hold = (t_hold_end - t_full) if (t_full is not None and t_hold_end is not None) else -1
    cycle = (t_last - t_first) if vis else -1
    peak = next((f for f in post if f['io'] >= 0.99), None)
    chk('PI4 плашка появляется одновременно с переходом и несёт номер ОТКРЫТОЙ полосы',
        bool(vis) and t_first is not None and t_first <= 120
        and all(f['itx'] == 'ПОЛОСА 2 / 4' for f in vis)
        and peak is not None and 'show' in peak['ic'],
        (t_first, vis[0]['itx'] if vis else None))
    chk('PI5 появление: opacity 0→1 + translateY(-8px→0) примерно за 0.29s (≤0.45s)',
        t_full is not None and 150 <= t_full <= 450
        and min(itys) >= -8.6 and any(-8.6 <= v <= -3 for v in itys[:6]),
        (t_full, [round(v, 1) for v in itys[:6]]))
    chk('PI6 пауза в полностью видимом состоянии ~0.7–0.9s (мс)', 620 <= hold <= 980, round(hold, 1))
    chk('PI7 уход: opacity 1→0 + translateY(0→-8px), весь цикл 1.3–1.8s',
        t_last is not None and 1300 <= cycle <= 1850 and t_last <= 1900
        and any(-8.6 <= v <= -3 for v in itys[-6:]),
        (round(cycle, 1), round(t_last, 1), [round(v, 1) for v in itys[-6:]]))
    chk('PI8 после исчезновения плашка не видна: класс show снят, opacity 0',
        post[-1]['io'] == 0 and 'show' not in post[-1]['ic'],
        (post[-1]['io'], post[-1]['ic'], post[-1]['itx']))
    last = post[-1]
    chk('F7 осела: старая снята (display:none), новая opacity 1 / transform none / классы чистые',
        last['s'][0]['d'] == 'none' and last['s'][1]['o'] >= 0.999
        and last['s'][1]['t'] == 'none' and 'page-enter-next' not in last['s'][1]['c']
        and 'page-exit' not in last['s'][0]['c'] and 'is-off' in last['s'][0]['c'])
    f_set = pg.evaluate(STATE)
    chk('F8 после перехода: scrollY=0, p2 открыта с самого верха, счётчика нет, кнопки живы',
        f_set['scrollY'] == 0 and abs(f_set['tops'][1]) <= 2
        and f_set['disp'] == ['none', 'block', 'none', 'none']
        and not f_set['hasCounter'] and f_set['counterNodes'] == 0
        and not f_set['prevD'] and not f_set['nextD']
        and not any(f_set['busyCls']) and f_set['minH'] == ''
        and f_set['indOp'] == '0' and 'show' not in f_set['indCls'],
        (f_set['scrollY'], f_set['tops'][1], f_set['minH'], f_set['indCls']))
    chk('G1 геометрия p2 идентична потоковой версии без JS',
        abs(f_set['heights'][1] - base['heights'][1]) <= 2
        and abs(f_set['a05top'] - base['a05top']) <= 2,
        (f_set['heights'][1], base['heights'][1], f_set['a05top'], base['a05top']))

    # --- экран после исчезновения плашки = экран до перехода (область верха) ---
    clip_top = {'x': 0, 'y': 0, 'width': 1440, 'height': 200}
    pg.reload(wait_until='load')
    pg.wait_for_timeout(2200)
    pg.mouse.move(0, 0)
    before = pg.screenshot(clip=clip_top)
    pg.click('#navNext')
    pg.wait_for_timeout(2600)
    pg.click('#navPrev')
    pg.wait_for_timeout(2600)
    pg.mouse.move(0, 0)
    after = pg.screenshot(clip=clip_top)
    same_px = before == after
    if not same_px:
        import io as _io
        from PIL import Image, ImageChops
        _a = Image.open(_io.BytesIO(before)).convert('RGB')
        _b = Image.open(_io.BytesIO(after)).convert('RGB')
        _d = ImageChops.difference(_a, _b).convert('L')
        _hist = _d.histogram()
        same_px = sum(_hist[9:]) <= 64 and max((i for i, v in enumerate(_hist) if v), default=0) <= 24
    back1 = pg.evaluate(STATE)
    chk('PI9 верх экрана после исчезновения плашки — как до перехода (следов не остаётся)',
        same_px and back1['disp'] == ['block', 'none', 'none', 'none']
        and back1['indOp'] == '0' and back1['scrollY'] == 0)

    # --- переход ВПЕРЁД ещё раз: анимация запускается ЗАНОВО с новым номером ---
    rec_n = pg.evaluate(SAMPLER, {'y0': 0, 'btn': 'navNext', 'tmax': 2200})
    post_n = rec_n[2:]
    vis_n = [f for f in post_n if f['io'] > 0.02]
    full_n = [f for f in post_n if f['io'] >= 0.99]
    chk('PI10 следующее переключение: плашка заново с номером «ПОЛОСА 2 / 4», цикл полный',
        bool(vis_n) and vis_n[0]['t'] <= 120
        and all(f['itx'] == 'ПОЛОСА 2 / 4' for f in vis_n)
        and len(full_n) >= 3
        and (full_n[-1]['t'] - full_n[0]['t']) >= 600
        and post_n[-1]['io'] == 0 and 'show' not in post_n[-1]['ic'],
        (vis_n[0]['t'] if vis_n else None, len(full_n)))
    pg.wait_for_timeout(600)
    pg.click('#navNext')
    pg.wait_for_timeout(400)
    mid3 = pg.evaluate("""() => { const i=document.getElementById('pageIndicator');
        return {txt:i.textContent, op:+(+getComputedStyle(i).opacity).toFixed(2),
                cls:i.className}; }""")
    pg.screenshot(path=os.path.join(REND, 'v20_crossfade_mid.png'))
    pg.wait_for_timeout(2200)
    m1 = pg.evaluate(STATE)
    chk('PI11 на переходе 2→3 плашка показывает «ПОЛОСА 3 / 4» (номер реальной полосы)',
        mid3['txt'] == 'ПОЛОСА 3 / 4' and mid3['op'] > 0.5 and 'show' in mid3['cls']
        and m1['scrollY'] == 0 and m1['disp'] == ['none', 'none', 'block', 'none'],
        mid3)
    chk('M1 середина перехода с плашкой снята',
        os.path.exists(os.path.join(REND, 'v20_crossfade_mid.png')))

    # --- переход НАЗАД: покадровый сэмплер (p3 → p2) ---
    p3h = pg.evaluate("document.getElementById('p3').offsetHeight")
    y0b = min(1800, p3h - 1000)
    rec_b = pg.evaluate(SAMPLER, {'y0': y0b, 'btn': 'navPrev', 'tmax': 2400})
    post_b = rec_b[2:]
    sim_b = [f for f in post_b if f['s'][2]['d'] == 'block' and f['s'][1]['d'] == 'block'
             and 0.02 < f['s'][2]['o'] < 0.98 and 0.02 < f['s'][1]['o'] < 0.98]
    ok_layer_b = any(f['s'][2]['p'] == 'absolute' and 'page-exit' in f['s'][2]['c']
                     for f in sim_b)
    chk('K1 назад: кроссфейд — p3 уходит слоем, p2 появляется одновременно',
        len(sim_b) >= 5 and ok_layer_b, f'кадров вместе: {len(sim_b)}')
    ent_b = [f for f in post_b if 'page-enter-prev' in f['s'][1]['c']]
    tys_b = [v for v in (ty_of(f['s'][1]['t']) for f in ent_b) if v is not None]
    nom3d_b = all('matrix3d' not in f['s'][i]['t'] for f in rec_b for i in range(4))
    chk('K2 назад: p2 едет сверху вниз translateY(-14px→0), без 3D',
        len(ent_b) >= 5 and sum(1 for v in tys_b if -14.6 < v < -0.2) >= 2
        and all(-14.6 <= v <= 0.5 for v in tys_b) and nom3d_b,
        [round(v, 1) for v in tys_b[:6]])
    vis_b = [f for f in post_b if f['io'] > 0.02]
    full_b = [f for f in post_b if f['io'] >= 0.99]
    ys_b = [f['y'] for f in post_b]
    mids_b = {y for y in ys_b if 0 < y < y0b}
    drops_b = [ys_b[i] - ys_b[i + 1] for i in range(len(ys_b) - 1)]
    chk('K3 назад: прокрутка к началу p2 плавная, финиш scrollY=0',
        all(drops_b[i] >= 0 for i in range(len(drops_b))) and len(mids_b) >= 4
        and max(drops_b) < 900 and ys_b[-1] == 0, (len(mids_b), max(drops_b)))
    chk('PI12 назад плашка тоже работает: «ПОЛОСА 2 / 4», полный цикл, потом гаснет',
        bool(vis_b) and all(f['itx'] == 'ПОЛОСА 2 / 4' for f in vis_b)
        and len(full_b) >= 3 and (1300 <= (vis_b[-1]['t'] - vis_b[0]['t']) <= 1850)
        and post_b[-1]['io'] == 0 and 'show' not in post_b[-1]['ic'],
        (len(vis_b), vis_b[-1]['t'] - vis_b[0]['t'] if vis_b else None))
    last_b = post_b[-1]
    b_set = pg.evaluate(STATE)
    chk('K4 назад: осела — p2 с верха (scrollY=0, top≈0), p3 скрыта, классы чистые',
        last_b['s'][2]['d'] == 'none' and last_b['s'][1]['o'] >= 0.999
        and last_b['s'][1]['t'] == 'none' and rec_b[-1]['mh'] == ''
        and b_set['scrollY'] == 0 and abs(b_set['tops'][1]) <= 2
        and not any(b_set['busyCls']) and not b_set['hasCounter'])

    # --- hammer: 5 быстрых кликов ---
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    g2s = pg.evaluate(STATE)
    chk('G2 геометрия p1 идентична потоковой версии без JS',
        abs(g2s['heights'][0] - base['heights'][0]) <= 2
        and abs(g2s['a01top'] - base['a01top']) <= 2,
        (g2s['heights'][0], base['heights'][0], g2s['a01top'], base['a01top']))
    pg.evaluate("for(let i=0;i<5;i++)document.getElementById('navNext')"
                ".dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(2000)
    h1 = pg.evaluate(STATE)
    ind_h = pg.evaluate("""() => { const i=document.getElementById('pageIndicator');
        return {n: i.getAnimations().length, cls: i.className, op: getComputedStyle(i).opacity}; }""")
    chk('H1 hammer: ровно одно переключение (p2), плашка одна и уже погасла',
        h1['disp'] == ['none', 'block', 'none', 'none'] and h1['indText'] == 'ПОЛОСА 2 / 4'
        and ind_h['cls'] == 'page-indicator' and ind_h['op'] == '0' and ind_h['n'] == 0,
        (h1['indText'], ind_h))
    chk('H2 hammer: состояние цело — классы/minHeight вычищены, scrollY=0',
        not any(h1['busyCls']) and h1['op'][1] == '1' and h1['minH'] == ''
        and h1['scrollY'] == 0 and not h1['prevD'] and not h1['nextD'])

    # --- до конца: p4 ---
    for _ in range(2):
        pg.click('#navNext')
        pg.wait_for_timeout(1900)
    e1 = pg.evaluate(STATE)
    chk('E1 дошли до p4: вперёд неактивна, постоянного счётчика нет',
        e1['nextD'] and not e1['prevD']
        and e1['disp'] == ['none', 'none', 'none', 'block']
        and not e1['hasCounter'] and e1['counterNodes'] == 0 and not e1['bodyCount']
        and e1['indVis'] == 'hidden',
        (e1['indText'], e1['bodyCount'], e1['indVis']))
    chk('G3 геометрия p4 идентична потоковой версии без JS',
        abs(e1['heights'][3] - base['heights'][3]) <= 2
        and abs(e1['a12top'] - base['a12top']) <= 2)
    pg.click('#navPrev')
    pg.wait_for_timeout(350)
    e3 = pg.evaluate("""() => document.getElementById('pageIndicator').textContent""")
    pg.wait_for_timeout(1900)
    chk('PI13 номер плашки всегда соответствует реально открытой полосе (4→3 = «ПОЛОСА 3 / 4»)',
        e3 == 'ПОЛОСА 3 / 4' and pg.evaluate(
            "() => document.getElementById('p3').classList.contains('is-on')"))
    pg.evaluate("document.getElementById('navNext').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(2000)
    e2 = pg.evaluate(STATE)
    chk('E2 на p4 вперёд не ломается, плашка гаснет',
        e2['disp'][3] == 'block' and not any(e2['busyCls']) and e2['indOp'] == '0')

    # --- рендеры полос в покое ---
    pg.reload(wait_until='load')
    pg.evaluate('document.fonts.ready.then(()=>1)')
    pg.wait_for_timeout(2200)
    for i in range(1, 5):
        if i > 1:
            pg.click('#navNext')
            pg.wait_for_timeout(1600)
        pg.mouse.move(0, 0)
        pg.wait_for_timeout(400)
        pg.query_selector(f'#p{i}').screenshot(path=os.path.join(REND, f'v20_p{i}.png'))
    chk('R3 рендеры полос сделаны',
        all(os.path.exists(os.path.join(REND, f'v20_p{i}.png')) for i in range(1, 5)))

    # --- ширина 1300: стрелки вплотную к листу, плашка по центру ---
    pg.set_viewport_size({'width': 1300, 'height': 900})
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    n13 = pg.evaluate(NAVRECT)
    g13L = n13['sheet']['l'] - n13['prev']['r']
    g13R = n13['next']['l'] - n13['sheet']['r']
    s13 = pg.evaluate(STATE)
    pg.click('#navNext')
    pg.wait_for_timeout(250)
    s13m = pg.evaluate(STATE)
    i13 = pg.evaluate(NAVRECT)['ind']
    pg.wait_for_timeout(2000)
    s13e = pg.evaluate(STATE)
    chk('W1 @1300px: стрелки у листа (20–35px), плашка вверху по центру, без переполнения',
        n13['dispNav'] == 'contents' and 20 <= g13L <= 35 and 20 <= g13R <= 35
        and n13['prev']['l'] >= 0 and n13['next']['r'] <= n13['vw']
        and s13['scrollW'] <= s13['innerW'] + 1 and s13m['scrollW'] <= s13m['innerW'] + 1
        and s13m['indText'] == 'ПОЛОСА 2 / 4' and abs(i13['cx'] - 650) <= 2
        and i13['t'] >= 16 and i13['b'] <= n13['prev']['t'] and s13e['indOp'] == '0'
        and s13e['indVis'] == 'hidden',
        (round(g13L, 1), round(g13R, 1), i13['cx'], i13['t'], i13['b']))

    # --- узкие экраны: компактный блок ← → у верха, плашка под ним ---
    pg.set_viewport_size({'width': 1100, 'height': 900})
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    w1 = pg.evaluate(NAVRECT)
    ok_bar = (w1['dispNav'] == 'flex' and w1['bar']['t'] <= 14 and w1['barKids'] == 2
              and abs(w1['bar']['cx'] - w1['vw'] / 2) <= 4 and w1['prev']['t'] < 60)
    sw1 = pg.evaluate(STATE)
    pg.click('#navNext')
    pg.wait_for_timeout(300)
    w1i = pg.evaluate(NAVRECT)
    swm = pg.evaluate(STATE)
    pg.screenshot(path=os.path.join(REND, 'v20_narrow_indicator.png'),
                  clip={'x': 0, 'y': 0, 'width': 1100, 'height': 200})
    pg.wait_for_timeout(2000)
    chk('W2 @1100px: компактный блок из двух стрелок (без счётчика), плашка ниже кнопок',
        ok_bar and sw1['scrollW'] <= sw1['innerW'] + 1
        and swm['scrollW'] <= swm['innerW'] + 1
        and w1i['ind']['t'] >= w1['bar']['b'] - 1
        and abs(w1i['ind']['cx'] - w1['vw'] / 2) <= 2
        and swm['indText'] == 'ПОЛОСА 2 / 4',
        (round(w1['bar']['b']), round(w1i['ind']['t']), w1['barKids']))

    pg.set_viewport_size({'width': 390, 'height': 844})
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    w2 = pg.evaluate(NAVRECT)
    ok_m = (w2['dispNav'] == 'flex' and w2['bar']['t'] <= 14 and w2['barKids'] == 2
            and w2['bar']['l'] >= 0 and w2['bar']['r'] <= w2['vw']
            and abs(w2['bar']['cx'] - w2['vw'] / 2) <= 4)
    sw2 = pg.evaluate(STATE)
    pg.click('#navNext')
    pg.wait_for_timeout(300)
    w2i = pg.evaluate(NAVRECT)
    sw2m = pg.evaluate(STATE)
    pg.mouse.move(0, 0)
    pg.screenshot(path=os.path.join(REND, 'v20_mobile_indicator.png'))
    pg.wait_for_timeout(2000)
    pg.click('#navPrev')
    pg.wait_for_timeout(2000)
    w3 = pg.evaluate(STATE)
    chk('W3 @390px: блок в экране, плашка под кнопками и по центру, возврат на p1',
        ok_m and sw2['scrollW'] <= sw2['innerW'] + 1
        and sw2m['scrollW'] <= sw2m['innerW'] + 1
        and w2i['ind']['t'] >= w2['bar']['b'] - 1
        and w2i['ind']['l'] >= 0 and w2i['ind']['r'] <= w2['vw']
        and abs(w2i['ind']['cx'] - w2['vw'] / 2) <= 2
        and sw2m['indText'] == 'ПОЛОСА 2 / 4' and w3['indOp'] == '0'
        and w3['disp'] == ['block', 'none', 'none', 'none'] and w3['scrollY'] == 0,
        (round(w2['bar']['b']), round(w2i['ind']['t']), round(w2i['ind']['l'])))
    pg.mouse.move(0, 0)
    pg.wait_for_timeout(400)
    pg.query_selector('#p1').screenshot(path=os.path.join(REND, 'v20_mobile_p1.png'))
    pg.screenshot(path=os.path.join(REND, 'v20_mobile_nav.png'))

    # --- LM: «моушен всегда жив» — плашка и кроссфейд при reduce ---
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    pr = ctx.new_page()
    pr.goto(URL, wait_until='load')
    lm = pr.evaluate("""() => {
      const c = getComputedStyle(document.getElementById('a01'));
      const s = getComputedStyle(document.getElementById('p1'));
      return {aName: c.animationName, aDur: c.animationDuration, sDur: s.animationDuration,
              rm: window.matchMedia('(prefers-reduced-motion: reduce)').matches};
    }""")
    chk('LM1 reduce: ОС просит уменьшить движение, но day-motion жив (0.55s/0.65s)',
        lm['rm'] and lm['aName'] == 'sfn-rise' and lm['aDur'] == '0.55s'
        and lm['sDur'] == '0.65s', lm)
    pr.wait_for_timeout(900)
    rec_rm = pr.evaluate(SAMPLER, {'y0': 0, 'btn': 'navNext', 'tmax': 2300})
    post_rm = rec_rm[2:]
    both_rm = [f for f in post_rm if sum(1 for s in f['s'] if s['d'] != 'none') >= 2]
    mids_rm = sorted({s['o'] for f in both_rm for s in f['s'] if 0.02 < s['o'] < 0.98})
    chk('LM2 reduce: кроссфейд проигрывается (сосуществование полос, промежуточные opacity)',
        len(both_rm) >= 8
        and any('page-exit' in s['c'] for f in rec_rm for s in f['s'])
        and any('page-enter-next' in s['c'] for f in rec_rm for s in f['s'])
        and len(mids_rm) >= 3, (len(both_rm), mids_rm[:4]))
    vis_rm = [f for f in post_rm if f['io'] > 0.02]
    full_rm = [f for f in post_rm if f['io'] >= 0.99]
    chk('LM3 reduce: плашка живёт и при «уменьшить движение» (полный цикл, потом гаснет)',
        len(vis_rm) >= 5 and len(full_rm) >= 3
        and all(f['itx'] == 'ПОЛОСА 2 / 4' for f in vis_rm)
        and (1300 <= (vis_rm[-1]['t'] - vis_rm[0]['t']) <= 1850)
        and post_rm[-1]['io'] == 0 and 'show' not in post_rm[-1]['ic'],
        (len(vis_rm), vis_rm[-1]['t'] - vis_rm[0]['t'] if vis_rm else None))
    chk('LM4 reduce: финал перехода — scrollY=0, уходящая полоса снята',
        rec_rm[-1]['y'] == 0
        and rec_rm[-1]['s'][0]['d'] == 'none' and rec_rm[-1]['s'][1]['d'] == 'block',
        rec_rm[-1]['y'])
    pr.wait_for_timeout(1200)
    r2 = pr.evaluate(STATE)
    chk('LM5 reduce: после оседания p2 активна, блокировка и minHeight вычищены',
        r2['disp'] == ['none', 'block', 'none', 'none']
        and not any(r2['busyCls']) and r2['minH'] == '' and r2['indOp'] == '0')
    ctx.close()

    # --- печать ---
    ctx2 = br.new_context(viewport={'width': 1440, 'height': 900})
    pp = ctx2.new_page()
    pp.goto(URL, wait_until='load')
    pp.wait_for_timeout(1800)
    pp.click('#navNext')
    pp.wait_for_timeout(300)
    pp.emulate_media(media='print')
    pp.wait_for_timeout(300)
    prn = pp.evaluate("""() => {
      const g = i => document.getElementById('p' + i);
      const cs = el => getComputedStyle(el);
      const ind = document.getElementById('pageIndicator');
      return {
        disp: [1,2,3,4].map(i => cs(g(i)).display),
        op: [1,2,3,4].map(i => cs(g(i)).opacity),
        pos: [1,2,3,4].map(i => cs(g(i)).position),
        heights: [1,2,3,4].map(i => g(i).offsetHeight),
        tops: [1,2,3,4].map(i => g(i).offsetTop),
        nav: cs(document.querySelector('.sheetnav')).display,
        ind: cs(ind).display, indTxt: ind.textContent,
        minH: cs(document.getElementById('newspaper')).minHeight,
      };
    }""")
    chk('PR1 печать: 4 полосы в потоке (relative), все видимы',
        prn['disp'] == ['block'] * 4 and all(x > 1000 for x in prn['heights'])
        and prn['op'] == ['1'] * 4 and prn['pos'] == ['relative'] * 4
        and all(prn['tops'][i] < prn['tops'][i + 1] for i in range(3)), prn['tops'])
    chk('PR2 печать: навигация и плашка скрыты (статичный лист)',
        prn['nav'] == 'none' and prn['ind'] == 'none', (prn['nav'], prn['ind']))
    ctx2.close()

    # --- синхронный контроль прошлой опубликованной версии (day-livemotion) ---
    if HAVE_OLD:
        cp = br.new_page(viewport={'width': 1440, 'height': 900})
        cp.goto('file://' + OLD_HTML, wait_until='load')
        cp.evaluate('document.fonts.ready.then(()=>1)')
        cp.wait_for_timeout(2200)
        for i in range(1, 5):
            if i > 1:
                cp.click('#navNext')
                cp.wait_for_timeout(1600)
            cp.mouse.move(0, 0)
            cp.wait_for_timeout(400)
            cp.query_selector(f'#p{i}').screenshot(path=os.path.join(SCRATCH, f'ctrl_h_p{i}.png'))
        cp.close()
        cmg = br.new_page(viewport={'width': 390, 'height': 844})
        cmg.goto('file://' + OLD_HTML, wait_until='load')
        cmg.wait_for_timeout(2200)
        cmg.mouse.move(0, 0)
        cmg.wait_for_timeout(400)
        cmg.query_selector('#p1').screenshot(path=os.path.join(SCRATCH, 'ctrl_h_mobile_p1.png'))
        cmg.close()

    chk('C1 консоль чистая', not errs, errs[:3])
    br.close()

# ---------------------- идентичность покоя синхронному контролю --------------
try:
    from PIL import Image, ImageChops

    def maxdelta(a, b):
        d = ImageChops.difference(a, b).convert('L')
        hist = d.histogram()
        mx = max((i for i, v in enumerate(hist) if v), default=0)
        return d.getbbox(), mx, sum(hist[9:])

    if HAVE_OLD:
        bad_i = []
        for i in range(1, 5):
            a = Image.open(os.path.join(SCRATCH, f'ctrl_h_p{i}.png')).convert('RGB')
            b = Image.open(os.path.join(REND, f'v20_p{i}.png')).convert('RGB')
            if a.size != b.size:
                bad_i.append((i, a.size, b.size))
                continue
            bb, mx, st = maxdelta(a, b)
            # допуск: растровый шум JPEG/AA (≤64 пикселей с дельтой >8 и ≤24 по яркости)
            if st > 64 or mx > 24:
                bad_i.append((i, bb, mx, st))
        chk('I1 полосы в покое идентичны day-livemotion (синхр. контроль)', not bad_i, bad_i)
        a = Image.open(os.path.join(SCRATCH, 'ctrl_h_mobile_p1.png')).convert('RGB')
        b = Image.open(os.path.join(REND, 'v20_mobile_p1.png')).convert('RGB')
        if a.size != b.size:
            chk('I2 мобильная p1 идентична day-livemotion (синхр. контроль)', False, (a.size, b.size))
        else:
            # верхняя полоса 0–70px: там компактная навигация (в новой сборке она
            # уже — без счётчика), поэтому сравнение касается только бумаги
            aa = a.crop((0, 70, a.width, a.height))
            bbim = b.crop((0, 70, b.width, b.height))
            bb, mx, st = maxdelta(aa, bbim)
            chk('I2 мобильная p1 идентична day-livemotion (синхр. контроль, ниже навигации)',
                st <= 64 and mx <= 24, (bb, mx, st))
    else:
        chk('I1/I2 идентичность (нет контроля day-livemotion)', False, 'нет blob в git')
except FileNotFoundError as e:
    chk('I1/I2 идентичность', False, e)

# ------------------------------ композит ------------------------------------
try:
    from PIL import Image
    desk = Image.open(os.path.join(REND, 'v20_nav_desktop.png')).convert('RGB')
    ind = Image.open(os.path.join(REND, 'v20_indicator_desktop.png')).convert('RGB')
    mid = Image.open(os.path.join(REND, 'v20_crossfade_mid.png')).convert('RGB')
    mob = Image.open(os.path.join(REND, 'v20_mobile_indicator.png')).convert('RGB')
    ims = [Image.open(os.path.join(REND, f'v20_p{i}.png')).convert('RGB') for i in range(1, 5)]
    W, GAP, BG = 1120, 12, (242, 237, 227)

    def fit(im, w):
        return im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS)

    desk_s = fit(desk, W)
    ind_s = fit(ind, W)
    half = (W - GAP) // 2
    mid_s = fit(mid, half)
    mob_s = fit(mob, half)
    cells = [fit(im, half) for im in ims]
    row_h = max(mid_s.height, mob_s.height)
    grid_h = max(cells[0].height, cells[1].height) + GAP + max(cells[2].height, cells[3].height)
    canvas = Image.new('RGB', (W, GAP * 5 + desk_s.height + ind_s.height + row_h + grid_h), BG)
    y = GAP
    canvas.paste(desk_s, (0, y)); y += desk_s.height + GAP
    canvas.paste(ind_s, (0, y)); y += ind_s.height + GAP
    canvas.paste(mid_s, (0, y)); canvas.paste(mob_s, (half + GAP, y))
    y += row_h + GAP
    canvas.paste(cells[0], (0, y)); canvas.paste(cells[1], (half + GAP, y))
    y += max(cells[0].height, cells[1].height) + GAP
    canvas.paste(cells[2], (0, y)); canvas.paste(cells[3], (half + GAP, y))
    canvas.save(os.path.join(REND, 'preview-all.png'))
    chk('Z1 композит preview-all.png', True, canvas.size)
except Exception as e:  # noqa: BLE001
    chk('Z1 композит preview-all.png', False, e)

print()
print(f'ИТОГ: {len(OK)} PASS / {len(BAD)} FAIL')
if BAD:
    print('ПРОВАЛЕНО:', '; '.join(BAD))
    sys.exit(1)
