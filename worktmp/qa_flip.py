#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN QA day-flip: перелистывание полос выпуска 03.10.2026.

Проверяет: статику HTML (perspective / transform-origin / backface-visibility /
rotateY / #p1–#p4 / логика переключения), поведение в Chromium (состояния,
счётчик, блокировка повторных нажатий, физический поворот без opacity,
длительность ~800мс, отсутствие горизонтального переполнения, неизменность
геометрии полос и материалов), prefers-reduced-motion, печать, консоль.
В конце — рендеры v16_* и композит preview-all.png.
Запуск из корня репо:  python3 worktmp/qa_flip.py
"""
import math
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

# ------------------------------ статика -------------------------------------
chk('S1 штамп day-flip', '/* SFN-DESIGN-029: day-flip · 03.10.2026 */' in h)
chk('S2 маркер day-flip', '<!-- SFN · 2026 · 029 · day-flip -->' in h)
chk('S3 perspective', 'perspective:4800px' in h)
chk('S4 transform-origin', 'transform-origin:left center' in h)
chk('S5 backface-visibility', 'backface-visibility:hidden' in h)
chk('S6 rotateY(-95deg) x2', h.count('rotateY(-95deg)') >= 2)
chk('S7 обёртка #newspaper', 'id="newspaper"' in h and h.count('<section class="sheet" id="p') == 4)
chk('S8 навигация', all(x in h for x in ('id="navPrev"', 'id="navNext"', 'id="navCount"', '1 / 4')))
dur = [float(x) * 1000 for x in re.findall(r'transition:transform (\d*\.?\d+)s', h)]
chk('S9 длительность 700-900мс', bool(dur) and all(700 <= d <= 900 for d in dur), dur[:4])
chk('S10 логика переключения', all(x in h for x in (
    'transitionend', 'setTimeout(settle', 'busy', 'turn-next', 'is-off', "querySelectorAll('.sheet')")))
chk('S11 нет inline-стилей', 'style="' not in h)
chk('S12 12 кадров на месте', h.count('data:image/jpeg;base64,') == 12
    and all(f'id="a{n:02d}"' in h for n in range(1, 13)))
chk('S13 оболочка/palette не тронуты', ':root{--paper:#f2ede3;--ink:#1a1714;--ox:#9e2b25' in h
    and '.sheet{max-width:1120px' in h and h.count(':root{') == 2)  # главный :root + мобильный --pad
chk('S14 печать: полосы снова в потоке', '@media print' in h and 'position:static' in h)

# ------------------------------ браузер -------------------------------------
from playwright.sync_api import sync_playwright

STATE = """() => {
  const g = i => document.getElementById('p' + i);
  const cs = el => getComputedStyle(el);
  const wrap = document.getElementById('newspaper');
  return {
    jsflip: document.documentElement.classList.contains('js-flip'),
    cls: [1,2,3,4].map(i => g(i).className),
    vis: [1,2,3,4].map(i => cs(g(i)).visibility),
    op:  [1,2,3,4].map(i => cs(g(i)).opacity),
    tr:  [1,2,3,4].map(i => cs(g(i)).transform),
    z:   [1,2,3,4].map(i => cs(g(i)).zIndex),
    counter: document.getElementById('navCount').textContent,
    prevD: document.getElementById('navPrev').disabled,
    nextD: document.getElementById('navNext').disabled,
    wrapH: wrap.offsetHeight,
    heights: [1,2,3,4].map(i => g(i).offsetHeight),
    a01top: document.getElementById('a01').offsetTop,
    a12top: document.getElementById('a12').offsetTop,
    scrollW: document.documentElement.scrollWidth,
    innerW: window.innerWidth,
    shade: !!document.getElementById('flipshade'),
    shading: document.getElementById('flipshade') ?
      document.getElementById('flipshade').classList.contains('shading') : false,
  };
}"""

ANGLE = """(i) => {
  const cs = getComputedStyle(document.getElementById('p' + i));
  const t = cs.transform;
  if (!t || t === 'none') return {none: true, op: cs.opacity, vis: cs.visibility, z: cs.zIndex};
  const v = t.slice(t.indexOf('(') + 1, -1).split(',').map(Number);
  let ang = null;
  if (v.length === 16) ang = Math.atan2(-v[2], v[0]) * 180 / Math.PI;
  return {none: false, m3d: t.startsWith('matrix3d'), ang, op: cs.opacity,
          vis: cs.visibility, z: cs.zIndex};
}"""


def flip_ang(st, i):
    return st  # не используется; угол считаем через ANGLE


with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={'width': 1440, 'height': 900})
    errs = []
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL, wait_until='load')
    pg.wait_for_timeout(1800)

    s0 = pg.evaluate(STATE)
    chk('B1 режим стопки включён', s0['jsflip'] and s0['shade'])
    chk('B2 счётчик 1 / 4, назад неактивна', s0['counter'] == '1 / 4' and s0['prevD'] and not s0['nextD'])
    chk('B3 p1 видна, p2-p4 скрыты', s0['vis'] == ['visible', 'hidden', 'hidden', 'hidden'], s0['vis'])
    chk('B4 высота обёртки = p1', abs(s0['wrapH'] - s0['heights'][0]) <= 2, (s0['wrapH'], s0['heights'][0]))
    chk('B5 нет горизонт. переполнения', s0['scrollW'] <= s0['innerW'] + 1, (s0['scrollW'], s0['innerW']))
    H = s0['heights'][:]
    A01, A12 = s0['a01top'], s0['a12top']

    # --- hammer: 5 быстрых кликов подряд (диспатч в обход disabled) ---
    pg.evaluate("for(let i=0;i<5;i++)document.getElementById('navNext')"
                ".dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(1500)
    s1 = pg.evaluate(STATE)
    chk('H1 hammer: ровно один переворот, p2', s1['counter'] == '2 / 4'
        and 'is-on' in s1['cls'][1] and 'is-off' in s1['cls'][0], s1['counter'])
    chk('H2 hammer: состояние цело', s1['vis'] == ['hidden', 'visible', 'hidden', 'hidden']
        and abs(s1['wrapH'] - H[1]) <= 2 and not s1['prevD'] and not s1['nextD'])

    # --- mid-flip вперёд: физика поворота, не fade ---
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    pg.click('#navNext')
    pg.wait_for_timeout(380)
    mid = pg.evaluate(ANGLE, 1)
    st = pg.evaluate(STATE)
    chk('M1 лист в 3D-повороте (matrix3d)', mid.get('m3d') and not mid.get('none'), mid.get('ang'))
    chk('M2 угол в середине переворота', mid.get('ang') is not None and -88 < mid['ang'] < -8,
        round(mid.get('ang') or 0, 1))
    chk('M3 не fade: opacity=1, видимость есть', mid['op'] == '1' and mid['vis'] == 'visible')
    chk('M4 лист в воздухе z=4, тень идёт', mid['z'] == '4' and st['shading'])
    chk('M5 кнопки заблокированы, счётчик впереди', st['prevD'] and st['nextD'] and st['counter'] == '2 / 4')
    chk('M6 без горизонт. переполнения mid-flip', st['scrollW'] <= st['innerW'] + 1)
    chk('M7 целевая полоса раскрыта под листом', st['vis'][1] == 'visible' and st['tr'][1] == 'none')
    pg.screenshot(path=os.path.join(REND, 'v16_flip_mid.png'))

    # --- тайминг: отдельно, детерминированно ---
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    pg.click('#navNext')
    pg.wait_for_timeout(620)  # t≈620мс: переворот ещё идёт (800мс)
    s650 = pg.evaluate(STATE)
    chk('T1 на 620мс ещё переворачивается', s650['prevD'] and s650['nextD']
        and s650['counter'] == '2 / 4')
    pg.wait_for_timeout(430)  # t≈1050мс: transitionend (800мс) отработал
    s1000 = pg.evaluate(STATE)
    chk('T2 к 1000мс осела на p2', s1000['counter'] == '2 / 4' and not s1000['prevD']
        and not s1000['nextD'] and 'is-on' in s1000['cls'][1])
    p1off = pg.evaluate(ANGLE, 1)
    chk('T3 p1 ушла за вертикаль (backface)', p1off.get('ang') is not None and p1off['ang'] < -90
        and p1off['vis'] == 'hidden', round(p1off.get('ang') or 0, 1))
    chk('T4 p2 в покое: transform none', s1000['tr'][1] == 'none')
    chk('T5 геометрия не изменилась', s1000['heights'] == H and s1000['a01top'] == A01
        and s1000['a12top'] == A12 and abs(s1000['wrapH'] - H[1]) <= 2)

    # --- переворот назад ---
    pg.click('#navPrev')
    pg.wait_for_timeout(380)
    midb = pg.evaluate(ANGLE, 1)
    stb = pg.evaluate(STATE)
    chk('P1 назад: p1 возвращается из-за вертикали', midb.get('m3d') and -96 < midb['ang'] < -5
        and midb['vis'] == 'visible', round(midb.get('ang') or 0, 1))
    chk('P2 назад: счётчик сразу 1 / 4', stb['counter'] == '1 / 4')
    pg.wait_for_timeout(1000)
    sb = pg.evaluate(STATE)
    chk('P3 назад: p1 снова наверху', sb['vis'] == ['visible', 'hidden', 'hidden', 'hidden']
        and sb['tr'][0] == 'none' and sb['counter'] == '1 / 4' and sb['prevD'] and not sb['nextD']
        and abs(sb['wrapH'] - H[0]) <= 2)

    # --- до конца: p4 ---
    for _ in range(3):
        pg.click('#navNext')
        pg.wait_for_timeout(1250)
    s4 = pg.evaluate(STATE)
    chk('E1 дошли до p4: 4 / 4', s4['counter'] == '4 / 4' and s4['nextD'] and not s4['prevD']
        and 'is-on' in s4['cls'][3] and s4['vis'][3] == 'visible')
    pg.evaluate("document.getElementById('navNext').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(60)
    s4b = pg.evaluate(STATE)
    chk('E2 на p4 вперёд не ломается', s4b['counter'] == '4 / 4' and 'is-on' in s4b['cls'][3])

    # --- рендеры полос в покое ---
    os.makedirs(REND, exist_ok=True)
    pg.reload(wait_until='load')
    pg.wait_for_timeout(1800)
    for i in range(1, 5):
        if i > 1:
            pg.click('#navNext')
            pg.wait_for_timeout(1300)
        el = pg.query_selector(f'#p{i}')
        el.screenshot(path=os.path.join(REND, f'v16_p{i}.png'))
    chk('R1 рендеры полос сделаны', all(os.path.exists(os.path.join(REND, f'v16_p{i}.png'))
                                        for i in range(1, 5)))

    # --- узкие экраны: 1100 и 390 ---
    for w, tag in ((1100, 'W1'), (390, 'W2')):
        pg.set_viewport_size({'width': w, 'height': 900})
        pg.wait_for_timeout(500)
        sw = pg.evaluate(STATE)
        ok_rest = sw['scrollW'] <= sw['innerW'] + 1
        pg.click('#navPrev')
        pg.wait_for_timeout(400)
        sm = pg.evaluate(STATE)
        ok_mid = sm['scrollW'] <= sm['innerW'] + 1
        pg.wait_for_timeout(1000)
        chk(f'{tag} нет переполнения @{w}px (покой+mid)', ok_rest and ok_mid,
            (sw['scrollW'], sm['scrollW'], w))
    pg.set_viewport_size({'width': 390, 'height': 844})
    pg.wait_for_timeout(600)
    pg.evaluate("document.getElementById('navPrev').click()")
    pg.wait_for_timeout(1300)
    pg.evaluate("document.getElementById('navPrev').click()")
    pg.wait_for_timeout(1300)
    pg.evaluate("document.getElementById('navPrev').click()")
    pg.wait_for_timeout(1300)
    mob = pg.evaluate(STATE)
    chk('W3 мобильная: вернулись на p1', mob['counter'] == '1 / 4', mob['counter'])
    pg.query_selector('#p1').screenshot(path=os.path.join(REND, 'v16_mobile_p1.png'))

    # --- prefers-reduced-motion ---
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    pr = ctx.new_page()
    pr.goto(URL, wait_until='load')
    pr.wait_for_timeout(700)
    pr.click('#navNext')
    pr.wait_for_timeout(220)
    sr = pr.evaluate(STATE)
    an = pr.evaluate("getComputedStyle(document.getElementById('flipshade')).animationName")
    chk('RM reduced-motion: мгновенное переключение', sr['counter'] == '2 / 4'
        and 'is-on' in sr['cls'][1], sr['counter'])
    chk('RM reduced-motion: тень-градиент выключена', an == 'none', an)
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
        pos: [1,2,3,4].map(i => cs(g(i)).position),
        vis: [1,2,3,4].map(i => cs(g(i)).visibility),
        nav: cs(document.querySelector('.sheetnav')).display,
        wrapH: document.getElementById('newspaper').offsetHeight,
        sum: [1,2,3,4].reduce((a,i) => a + g(i).offsetHeight, 0),
      };
    }""")
    chk('PR печать: 4 полосы в потоке, все видимы', prn['pos'] == ['static'] * 4
        and prn['vis'] == ['visible'] * 4 and prn['wrapH'] >= prn['sum'] * 0.9,
        (prn['wrapH'], prn['sum']))
    chk('PR печать: навигация скрыта', prn['nav'] == 'none')
    ctx2.close()

    chk('C1 консоль чистая', not errs, errs[:3])
    br.close()

# ------------------------------ композит ------------------------------------
try:
    from PIL import Image
    ims = [Image.open(os.path.join(REND, f'v16_p{i}.png')).convert('RGB') for i in range(1, 5)]
    mid = Image.open(os.path.join(REND, 'v16_flip_mid.png')).convert('RGB')
    mob = Image.open(os.path.join(REND, 'v16_mobile_p1.png')).convert('RGB')
    W, GAP, BG = 1120, 12, (242, 237, 227)

    def fit(im, w):
        return im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS)

    mid_s = fit(mid, W)
    cells = [fit(im, (W - GAP) // 2) for im in ims]
    mob_s = fit(mob, (W - GAP) // 2)
    grid_h = max(cells[0].height, cells[1].height) + GAP + max(cells[2].height, cells[3].height)
    tail_h = mob_s.height
    canvas = Image.new('RGB', (W, mid_s.height + GAP + grid_h + GAP + tail_h + GAP * 2), BG)
    y = GAP
    canvas.paste(mid_s, (0, y)); y += mid_s.height + GAP
    canvas.paste(cells[0], (0, y)); canvas.paste(cells[1], ((W - GAP) // 2 + GAP, y))
    y += max(cells[0].height, cells[1].height) + GAP
    canvas.paste(cells[2], (0, y)); canvas.paste(cells[3], ((W - GAP) // 2 + GAP, y))
    y += max(cells[2].height, cells[3].height) + GAP
    canvas.paste(mob_s, (0, y))
    canvas.save(os.path.join(REND, 'preview-all.png'))
    chk('K1 композит preview-all.png', True, canvas.size)
except Exception as e:  # noqa: BLE001
    chk('K1 композит preview-all.png', False, e)

print()
print(f'ИТОГ: {len(OK)} PASS / {len(BAD)} FAIL')
if BAD:
    print('ПРОВАЛЕНО:', BAD)
    sys.exit(1)
print('ALL GREEN — day-flip готов к публикации')
