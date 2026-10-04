#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN QA day-navglide: стрелки вплотную к газете + живой кроссфейд полос (03.10.2026).

Проверяет: статику HTML (штамп day-navglide, keyframes pageEnterNext/pageEnterPrev/
pageExit с translateY(±14px), .6s cubic-bezier(.22,.61,.36,1), calc-позиции стрелок
у краёв листа, отсутствие 3D/слайдов/старых фейдов, сцена .pages-stage, печать,
day-motion сохранён), поведение в Chromium:
— стрелки ← → в 20–35px от краёв .sheet, по центру видимой области, фиксированы
  (стоят при прокрутке), лист не перекрывают, не прибиты к краям монитора;
— переход ВПЕРЁД и НАЗАД покадровым сэмплером rAF: старая и новая полоса
  существуют ОДНОВРЕМЕННО (кроссфейд, старая — слой absolute поверх сцены),
  новая входит translateY(14px→0) вперёд / (-14px→0) назад, без matrix3d,
  прокрутка к началу новой полосы плавная (монотонная, много промежуточных
  значений, без мгновенного скачка), после оседания scrollY=0, верх полосы = 0,
  классы и minHeight вычищены;
— hammer, края, геометрия идентична потоковой версии без JS, ширины 1300/1100/390,
  prefers-reduced-motion, печать, консоль;
— покадровую идентичность полос в покое синхронному контролю day-navfade (0cdfa1a).
В конце — рендеры v18_* и композит preview-all.png.
Запуск из корня репо:  python3 worktmp/qa_navglide.py
"""
import os
import re
import sys

ROOT = os.getcwd()
HTML = os.path.join(ROOT, 'anna-malboro', 'daily-03-10-2026.html')
REND = os.path.join(os.path.dirname(ROOT), 'renders')
URL = 'file://' + HTML

OK, BAD = [], []


def chk(name, cond, detail=''):
    (OK if cond else BAD).append(name)
    print(('PASS  ' if cond else 'FAIL  ') + name + (('  · ' + str(detail)) if detail else ''))


h = open(HTML, encoding='utf-8').read()

# контрольная версия (day-navfade) для проверки идентичности покоя — из истории git
import subprocess
OLD_SHA = '0cdfa1a'
SCRATCH = os.path.join(os.path.dirname(ROOT), 'scratch_qa')
os.makedirs(SCRATCH, exist_ok=True)
OLD_HTML = os.path.join(SCRATCH, 'old_day_navfade.html')
HAVE_OLD = True
try:
    blob = subprocess.run(['git', '-C', ROOT, 'show',
                           f'{OLD_SHA}:anna-malboro/daily-03-10-2026.html'],
                          capture_output=True, check=True).stdout
    with open(OLD_HTML, 'wb') as fh:
        fh.write(blob)
except Exception as e:  # noqa: BLE001
    HAVE_OLD = False
    print('WARN: контрольная версия day-navfade недоступна:', e)

# ------------------------------ статика -------------------------------------
chk('S1 штамп day-navglide', '/* SFN-DESIGN-029: day-navglide · 03.10.2026 */' in h)
chk('S2 маркер day-navglide', '<!-- SFN · 2026 · 029 · day-navglide -->' in h)
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
chk('S8 в кейфреймах только opacity/translateY (нет translateX/rotate/scale)',
    len(kf_wins) == 3 and all(('translateX' not in w and 'rotate' not in w
                               and 'scale' not in w) for w in kf_wins))
_mb_i = h.index('@media (min-width:1300px)')
mb = h[_mb_i:h.index('/* ==== мобильная версия', _mb_i)]
chk('S9 стрелки у краёв листа через calc от центральной оси (не left:0/right:0)',
    'left:calc(50% - 640px)' in mb and 'right:calc(50% - 640px)' in mb
    and 'top:50%;transform:translateY(-50%)' in mb
    and 'left:0' not in mb and 'right:0;' not in mb)
chk('S10 навигация фиксирована; мобильный компактный блок сохранён',
    '.sheetnav{display:none;position:fixed;z-index:120;top:8px;left:50%;' in h
    and 'html.js-nav .sheetnav{display:flex}' in h
    and 'html.js-nav .sheetnav{display:contents}' in mb)
chk('S11 полосы и навигация на месте',
    'id="newspaper"' in h and h.count('<section class="sheet" id="p') == 4
    and all(x in h for x in ('id="navPrev"', 'id="navNext"', 'id="navCount"', '1 / 4')))
chk('S12 нет inline-стилей', 'style="' not in h)
chk('S13 12 кадров на месте', h.count('data:image/jpeg;base64,') == 12
    and all(f'id="a{n:02d}"' in h for n in range(1, 13)))
chk('S14 оболочка/палитра не тронуты',
    ':root{--paper:#f2ede3;--ink:#1a1714;--ox:#9e2b25' in h
    and '.sheet{max-width:1120px' in h and h.count(':root{') == 2)
chk('S15 day-motion загрузки сохранён',
    'sfn-rise' in h and '#p4.sheet{animation-delay:.18s}' in h
    and '.ph:hover img{transform:scale(1.02)}' in h)
chk('S16 печать: полосы в потоке (relative), сцена без minHeight, навигация скрыта',
    '.sheetnav{display:none!important}' in h
    and 'html.js-nav #newspaper{min-height:0!important}' in h
    and 'html.js-nav #newspaper .sheet{display:block!important;position:relative!important;' in h
    and 'opacity:1!important;transform:none!important' in h)
chk('S17 логика переключения и плавной прокрутки',
    all(x in h for x in ('js-nav', 'busy', 'setTimeout', 'requestAnimationFrame',
                         'cancelAnimationFrame', 'minHeight', 'DUR=600', 'cb(t,.22,.36)',
                         'scrollTo(0,0)', "querySelectorAll('.sheet')",
                         'page-exit', 'page-enter-next', 'page-enter-prev', 'is-off',
                         'html.js-nav #newspaper .sheet{margin-top:0}')))

# ------------------------------ браузер -------------------------------------
from playwright.sync_api import sync_playwright

STATE = """() => {
  const g = i => document.getElementById('p' + i);
  const cs = el => getComputedStyle(el);
  const wrap = document.getElementById('newspaper');
  return {
    jsnav: document.documentElement.classList.contains('js-nav'),
    cls: [1,2,3,4].map(i => g(i).className),
    disp: [1,2,3,4].map(i => cs(g(i)).display),
    op:  [1,2,3,4].map(i => cs(g(i)).opacity),
    tr:  [1,2,3,4].map(i => cs(g(i)).transform),
    pos: [1,2,3,4].map(i => cs(g(i)).position),
    tops:[1,2,3,4].map(i => +g(i).getBoundingClientRect().top.toFixed(1)),
    counter: document.getElementById('navCount').textContent,
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
  };
}"""

NAVRECT = """() => {
  const r = el => { const b = el.getBoundingClientRect();
    return {t:b.top,l:b.left,r:b.right,b:b.bottom,cx:b.left+b.width/2,cy:b.top+b.height/2,
            w:b.width,h:b.height}; };
  const nav = document.querySelector('.sheetnav');
  return {
    sheet: r(document.getElementById('p1')),
    prev: r(document.getElementById('navPrev')),
    next: r(document.getElementById('navNext')),
    count: r(document.getElementById('navCount')),
    bar: r(nav),
    dispNav: getComputedStyle(nav).display,
    posPrev: getComputedStyle(document.getElementById('navPrev')).position,
    posNext: getComputedStyle(document.getElementById('navNext')).position,
    posCount: getComputedStyle(document.getElementById('navCount')).position,
    vw: window.innerWidth, vh: window.innerHeight,
  };
}"""

STATIC = """() => {
  const g = i => document.getElementById('p' + i);
  return {
    jscls: document.documentElement.className,
    heights: [1,2,3,4].map(i => g(i).offsetHeight),
    tops: [1,2,3,4].map(i => g(i).offsetTop),
    a01top: document.getElementById('a01').offsetTop,
    a05top: document.getElementById('a05').offsetTop,
    a12top: document.getElementById('a12').offsetTop,
    navDisp: getComputedStyle(document.querySelector('.sheetnav')).display,
  };
}"""

# покадровый сэмплер перехода: пишет состояние всех полос каждый кадр rAF,
# на 3-м кадре диспатчит клик — никаких гонок между вызовами playwright
SAMPLER = """(cfg) => new Promise(res => {
  const g = i => document.getElementById('p' + i);
  window.scrollTo(0, cfg.y0);
  const rec = [];
  requestAnimationFrame(function tick(){
    const fr = {y: Math.round(window.scrollY),
                sw: document.documentElement.scrollWidth,
                mh: document.getElementById('newspaper').style.minHeight, s: []};
    for (let i = 1; i <= 4; i++){
      const c = getComputedStyle(g(i));
      fr.s.push({d: c.display, o: +(+c.opacity).toFixed(3), t: c.transform,
                 p: c.position, c: g(i).className});
    }
    rec.push(fr);
    if (rec.length === 3) document.getElementById(cfg.btn)
      .dispatchEvent(new MouseEvent('click', {bubbles: true}));
    if (rec.length < cfg.n) requestAnimationFrame(tick); else res(rec);
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
    chk('NJ1 без JS: навигация скрыта, режима нет',
        base['navDisp'] == 'none' and 'js-nav' not in base['jscls'])
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
    chk('B2 счётчик 1 / 4, назад неактивна',
        s0['counter'] == '1 / 4' and s0['prevD'] and not s0['nextD'])
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
    chk('B7 счётчик N / 4 — со стрелками (в левом поле, лист не накрывает)',
        nr['posCount'] == 'fixed' and nr['count']['t'] >= nr['prev']['b'] - 6
        and abs(nr['count']['cx'] - nr['prev']['cx']) <= 6
        and nr['count']['r'] <= nr['sheet']['l'] - 8,
        (round(nr['count']['t']), round(nr['prev']['b'])))
    pg.evaluate("window.scrollTo(0,1200)")
    pg.wait_for_timeout(350)
    nr2 = pg.evaluate(NAVRECT)
    same = all(abs(nr[k]['t'] - nr2[k]['t']) <= 1 and abs(nr[k]['l'] - nr2[k]['l']) <= 1
               for k in ('prev', 'next', 'count'))
    chk('B8 навигация доступна при прокрутке — стоит на месте', same)
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(250)
    chk('B9 нет горизонт. переполнения, стрелки в экране',
        s0['scrollW'] <= s0['innerW'] + 1
        and nr['prev']['l'] >= 0 and nr['next']['r'] <= nr['vw']
        and nr['prev']['t'] >= 0 and nr['prev']['b'] <= nr['vh'])
    os.makedirs(REND, exist_ok=True)
    pg.screenshot(path=os.path.join(REND, 'v18_nav_desktop.png'))
    chk('R1 рендер десктоп-навигации', os.path.exists(os.path.join(REND, 'v18_nav_desktop.png')))

    # --- переход ВПЕРЁД: покадровый сэмплер из глубокой прокрутки ---
    p1h = pg.evaluate("document.getElementById('p1').offsetHeight")
    y0f = min(2500, p1h - 1000)
    rec_f = pg.evaluate(SAMPLER, {'y0': y0f, 'btn': 'navNext', 'n': 55})
    pre, post = rec_f[:3], rec_f[3:]
    chk('F1 до клика: вид внизу p1, p2 скрыта',
        all(abs(f['y'] - y0f) <= 2 for f in pre)
        and pre[0]['s'][0]['d'] == 'block' and pre[0]['s'][1]['d'] == 'none', y0f)
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
    last = post[-1]
    chk('F7 осела: старая снята (display:none), новая opacity 1 / transform none / классы чистые',
        last['s'][0]['d'] == 'none' and last['s'][1]['o'] >= 0.999
        and last['s'][1]['t'] == 'none' and 'page-enter-next' not in last['s'][1]['c']
        and 'page-exit' not in last['s'][0]['c'] and 'is-off' in last['s'][0]['c'])
    f_set = pg.evaluate(STATE)
    chk('F8 после перехода: scrollY=0, p2 открыта с самого верха, счётчик 2 / 4, кнопки живы',
        f_set['scrollY'] == 0 and abs(f_set['tops'][1]) <= 2
        and f_set['disp'] == ['none', 'block', 'none', 'none']
        and f_set['counter'] == '2 / 4' and not f_set['prevD'] and not f_set['nextD']
        and not any(f_set['busyCls']) and f_set['minH'] == '',
        (f_set['scrollY'], f_set['tops'][1], f_set['minH']))
    chk('G1 геометрия p2 идентична потоковой версии без JS',
        abs(f_set['heights'][1] - base['heights'][1]) <= 2
        and abs(f_set['a05top'] - base['a05top']) <= 2,
        (f_set['heights'][1], base['heights'][1], f_set['a05top'], base['a05top']))

    # --- кадр середины перехода для монтажa (p2 → p3) ---
    p2h = pg.evaluate("document.getElementById('p2').offsetHeight")
    pg.evaluate(f"window.scrollTo(0,{min(2200, p2h - 1000)})")
    pg.wait_for_timeout(200)
    pg.click('#navNext')
    pg.wait_for_timeout(170)
    pg.screenshot(path=os.path.join(REND, 'v18_crossfade_mid.png'))
    pg.wait_for_timeout(1200)
    m1 = pg.evaluate(STATE)
    chk('M1 середина перехода снята, p3 осела',
        os.path.exists(os.path.join(REND, 'v18_crossfade_mid.png'))
        and m1['counter'] == '3 / 4' and m1['scrollY'] == 0)

    # --- переход НАЗАД: покадровый сэмплер (p3 → p2) ---
    p3h = pg.evaluate("document.getElementById('p3').offsetHeight")
    y0b = min(1800, p3h - 1000)
    rec_b = pg.evaluate(SAMPLER, {'y0': y0b, 'btn': 'navPrev', 'n': 55})
    pre_b, post_b = rec_b[:3], rec_b[3:]
    chk('K1 назад, до клика: вид внизу p3, p1 скрыта',
        all(abs(f['y'] - y0b) <= 2 for f in pre_b)
        and pre_b[0]['s'][2]['d'] == 'block' and pre_b[0]['s'][1]['d'] == 'none', y0b)
    sim_b = [f for f in post_b if f['s'][2]['d'] == 'block' and f['s'][1]['d'] == 'block'
             and 0.02 < f['s'][2]['o'] < 0.98 and 0.02 < f['s'][1]['o'] < 0.98]
    ok_layer_b = any(f['s'][2]['p'] == 'absolute' and 'page-exit' in f['s'][2]['c']
                     for f in sim_b)
    chk('K2 назад: кроссфейд — p3 уходит слоем, p2 появляется одновременно',
        len(sim_b) >= 5 and ok_layer_b, f'кадров вместе: {len(sim_b)}')
    ent_b = [f for f in post_b if 'page-enter-prev' in f['s'][1]['c']]
    tys_b = [v for v in (ty_of(f['s'][1]['t']) for f in ent_b) if v is not None]
    nom3d_b = all('matrix3d' not in f['s'][i]['t'] for f in rec_b for i in range(4))
    chk('K3 назад: p2 едет сверху вниз translateY(-14px→0), без 3D',
        len(ent_b) >= 5 and sum(1 for v in tys_b if -14.6 < v < -0.2) >= 2
        and all(-14.6 <= v <= 0.5 for v in tys_b) and nom3d_b,
        [round(v, 1) for v in tys_b[:6]])
    ys_b = [f['y'] for f in post_b]
    mids_b = {y for y in ys_b if 0 < y < y0b}
    drops_b = [ys_b[i] - ys_b[i + 1] for i in range(len(ys_b) - 1)]
    chk('K4 назад: прокрутка к началу p2 плавная, финиш scrollY=0',
        all(drops_b[i] >= 0 for i in range(len(drops_b))) and len(mids_b) >= 4
        and max(drops_b) < 900 and ys_b[-1] == 0, (len(mids_b), max(drops_b)))
    last_b = post_b[-1]
    b_set = pg.evaluate(STATE)
    chk('K5 назад: осела — p2 с верха (scrollY=0, top≈0), p3 скрыта, классы чистые, 2 / 4',
        last_b['s'][2]['d'] == 'none' and last_b['s'][1]['o'] >= 0.999
        and last_b['s'][1]['t'] == 'none' and rec_b[-1]['mh'] == ''
        and b_set['scrollY'] == 0 and abs(b_set['tops'][1]) <= 2
        and b_set['counter'] == '2 / 4' and not any(b_set['busyCls']))

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
    pg.wait_for_timeout(1500)
    h1 = pg.evaluate(STATE)
    chk('H1 hammer: ровно одно переключение, p2',
        h1['counter'] == '2 / 4' and h1['disp'] == ['none', 'block', 'none', 'none'])
    chk('H2 hammer: состояние цело — классы/minHeight вычищены, scrollY=0',
        not any(h1['busyCls']) and h1['op'][1] == '1' and h1['minH'] == ''
        and h1['scrollY'] == 0 and not h1['prevD'] and not h1['nextD'])

    # --- до конца: p4 ---
    for _ in range(2):
        pg.click('#navNext')
        pg.wait_for_timeout(1300)
    e1 = pg.evaluate(STATE)
    chk('E1 дошли до p4: 4 / 4, вперёд неактивна',
        e1['counter'] == '4 / 4' and e1['nextD'] and not e1['prevD']
        and e1['disp'] == ['none', 'none', 'none', 'block'])
    chk('G3 геометрия p4 идентична потоковой версии без JS',
        abs(e1['heights'][3] - base['heights'][3]) <= 2
        and abs(e1['a12top'] - base['a12top']) <= 2)
    pg.evaluate("document.getElementById('navNext').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(150)
    e2 = pg.evaluate(STATE)
    chk('E2 на p4 вперёд не ломается',
        e2['counter'] == '4 / 4' and e2['disp'][3] == 'block' and not any(e2['busyCls']))

    # --- рендеры полос в покое ---
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    for i in range(1, 5):
        if i > 1:
            pg.click('#navNext')
            pg.wait_for_timeout(1300)
        pg.mouse.move(0, 0)
        pg.wait_for_timeout(400)
        pg.query_selector(f'#p{i}').screenshot(path=os.path.join(REND, f'v18_p{i}.png'))
    chk('R2 рендеры полос сделаны',
        all(os.path.exists(os.path.join(REND, f'v18_p{i}.png')) for i in range(1, 5)))

    # --- ширина 1300: стрелки по-прежнему вплотную к листу ---
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
    pg.wait_for_timeout(1100)
    s13e = pg.evaluate(STATE)
    chk('W1 @1300px: стрелки у листа (20–35px), в экране, переход без переполнения',
        n13['dispNav'] == 'contents' and 20 <= g13L <= 35 and 20 <= g13R <= 35
        and n13['prev']['l'] >= 0 and n13['next']['r'] <= n13['vw']
        and s13['scrollW'] <= s13['innerW'] + 1 and s13m['scrollW'] <= s13m['innerW'] + 1
        and s13e['counter'] == '2 / 4',
        (round(g13L, 1), round(g13R, 1), round(n13['prev']['l'], 1)))

    # --- узкие экраны: компактный блок у верха ---
    pg.set_viewport_size({'width': 1100, 'height': 900})
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    w1 = pg.evaluate(NAVRECT)
    ok_bar = (w1['dispNav'] == 'flex' and w1['bar']['t'] <= 14
              and abs(w1['bar']['cx'] - w1['vw'] / 2) <= 4 and w1['prev']['t'] < 60)
    sw1 = pg.evaluate(STATE)
    pg.click('#navNext')
    pg.wait_for_timeout(250)
    swm = pg.evaluate(STATE)
    pg.wait_for_timeout(1100)
    chk('W2 @1100px: компактный блок у верха, счётчик между стрелками, без переполнения',
        ok_bar and sw1['scrollW'] <= sw1['innerW'] + 1
        and swm['scrollW'] <= swm['innerW'] + 1
        and w1['prev']['r'] < w1['count']['l'] and w1['count']['r'] < w1['next']['l'],
        (round(w1['bar']['t']), round(w1['bar']['cx']), w1['dispNav']))

    pg.set_viewport_size({'width': 390, 'height': 844})
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    w2 = pg.evaluate(NAVRECT)
    ok_m = (w2['dispNav'] == 'flex' and w2['bar']['t'] <= 14
            and w2['bar']['l'] >= 0 and w2['bar']['r'] <= w2['vw']
            and abs(w2['bar']['cx'] - w2['vw'] / 2) <= 4)
    sw2 = pg.evaluate(STATE)
    pg.click('#navNext')
    pg.wait_for_timeout(250)
    sw2m = pg.evaluate(STATE)
    pg.wait_for_timeout(1100)
    pg.click('#navPrev')
    pg.wait_for_timeout(1300)
    w3 = pg.evaluate(STATE)
    chk('W3 @390px: блок в экране, без переполнения (покой+mid), возврат на p1',
        ok_m and sw2['scrollW'] <= sw2['innerW'] + 1
        and sw2m['scrollW'] <= sw2m['innerW'] + 1 and w3['counter'] == '1 / 4'
        and w3['scrollY'] == 0,
        (round(w2['bar']['l']), round(w2['bar']['r'])))
    pg.mouse.move(0, 0)
    pg.wait_for_timeout(400)
    pg.query_selector('#p1').screenshot(path=os.path.join(REND, 'v18_mobile_p1.png'))
    pg.screenshot(path=os.path.join(REND, 'v18_mobile_nav.png'))

    # --- prefers-reduced-motion ---
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    pr = ctx.new_page()
    pr.goto(URL, wait_until='load')
    pr.wait_for_timeout(900)
    pr.click('#navNext')
    pr.wait_for_timeout(250)
    r1 = pr.evaluate(STATE)
    chk('RM1 reduced-motion: мгновенное переключение, классы перехода не ставятся',
        r1['counter'] == '2 / 4' and r1['disp'][1] == 'block' and r1['op'][1] == '1'
        and r1['tr'][1] == 'none' and not r1['prevD'] and r1['scrollY'] == 0
        and not any(r1['busyCls']) and 'is-off' in r1['cls'][0])
    pr.click('#navNext')
    pr.wait_for_timeout(250)
    r2 = pr.evaluate(STATE)
    chk('RM2 reduced-motion: блокировка не залипает', r2['counter'] == '3 / 4', r2['counter'])
    ctx.close()

    # --- печать ---
    ctx2 = br.new_context(viewport={'width': 1440, 'height': 900})
    pp = ctx2.new_page()
    pp.goto(URL, wait_until='load')
    pp.wait_for_timeout(1800)
    pp.click('#navNext')
    pp.wait_for_timeout(1300)
    pp.emulate_media(media='print')
    pp.wait_for_timeout(300)
    prn = pp.evaluate("""() => {
      const g = i => document.getElementById('p' + i);
      const cs = el => getComputedStyle(el);
      return {
        disp: [1,2,3,4].map(i => cs(g(i)).display),
        op: [1,2,3,4].map(i => cs(g(i)).opacity),
        pos: [1,2,3,4].map(i => cs(g(i)).position),
        heights: [1,2,3,4].map(i => g(i).offsetHeight),
        tops: [1,2,3,4].map(i => g(i).offsetTop),
        nav: cs(document.querySelector('.sheetnav')).display,
        minH: cs(document.getElementById('newspaper')).minHeight,
      };
    }""")
    chk('PR1 печать: 4 полосы в потоке (relative), все видимы',
        prn['disp'] == ['block'] * 4 and all(x > 1000 for x in prn['heights'])
        and prn['op'] == ['1'] * 4 and prn['pos'] == ['relative'] * 4
        and all(prn['tops'][i] < prn['tops'][i + 1] for i in range(3)), prn['tops'])
    chk('PR2 печать: навигация скрыта', prn['nav'] == 'none')
    ctx2.close()

    # --- синхронный контроль прошлой версии (day-navfade): рендеры покоя ---
    if HAVE_OLD:
        cp = br.new_page(viewport={'width': 1440, 'height': 900})
        cp.goto('file://' + OLD_HTML, wait_until='load')
        cp.wait_for_timeout(2200)
        for i in range(1, 5):
            if i > 1:
                cp.click('#navNext')
                cp.wait_for_timeout(1400)
            cp.mouse.move(0, 0)
            cp.wait_for_timeout(400)
            cp.query_selector(f'#p{i}').screenshot(path=os.path.join(SCRATCH, f'ctrl_g_p{i}.png'))
        cp.close()
        cmg = br.new_page(viewport={'width': 390, 'height': 844})
        cmg.goto('file://' + OLD_HTML, wait_until='load')
        cmg.wait_for_timeout(2200)
        cmg.mouse.move(0, 0)
        cmg.wait_for_timeout(400)
        cmg.query_selector('#p1').screenshot(path=os.path.join(SCRATCH, 'ctrl_g_mobile_p1.png'))
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
            a = Image.open(os.path.join(SCRATCH, f'ctrl_g_p{i}.png')).convert('RGB')
            b = Image.open(os.path.join(REND, f'v18_p{i}.png')).convert('RGB')
            if a.size != b.size:
                bad_i.append((i, a.size, b.size))
                continue
            bb, mx, st = maxdelta(a, b)
            # допуск: растровый шум JPEG/AA (≤64 пикселей с дельтой >8 и ≤24 по яркости)
            if st > 64 or mx > 24:
                bad_i.append((i, bb, mx, st))
        chk('I1 полосы в покое идентичны day-navfade (синхр. контроль)', not bad_i, bad_i)
        a = Image.open(os.path.join(SCRATCH, 'ctrl_g_mobile_p1.png')).convert('RGB')
        b = Image.open(os.path.join(REND, 'v18_mobile_p1.png')).convert('RGB')
        if a.size != b.size:
            chk('I2 мобильная p1 идентична day-navfade (синхр. контроль)', False, (a.size, b.size))
        else:
            # верхняя полоса 0–70px: там компактная навигация (идентична по стилям,
            # но срезается, чтобы сравнение касалось только бумаги)
            aa = a.crop((0, 70, a.width, a.height))
            bbim = b.crop((0, 70, b.width, b.height))
            bb, mx, st = maxdelta(aa, bbim)
            chk('I2 мобильная p1 идентична day-navfade (синхр. контроль, ниже навигации)',
                st <= 64 and mx <= 24, (bb, mx, st))
    else:
        chk('I1/I2 идентичность (нет контроля day-navfade)', False, 'нет blob в git')
except FileNotFoundError as e:
    chk('I1/I2 идентичность', False, e)

# ------------------------------ композит ------------------------------------
try:
    from PIL import Image
    desk = Image.open(os.path.join(REND, 'v18_nav_desktop.png')).convert('RGB')
    mid = Image.open(os.path.join(REND, 'v18_crossfade_mid.png')).convert('RGB')
    mob = Image.open(os.path.join(REND, 'v18_mobile_nav.png')).convert('RGB')
    ims = [Image.open(os.path.join(REND, f'v18_p{i}.png')).convert('RGB') for i in range(1, 5)]
    W, GAP, BG = 1120, 12, (242, 237, 227)

    def fit(im, w):
        return im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS)

    desk_s = fit(desk, W)
    mid_s = fit(mid, (W - GAP) // 2)
    mob_s = fit(mob, (W - GAP) // 2)
    cells = [fit(im, (W - GAP) // 2) for im in ims]
    row_h = max(mid_s.height, mob_s.height)
    grid_h = max(cells[0].height, cells[1].height) + GAP + max(cells[2].height, cells[3].height)
    canvas = Image.new('RGB', (W, desk_s.height + GAP + row_h + GAP + grid_h + GAP * 2), BG)
    y = GAP
    canvas.paste(desk_s, (0, y)); y += desk_s.height + GAP
    canvas.paste(mid_s, (0, y)); canvas.paste(mob_s, ((W - GAP) // 2 + GAP, y))
    y += row_h + GAP
    canvas.paste(cells[0], (0, y)); canvas.paste(cells[1], ((W - GAP) // 2 + GAP, y))
    y += max(cells[0].height, cells[1].height) + GAP
    canvas.paste(cells[2], (0, y)); canvas.paste(cells[3], ((W - GAP) // 2 + GAP, y))
    canvas.save(os.path.join(REND, 'preview-all.png'))
    chk('Z1 композит preview-all.png', True, canvas.size)
except Exception as e:  # noqa: BLE001
    chk('Z1 композит preview-all.png', False, e)

print()
print(f'ИТОГ: {len(OK)} PASS / {len(BAD)} FAIL')
if BAD:
    print('ПРОВАЛЕНО:', '; '.join(BAD))
    sys.exit(1)
