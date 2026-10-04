#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN QA day-navfade: фиксированная навигация + фейд-переключение полос (03.10.2026).

Проверяет: статику HTML (штамп day-navfade, pageFadeIn/pageFadeOut/page-enter,
полное отсутствие 3D-перелистывания, фиксированная навигация, десктоп-сплит
≥1300px, длительности 400–450мс, печать, day-motion сохранён), поведение в
Chromium (режим одной полосы, раскладка ←/→/счётчика, неизменность при прокрутке,
плавный фейд-out → фейд-in без matrix3d и без горизонтальных слайдов, возврат
вида к началу газеты, блокировка повторных нажатий, геометрия полос и материалов
идентична потоковой версии без JS, предпочтительное уменьшение движения, печать, консоль),
покадровую идентичность полос в покое рендерам v16 (day-flip).
В конце — рендеры v17_* и композит preview-all.png.
Запуск из корня репо:  python3 worktmp/qa_navfade.py
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

# контрольная версия (day-flip) для проверки идентичности покоя — из истории git
import subprocess
OLD_SHA = '85f551c'
SCRATCH = os.path.join(os.path.dirname(ROOT), 'scratch_qa')
os.makedirs(SCRATCH, exist_ok=True)
OLD_HTML = os.path.join(SCRATCH, 'old_day_flip.html')
HAVE_OLD = True
try:
    blob = subprocess.run(['git', '-C', ROOT, 'show',
                           f'{OLD_SHA}:anna-malboro/daily-03-10-2026.html'],
                          capture_output=True, check=True).stdout
    with open(OLD_HTML, 'wb') as fh:
        fh.write(blob)
except Exception as e:  # noqa: BLE001
    HAVE_OLD = False
    print('WARN: контрольная версия day-flip недоступна:', e)

# ------------------------------ статика -------------------------------------
chk('S1 штамп day-navfade', '/* SFN-DESIGN-029: day-navfade · 03.10.2026 */' in h)
chk('S2 маркер day-navfade', '<!-- SFN · 2026 · 029 · day-navfade -->' in h)
chk('S3 появление: pageFadeIn .45s ease both',
    '.sheet.page-enter{animation:pageFadeIn .45s ease both}' in h
    and '@keyframes pageFadeIn{from{opacity:0;transform:translateY(8px)}'
         'to{opacity:1;transform:translateY(0)}}' in h)
chk('S4 исчезновение: pageFadeOut .4s ease both',
    '.sheet.is-turn{animation:pageFadeOut .4s ease both}' in h
    and '@keyframes pageFadeOut{from{opacity:1}to{opacity:0}}' in h)
chk('S5 3D-перелистывание удалено полностью',
    all(t not in h for t in ('rotateY', 'perspective', 'backface-visibility',
                             'transform-origin', 'flipshade', 'js-flip')))
wins = [h[m.start():m.start() + 220] for m in re.finditer(r'@keyframes pageFade', h)]
chk('S6 в кейфреймах нет слайдов/поворотов',
    len(wins) == 2 and all('translateX' not in w and 'rotate' not in w for w in wins))
durs = re.findall(r'animation:pageFade\w+ \.(\d+)s ease both', h)
chk('S7 длительности 400–500мс', sorted(durs) == ['4', '45'], durs)
chk('S8 навигация фиксирована',
    '.sheetnav{display:none;position:fixed;z-index:120;top:8px;left:50%' in h)
chk('S9 десктоп-сплит ≥1300px',
    '@media (min-width:1300px)' in h and 'html.js-nav .sheetnav{display:contents}' in h
    and '#navPrev{position:fixed;left:18px;top:50%;transform:translateY(-50%)' in h
    and '#navNext{position:fixed;right:18px;top:50%;transform:translateY(-50%)' in h)
chk('S10 полосы и навигация',
    'id="newspaper"' in h and h.count('<section class="sheet" id="p') == 4
    and all(x in h for x in ('id="navPrev"', 'id="navNext"', 'id="navCount"', '1 / 4')))
chk('S11 нет inline-стилей', 'style="' not in h)
chk('S12 12 кадров на месте', h.count('data:image/jpeg;base64,') == 12
    and all(f'id="a{n:02d}"' in h for n in range(1, 13)))
chk('S13 оболочка/палитра не тронуты',
    ':root{--paper:#f2ede3;--ink:#1a1714;--ox:#9e2b25' in h
    and '.sheet{max-width:1120px' in h and h.count(':root{') == 2)
chk('S14 day-motion загрузки сохранён',
    'sfn-rise' in h and '#p4.sheet{animation-delay:.18s}' in h
    and '.ph:hover img{transform:scale(1.02)}' in h)
chk('S15 печать: полосы в потоке, навигация скрыта',
    '.sheetnav{display:none!important}' in h
    and 'html.js-nav #newspaper .sheet{display:block!important' in h)
chk('S16 логика переключения',
    all(x in h for x in ('js-nav', 'busy', 'setTimeout', 'scrollTo(0,0)',
                         "querySelectorAll('.sheet')", 'page-enter', 'is-turn', 'is-off')))

# ------------------------------ браузер -------------------------------------
from playwright.sync_api import sync_playwright

STATE = """() => {
  const g = i => document.getElementById('p' + i);
  const cs = el => getComputedStyle(el);
  return {
    jsnav: document.documentElement.classList.contains('js-nav'),
    cls: [1,2,3,4].map(i => g(i).className),
    disp: [1,2,3,4].map(i => cs(g(i)).display),
    op:  [1,2,3,4].map(i => cs(g(i)).opacity),
    tr:  [1,2,3,4].map(i => cs(g(i)).transform),
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
    busyCls: [1,2,3,4].map(i => /page-enter|is-turn/.test(g(i).className)),
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


def ty_of(tr):
    m = re.match(r'matrix\(([^)]+)\)', tr or '')
    return float(m.group(1).split(',')[5]) if m else None


def ty_mid(tr):
    """translateY из matrix в середине pageFadeIn: 0 < ty <= 8."""
    v = ty_of(tr)
    return v is not None and 0.2 < v <= 8.5 and not tr.startswith('matrix3d')


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
    chk('B1 режим одной полосы включён', s0['jsnav'])
    chk('B2 счётчик 1 / 4, назад неактивна',
        s0['counter'] == '1 / 4' and s0['prevD'] and not s0['nextD'])
    chk('B3 p1 видна, p2–p4 скрыты', s0['disp'] == ['block', 'none', 'none', 'none'], s0['disp'])
    chk('B4 ← фиксирована слева от газеты, по центру высоты',
        nr['posPrev'] == 'fixed' and nr['prev'].get('r', 9e9) <= nr['sheet']['l'] - 8
        and abs(nr['prev']['cy'] - nr['vh'] / 2) <= 70 and nr['prev']['w'] == 56,
        (round(nr['prev']['r']), round(nr['sheet']['l']), round(nr['prev']['cy'])))
    chk('B5 → фиксирована справа от газеты, по центру высоты',
        nr['posNext'] == 'fixed' and nr['next']['l'] >= nr['sheet']['r'] + 8
        and abs(nr['next']['cy'] - nr['vh'] / 2) <= 70,
        (round(nr['next']['l']), round(nr['sheet']['r'])))
    chk('B6 счётчик фиксирован под левой стрелкой (не на листе)',
        nr['posCount'] == 'fixed' and nr['count']['t'] >= nr['prev']['b'] - 6
        and abs(nr['count']['cx'] - nr['prev']['cx']) <= 6
        and nr['count']['r'] <= nr['sheet']['l'] - 8,
        (round(nr['count']['t']), round(nr['prev']['b'])))
    pg.evaluate("window.scrollTo(0,1200)")
    pg.wait_for_timeout(350)
    nr2 = pg.evaluate(NAVRECT)
    same = all(abs(nr[k]['t'] - nr2[k]['t']) <= 1 and abs(nr[k]['l'] - nr2[k]['l']) <= 1
               for k in ('prev', 'next', 'count'))
    chk('B7 навигация стоит на месте при прокрутке', same)
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(250)
    chk('B8 нет горизонт. переполнения', s0['scrollW'] <= s0['innerW'] + 1,
        (s0['scrollW'], s0['innerW']))
    os.makedirs(REND, exist_ok=True)
    pg.screenshot(path=os.path.join(REND, 'v17_nav_desktop.png'))
    chk('R1 рендер десктоп-навигации', os.path.exists(os.path.join(REND, 'v17_nav_desktop.png')))

    # --- переключение вперёд из глубокой прокрутки ---
    pg.evaluate("window.scrollTo(0,2500)")
    pg.wait_for_timeout(250)
    s_pre = pg.evaluate("Math.round(window.scrollY)")
    pg.click('#navNext')
    pg.wait_for_timeout(200)
    f1 = pg.evaluate(STATE)
    op1 = float(f1['op'][0])
    chk('F1 старая полоса плавно исчезает (opacity, без transform)',
        0.05 < op1 < 0.95 and f1['tr'][0] == 'none' and f1['disp'][0] == 'block', round(op1, 2))
    chk('F2 кнопки заблокированы, счётчик впереди',
        f1['prevD'] and f1['nextD'] and f1['counter'] == '2 / 4')
    chk('F3 во время исчезновения прокрутка не дёргается',
        abs(f1['scrollY'] - s_pre) <= 2, (f1['scrollY'], s_pre))
    pg.wait_for_timeout(450)  # t≈650мс: старая исчезла, новая появляется
    f2 = pg.evaluate(STATE)
    op2 = float(f2['op'][1])
    chk('F4 новая полоса мягко появляется: opacity 0→1',
        f2['disp'] == ['none', 'block', 'none', 'none'] and 0.02 < op2 < 0.97, round(op2, 2))
    chk('F5 появление: только translateY(8px→0), без 3D', ty_mid(f2['tr'][1]), f2['tr'][1])
    chk('F6 вид вернулся к началу газеты (scrollY=0)', f2['scrollY'] == 0, f2['scrollY'])
    chk('F7 нет горизонт. переполнения mid-перехода',
        f2['scrollW'] <= f2['innerW'] + 1 and f1['scrollW'] <= f1['innerW'] + 1)
    pg.screenshot(path=os.path.join(REND, 'v17_fade_mid.png'))
    pg.wait_for_timeout(700)  # t≈1350мс: осела
    f3 = pg.evaluate(STATE)
    chk('F8 осела: p2 видна, opacity 1, transform none, классы сняты',
        f3['op'][1] == '1' and f3['tr'][1] == 'none' and not any(f3['busyCls'])
        and 'is-on' in f3['cls'][1] and 'page-enter' not in f3['cls'][1])
    chk('F9 кнопки разблокированы по краям',
        f3['counter'] == '2 / 4' and not f3['prevD'] and not f3['nextD'] and f3['scrollY'] == 0)
    chk('G1 геометрия p2 идентична потоковой версии',
        abs(f3['heights'][1] - base['heights'][1]) <= 2
        and abs(f3['a05top'] - base['a05top']) <= 2,
        (f3['heights'][1], base['heights'][1], f3['a05top'], base['a05top']))

    # --- hammer: 5 быстрых кликов ---
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    pg.evaluate("for(let i=0;i<5;i++)document.getElementById('navNext')"
                ".dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(1500)
    h1 = pg.evaluate(STATE)
    chk('H1 hammer: ровно одно переключение, p2',
        h1['counter'] == '2 / 4' and h1['disp'] == ['none', 'block', 'none', 'none'])
    chk('H2 hammer: состояние цело, классы сняты',
        not any(h1['busyCls']) and h1['op'][1] == '1' and not h1['prevD'] and not h1['nextD'])

    # --- переключение назад ---
    pg.click('#navPrev')
    pg.wait_for_timeout(650)
    k1 = pg.evaluate(STATE)
    chk('K1 назад: p1 мягко появляется (opacity<1, translateY)',
        k1['disp'][0] == 'block' and 0.02 < float(k1['op'][0]) < 0.97 and ty_mid(k1['tr'][0]))
    chk('K2 назад: счётчик сразу 1 / 4', k1['counter'] == '1 / 4')
    pg.wait_for_timeout(700)
    k2 = pg.evaluate(STATE)
    chk('K3 назад: p1 осела, назад неактивна',
        k2['op'][0] == '1' and k2['tr'][0] == 'none' and k2['prevD'] and not k2['nextD']
        and not any(k2['busyCls']))
    chk('G2 геометрия p1 идентична потоковой версии',
        abs(k2['heights'][0] - base['heights'][0]) <= 2
        and abs(k2['a01top'] - base['a01top']) <= 2,
        (k2['heights'][0], base['heights'][0]))

    # --- до конца: p4 ---
    for _ in range(3):
        pg.click('#navNext')
        pg.wait_for_timeout(1300)
    e1 = pg.evaluate(STATE)
    chk('E1 дошли до p4: 4 / 4, вперёд неактивна',
        e1['counter'] == '4 / 4' and e1['nextD'] and not e1['prevD']
        and e1['disp'] == ['none', 'none', 'none', 'block'])
    chk('G3 геометрия p4 идентична потоковой версии',
        abs(e1['heights'][3] - base['heights'][3]) <= 2
        and abs(e1['a12top'] - base['a12top']) <= 2)
    pg.evaluate("document.getElementById('navNext').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(120)
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
        pg.query_selector(f'#p{i}').screenshot(path=os.path.join(REND, f'v17_p{i}.png'))
    chk('R2 рендеры полос сделаны',
        all(os.path.exists(os.path.join(REND, f'v17_p{i}.png')) for i in range(1, 5)))

    # --- узкие экраны: компактный блок у верха ---
    pg.set_viewport_size({'width': 1100, 'height': 900})
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    w1 = pg.evaluate(NAVRECT)
    ok_bar = (w1['dispNav'] == 'flex' and w1['bar']['t'] <= 14
              and abs(w1['bar']['cx'] - w1['vw'] / 2) <= 4 and w1['prev']['t'] < 60)
    sw1 = pg.evaluate(STATE)
    pg.click('#navNext')
    pg.wait_for_timeout(650)
    swm = pg.evaluate(STATE)
    pg.wait_for_timeout(700)
    chk('W1 @1100px: компактный блок у верха, без переполнения (покой+mid)',
        ok_bar and sw1['scrollW'] <= sw1['innerW'] + 1 and swm['scrollW'] <= swm['innerW'] + 1,
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
    pg.wait_for_timeout(650)
    sw2m = pg.evaluate(STATE)
    pg.wait_for_timeout(700)
    pg.click('#navPrev')
    pg.wait_for_timeout(1300)
    w3 = pg.evaluate(STATE)
    chk('W2 @390px: блок в экране, без переполнения (покой+mid)',
        ok_m and sw2['scrollW'] <= sw2['innerW'] + 1 and sw2m['scrollW'] <= sw2m['innerW'] + 1,
        (round(w2['bar']['l']), round(w2['bar']['r'])))
    chk('W3 мобильная: вернулись на p1', w3['counter'] == '1 / 4', w3['counter'])
    pg.mouse.move(0, 0)
    pg.wait_for_timeout(400)
    pg.query_selector('#p1').screenshot(path=os.path.join(REND, 'v17_mobile_p1.png'))
    pg.screenshot(path=os.path.join(REND, 'v17_mobile_nav.png'))

    # --- prefers-reduced-motion ---
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    pr = ctx.new_page()
    pr.goto(URL, wait_until='load')
    pr.wait_for_timeout(800)
    pr.click('#navNext')
    pr.wait_for_timeout(200)
    r1 = pr.evaluate(STATE)
    chk('RM1 reduced-motion: мгновенное переключение',
        r1['counter'] == '2 / 4' and r1['disp'][1] == 'block' and r1['op'][1] == '1'
        and r1['tr'][1] == 'none' and not r1['prevD'])
    pr.click('#navNext')
    pr.wait_for_timeout(200)
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
        heights: [1,2,3,4].map(i => g(i).offsetHeight),
        tops: [1,2,3,4].map(i => g(i).offsetTop),
        nav: cs(document.querySelector('.sheetnav')).display,
      };
    }""")
    chk('PR1 печать: 4 полосы в потоке, все видимы',
        prn['disp'] == ['block'] * 4 and all(x > 1000 for x in prn['heights'])
        and prn['op'] == ['1'] * 4
        and all(prn['tops'][i] < prn['tops'][i + 1] for i in range(3)), prn['tops'])
    chk('PR2 печать: навигация скрыта', prn['nav'] == 'none')
    ctx2.close()

    # --- синхронный контроль прошлой версии (day-flip): рендеры покоя ---
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
            cp.query_selector(f'#p{i}').screenshot(path=os.path.join(SCRATCH, f'ctrl_p{i}.png'))
        cp.close()
        cmg = br.new_page(viewport={'width': 390, 'height': 844})
        cmg.goto('file://' + OLD_HTML, wait_until='load')
        cmg.wait_for_timeout(2200)
        cmg.mouse.move(0, 0)
        cmg.wait_for_timeout(400)
        cmg.query_selector('#p1').screenshot(path=os.path.join(SCRATCH, 'ctrl_mobile_p1.png'))
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
            a = Image.open(os.path.join(SCRATCH, f'ctrl_p{i}.png')).convert('RGB')
            b = Image.open(os.path.join(REND, f'v17_p{i}.png')).convert('RGB')
            if a.size != b.size:
                bad_i.append((i, a.size, b.size))
                continue
            bb, mx, st = maxdelta(a, b)
            # допуск: растровый шум JPEG/AA (≤64 пикселей с дельтой >8 и ≤24 по яркости);
            # реальное расхождение вёрстки дало бы тысячи сильных пикселей
            if st > 64 or mx > 24:
                bad_i.append((i, bb, mx, st))
        chk('I1 полосы в покое идентичны day-flip (синхр. контроль)', not bad_i, bad_i)
        a = Image.open(os.path.join(SCRATCH, 'ctrl_mobile_p1.png')).convert('RGB')
        b = Image.open(os.path.join(REND, 'v17_mobile_p1.png')).convert('RGB')
        if a.size != b.size:
            chk('I2 мобильная p1 идентична day-flip (синхр. контроль)', False, (a.size, b.size))
        else:
            # верхняя полоса 0–70px: там теперь фикс-навигация (в контроле её не было)
            aa = a.crop((0, 70, a.width, a.height))
            bbim = b.crop((0, 70, b.width, b.height))
            bb, mx, st = maxdelta(aa, bbim)
            chk('I2 мобильная p1 идентична day-flip (синхр. контроль, ниже навигации)',
                st <= 64 and mx <= 24, (bb, mx, st))
    else:
        chk('I1/I2 идентичность (нет контроля day-flip)', False, 'нет blob в git')
except FileNotFoundError as e:
    chk('I1/I2 идентичность', False, e)

# ------------------------------ композит ------------------------------------
try:
    from PIL import Image
    desk = Image.open(os.path.join(REND, 'v17_nav_desktop.png')).convert('RGB')
    mid = Image.open(os.path.join(REND, 'v17_fade_mid.png')).convert('RGB')
    mob = Image.open(os.path.join(REND, 'v17_mobile_nav.png')).convert('RGB')
    ims = [Image.open(os.path.join(REND, f'v17_p{i}.png')).convert('RGB') for i in range(1, 5)]
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
    chk('K1 композит preview-all.png', True, canvas.size)
except Exception as e:  # noqa: BLE001
    chk('K1 композит preview-all.png', False, e)

print()
print(f'ИТОГ: {len(OK)} PASS / {len(BAD)} FAIL')
if BAD:
    print('ПРОВАЛЕНО:', '; '.join(BAD))
    sys.exit(1)
