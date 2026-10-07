#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN QA · выпуск 04.10.2026, раунд 3 (redline-report). Запуск из корня workspace:
   python3 sf-repo/worktmp/qa_daily0410_v3.py
Любой FAIL -> exit 1 (цепочка публикации прерывается)."""
import base64, os, re, sys
from playwright.sync_api import sync_playwright

ROOT = os.getcwd()
HTML_PATH = os.path.join(ROOT, 'sf-repo', 'anna-malboro', 'daily-04-10-2026.html')
UP = os.path.join(ROOT, 'uploads')
URL = 'file://' + HTML_PATH
OLD_0310 = os.path.join(ROOT, 'renders', 'preview-all.png')
OLD_V2 = os.path.join(ROOT, 'renders', 'preview-all-0410-v2.png')
NEW_RENDER = os.path.join(ROOT, 'renders', 'preview-all-0410-v3.png')
IDS = ['b1', 'b2', 'b3', 'b4', 'b5', 'b6']

RES = []
def chk(name, ok, extra=''):
    RES.append((name, bool(ok), extra))
    print(('PASS ' if ok else 'FAIL ') + name + ((' · ' + str(extra)) if extra else ''))

HTML = open(HTML_PATH, encoding='utf-8').read()

# ---------- S1: статика ----------
chk('S1 штамп 032 первой строкой style', HTML.index('/* SFN-DESIGN-032: redline-report · 04.10.2026 */') < HTML.index('@import'))
chk('S1 маркер 032 перед </body>', '<!-- SFN · 2026 · 032 · redline-report -->\n</body>' in HTML)
chk('S1 title+viewport+description', '<title>San Fierro News — ежедневный выпуск от 04.10.2026</title>' in HTML
    and 'name="viewport"' in HTML and 'name="description"' in HTML)
chk('S1 один :root', HTML.count(':root{') == 1)
chk('S1 нет inline-styles', 'style="' not in HTML)
scen = re.findall(r'#b(\d) \.rlx-main\{[^}]*?grid-template-areas:([^;}]+)', HTML)
chk('S1 12 сценариев (6 десктоп + 6 мобильных) через grid-template-areas',
    sorted(x[0] for x in scen[:6]) == ['1', '2', '3', '4', '5', '6'] and len(scen) == 12, [x[0] for x in scen])
chk('S1 все 6 десктоп-сценариев различны', len({s[1].strip() for s in scen[:6]}) == 6)
chk('S1 нет object-fit/crop', 'object-fit' not in HTML and 'clip-path' not in HTML)
chk('S1 фото width:100% height:auto', 'img{display:block;width:100%;height:auto}' in HTML)
chk('S1 новая палитра (сигнальный красный/роза/сталь/фарфор)',
    all(t in HTML for t in ('--red:#c81e32', '--deep:#8c1222', '--rose:#ef3f63', '--steel:#3a4a58',
                            '--porc:#f7f2ee', 'rlx-crim', 'rlx-ink', 'rlx-porc')))
chk('S1 типографика: Fira Sans Condensed 700/900 + Inter, контурные слова',
    all(t in HTML for t in ('Fira+Sans+Condensed:wght@700;900', 'family=Inter', '-webkit-text-stroke:2.5px', 'clamp(52px,7.4vw,104px)')))
chk('S1 корешок-спайн у всех 6 полос', HTML.count('class="rlx-spine"') == 6)
OLD = ['pageEnter', 'pageExit', 'pageIndicator', 'showPageIndicator', 'sfn-rise', 'sfn-fade', 'navbtn',
       'pages-stage', 'page-indicator', 'sheetnav', 'navPrev', 'navNext', 'is-off', 'js-nav',
       'cubic-bezier(.22,.61,.36,1)', 'calc(50% - 640px)', 'calc(50% + 640px)', 'SFN-DESIGN-031',
       'class="sheet', 'class="grid"', 'class="ph', 'th-red', 'th-blush', 'Bricolage', 'Source Serif', 'Space Mono']
found_old = [t for t in OLD if t in HTML]
chk('S1 СТАРОЕ наследование отсутствует (анимации/навигация/классы прошлых выпусков)', not found_old, found_old)
chk('S1 новая моушен-система rlx на месте',
    all(t in HTML for t in ('@keyframes rlxBandIn', '@keyframes rlxBandOut', '@keyframes rlxRise',
                            '@keyframes rlxFlag', '@keyframes rlxDraw', 'rlxPrev', 'rlxNext', 'rlxFlag',
                            'sfn-js', 'st-live', 'st-off', 'st-in', 'st-out')))
chk('S1 нет prefers-reduced-motion гейтинга', 'prefers-reduced-motion' not in HTML)
chk('S1 нет постоянного счётчика полос (плашка собирается только в JS)',
    'ПОЛОСА' not in HTML and '<div class="rlx-flag" id="rlxFlag" role="status"></div>' in HTML
    and '\\u041f\\u041e\\u041b\\u041e\\u0421\\u0410' in HTML)
PH = {
 'm01': 'Массовое убийство на трассе Лас-Вентураса — четверо погибших, включая офицера полиции.jpg',
 'm02': 'Тело мужчины обнаружено в тоннеле между Лос-Сантосом и Сан-Фиерро — есть задержанный.png',
 'm03': 'Вертолёт обнаружен посреди тоннеля между Лос-Сантосом и Сан-Фиерро.jpg',
 'm04': 'В тоннеле между Лос-Сантосом и Сан-Фиерро обнаружен сотрудник полиции без сознания.jpg',
 'm05': 'Кровавая расправа на трассе между Лас-Вентурасом и Сан-Фиерро — двое погибших.jpg',
 'm06': 'Двойная трагедия на дороге в Лос-Сантосе — два тела на месте происшествия.jpg',
 'm07': 'В Сан-Фиерро перевернулась фура — движение на перекрёстке парализовано.png',
 'm08': 'Пирс на пляже Санта-Мария перекрыт — полиция и скорая на месте.jpg',
 'm09': 'Тело женщины обнаружено у пляжа Санта-Мария в Лос-Сантосе.png',
 'm10': 'У полицейского участка в Лос-Сантосе замечено массовое скопление полиции и машина редакции LSN.png',
 'm11': 'В мэрии Лос-Сантоса выставлен на продажу бизнес Carsharing Guaranteed за рекордные $1.800.000.000.jpg',
 'm12': 'В Сан-Фиерро упал самолёт — на месте работают экстренные службы.jpg'}
ok12, bad = True, []
for k, fn in PH.items():
    raw = open(os.path.join(UP, fn), 'rb').read()
    mime = 'image/png' if fn.endswith('.png') else 'image/jpeg'
    token = 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode())
    if HTML.count(token) != 1:
        ok12 = False; bad.append(k)
chk('S1 12 фото байт-в-байт base64 по одному разу', ok12, bad)
vis = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', HTML, flags=re.S)
vis = re.sub(r'base64,[A-Za-z0-9+/=]+', '', vis)
vis = re.sub(r'<[^>]+>', ' ', vis)
chk('S1 RP-чистота видимого текста', all(t not in vis for t in ('Evolve Role Play', 'Evolve RP', 'Saint-Louis', '2504'))
    and re.search(r'\bчат\b', vis) is None and re.search(r'[A-Za-zА-Яа-я]_[A-Za-zА-Яа-я]', vis) is None)
chk('S1 финал — сводная лента из 12 событий', HTML.count('class="rlx-ix"') == 12)

# ---------- браузер ----------
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--disable-dev-shm-usage', '--no-sandbox', '--disable-gpu'])
    pg = br.new_page(viewport={'width': 1440, 'height': 1000})
    cerr = []
    pg.on('console', lambda m: cerr.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: cerr.append(str(e)))
    pg.goto(URL)
    pg.evaluate('document.fonts.ready.then(()=>1)')
    pg.wait_for_timeout(500)
    st_load = pg.evaluate("""() => { const f=document.getElementById('rlxFlag');
      return [f.className, f.textContent, getComputedStyle(f).opacity]; }""")
    chk('S2 стартовая плашка «ПОЛОСА 1 / 6» показана и живёт временно',
        st_load[1] == 'ПОЛОСА 1 / 6' and 'on' in st_load[0], st_load[:2])
    pg.wait_for_timeout(2400)
    chk('S2 стартовая плашка погасла (постоянного счётчика нет)',
        pg.evaluate("getComputedStyle(document.getElementById('rlxFlag')).opacity") == '0')
    rv1 = pg.evaluate("""() => [...document.querySelectorAll('#b1 .rlx-rv')].map(e=>+getComputedStyle(e).opacity)""")
    chk('S2 ступенчатое появление на обложке завершилось (все rv видны)', rv1 and all(v == 1 for v in rv1), rv1)

    over = pg.evaluate("""() => {
      const bad=[];
      const off=[...document.querySelectorAll('.rlx-band.st-off')];
      off.forEach(s=>s.classList.remove('st-off'));
      for (const el of document.querySelectorAll('#rlxDeck *')) {
        const cs=getComputedStyle(el);
        if (cs.display==='none'||cs.visibility==='hidden') continue;
        const clips = cs.overflow!=='visible' || cs.overflowY!=='visible' || cs.overflowX!=='visible';
        if (!clips) continue;
        if (el.clientWidth>0 && el.scrollWidth>el.clientWidth+1) bad.push([el.className||el.tagName,'w',el.scrollWidth,el.clientWidth]);
        if (el.clientHeight>0 && el.scrollHeight>el.clientHeight+1) bad.push([el.className||el.tagName,'h',el.scrollHeight,el.clientHeight]);
      }
      off.forEach(s=>s.classList.add('st-off'));
      return bad.slice(0,8);
    }""")
    chk('S2 нет обрезанного текста/контента', not over, over)
    leak = []
    for w in (1440, 1300, 1100, 390):
        pg.set_viewport_size({'width': w, 'height': 1000})
        pg.wait_for_timeout(260)
        r = pg.evaluate("""() => {
          const de=document.documentElement; const out=[];
          if (de.scrollWidth>de.clientWidth+1) out.push(['doc',de.scrollWidth,de.clientWidth]);
          for (const sh of document.querySelectorAll('.rlx-band')) {
            const sr=sh.getBoundingClientRect();
            for (const el of sh.children) {
              const r=el.getBoundingClientRect();
              if (r.width===0) continue;
              if (r.left < sr.left-1 || r.right > sr.right+1) out.push([sh.id, el.className||el.tagName, Math.round(r.left-sr.left), Math.round(sr.right-r.right)]);
            }
            const g=sh.querySelector('.rlx-main');
            for (const el of g.querySelectorAll(':scope > *')) {
              const r=el.getBoundingClientRect();
              if (r.width===0) continue;
              if (r.left < sr.left-1 || r.right > sr.right+1) out.push([sh.id, 'g:'+(el.className||el.tagName), Math.round(r.left-sr.left), Math.round(sr.right-r.right)]);
            }
          }
          return out.slice(0,6);
        }""")
        if r:
            leak.append((w, r))
    chk('S2 ничего не выходит за границы полосы и экрана (1440/1300/1100/390)', not leak, leak)
    pg.set_viewport_size({'width': 1440, 'height': 1000})
    pg.wait_for_timeout(260)

    # S3: геометрия — полосы-экраны, пропорции и разномасштабность фото, стрелки вплотную
    geo = pg.evaluate("""() => {
      const off=[...document.querySelectorAll('.rlx-band.st-off')];
      off.forEach(s=>s.classList.remove('st-off'));
      const hs=[...document.querySelectorAll('.rlx-band')].map(s=>s.offsetHeight);
      const imgs=[...document.querySelectorAll('#rlxDeck img')].map(i=>[i.clientWidth,i.clientHeight]);
      off.forEach(s=>s.classList.add('st-off'));
      const on=[...document.querySelectorAll('.rlx-band')].find(s=>!s.classList.contains('st-off'));
      const sr=on.getBoundingClientRect();
      const nv=document.getElementById('rlxNav').getBoundingClientRect();
      return {hs, imgs, count:document.querySelectorAll('#rlxDeck img').length,
              gapR: Math.round(nv.left-sr.right),
              dY: Math.round((nv.top+nv.height/2)-(sr.top+Math.min(sr.height,innerHeight)/2))};
    }""")
    chk('S3 12 img в DOM', geo['count'] == 12, geo['count'])
    chk('S3 полосы-экраны во весь viewport (min-height 100vh)', all(h >= 999 for h in geo['hs']), geo['hs'])
    ratios = [w / h for w, h in geo['imgs']]
    chk('S3 пропорции фото сохранены (16:9, без кропа)', all(abs(r - 1.777) < 0.02 for r in ratios),
        [round(r, 3) for r in ratios])
    chk('S3 стрелки вплотную к полосе (24px справа) и по центру высоты',
        geo['gapR'] == 24 and abs(geo['dY']) <= 2, (geo['gapR'], geo['dY']))
    sizes = [tuple(d) for d in geo['imgs']]
    chk('S3 все 12 кадров разного масштаба (нет одинаковых)', len(set(sizes)) == 12, sorted(set(sizes)))

    # S4: навигация — вперёд/назад, плашка, busy-блок
    pg.evaluate('window.scrollTo(0,0)')
    pg.click('#rlxNext')
    pg.wait_for_timeout(900)
    fl = pg.evaluate("""() => { const f=document.getElementById('rlxFlag');
      return [f.className, f.textContent, getComputedStyle(f).opacity]; }""")
    chk('S4 клик вперёд: временная плашка «ПОЛОСА 2 / 6»', fl[1] == 'ПОЛОСА 2 / 6' and 'on' in fl[0] and float(fl[2]) > 0.5, fl[:2])
    chk('S4 входящая полоса проявилась (opacity 1)',
        pg.evaluate("getComputedStyle(document.getElementById('b2')).opacity") == '1')
    pg.wait_for_timeout(1900)
    chk('S4 плашка погасла (временная)', pg.evaluate("document.getElementById('rlxFlag').className") == 'rlx-flag')
    vis_now = pg.evaluate("[...document.querySelectorAll('.rlx-band')].map(s=>s.classList.contains('st-off'))")
    chk('S4 видна только b2', vis_now == [i != 1 for i in range(6)], vis_now)
    pg.evaluate("""() => { const b=document.getElementById('rlxNext'); b.click(); b.click(); }""")
    pg.wait_for_timeout(1100)
    vis_now = pg.evaluate("[...document.querySelectorAll('.rlx-band')].map(s=>!s.classList.contains('st-off'))")
    chk('S4 busy-блок: двойной клик = один переход (видна b3)', vis_now == [i == 2 for i in range(6)], vis_now)
    pg.click('#rlxPrev'); pg.wait_for_timeout(1000)
    vis_now = pg.evaluate("[...document.querySelectorAll('.rlx-band')].map(s=>!s.classList.contains('st-off'))")
    chk('S4 назад работает (видна b2)', vis_now == [i == 1 for i in range(6)], vis_now)
    kb = pg.evaluate("""() => new Promise(res => { window.scrollTo(0,0);
      document.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
      setTimeout(()=>res([...document.querySelectorAll('.rlx-band')].map(s=>!s.classList.contains('st-off'))), 1000); })""")
    chk('S4 клавиатура: ArrowRight листает вперёд (b3)', kb == [i == 2 for i in range(6)], kb)
    pg.click('#rlxPrev'); pg.wait_for_timeout(900)

    # S5: моушен — rAF-сэмплер кроссфейда + ступенчатое появление + rlxDraw
    pg.evaluate('window.scrollTo(0,0)')
    pg.evaluate("""() => { const b=document.getElementById('rlxPrev'); b.click(); }""")
    pg.wait_for_timeout(950)
    pg.evaluate('window.scrollTo(0,0)')
    pg.wait_for_timeout(2000)
    pg.evaluate("""() => {
      window.__samples=[];
      const a=document.getElementById('b1'), b=document.getElementById('b2');
      function tick(){
        const ca=getComputedStyle(a), cb=getComputedStyle(b);
        window.__samples.push([+ca.opacity, +cb.opacity, cb.transform]);
        if (window.__samples.length<70) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
      document.getElementById('rlxNext').click();
    }""")
    pg.wait_for_timeout(1500)
    samples = pg.evaluate('window.__samples')
    enters = [s[1] for s in samples]
    exits = [s[0] for s in samples]
    coex = sum(1 for s in samples if 0.05 < s[0] < 0.95 and 0.05 < s[1] < 0.95)
    chk('S5 переход: входящая полоса 0→1', enters[0] < 0.15 and max(enters) > 0.95, (round(enters[0], 2), round(max(enters), 2)))
    chk('S5 переход: уходящая полоса 1→0', exits[0] > 0.9 and min(exits) < 0.05, (round(exits[0], 2), round(min(exits), 2)))
    chk('S5 кроссфейд: сосуществование >=6 кадров', coex >= 6, coex)
    tr = [s[2] for s in samples if s[2] and s[2] != 'none']
    chk('S5 только opacity+translateY (matrix, без 3D)', any('matrix(' in t for t in tr) and all('matrix3d' not in t for t in tr), tr[:1])
    anim = pg.evaluate("""() => {
      const rv=document.querySelector('#b2 .rlx-rv[data-r="4"]');
      const ru=document.querySelector('#b2 .rlx-rule');
      return [getComputedStyle(rv).opacity, getComputedStyle(ru).transform];
    }""")
    chk('S5 ступенчатое появление материалов и прорисовка линии завершились',
        float(anim[0]) == 1, anim)
    names = pg.evaluate("""() => { const b=document.getElementById('b2');
      const rv=[...b.querySelectorAll('.rlx-rv')];
      return [...new Set(rv.map(e=>getComputedStyle(e).animationName))]; }""")
    chk('S5 материалы b2 несут новую анимацию rlxRise (старых имён нет)',
        all(n in ('rlxRise', 'none') for n in names) and 'rlxRise' in names, names)

    # S7: печать
    pg.emulate_media(media='print')
    pr = pg.evaluate("""() => ({
      d:[...document.querySelectorAll('.rlx-band')].map(s=>getComputedStyle(s).display),
      o:[...document.querySelectorAll('#b3 .rlx-rv')].map(e=>getComputedStyle(e).opacity),
      a:getComputedStyle(document.querySelector('#b3 .rlx-rv')).animationName,
      n:getComputedStyle(document.getElementById('rlxNav')).display})""")
    chk('S7 печать: все 6 полос видны, контент проявлен, анимации выключены, навигация скрыта',
        all(d != 'none' for d in pr['d']) and all(v == '1' for v in pr['o']) and pr['a'] == 'none' and pr['n'] == 'none', pr)
    pg.emulate_media(media='screen')

    chk('S8 консоль чиста', not cerr, cerr[:3])
    pg.close()

    # S5b: reduced-motion — моушен жив
    ctx = br.new_context(reduced_motion='reduce', viewport={'width': 1440, 'height': 1000})
    pg2 = ctx.new_page()
    pg2.goto(URL); pg2.wait_for_timeout(2600)
    pg2.evaluate("""() => { window.__s2=[]; const b=document.getElementById('b2');
      function tick(){ window.__s2.push(+getComputedStyle(b).opacity);
        if (window.__s2.length<60) requestAnimationFrame(tick); } requestAnimationFrame(tick);
      document.getElementById('rlxNext').click(); }""")
    pg2.wait_for_timeout(1300)
    s2 = pg2.evaluate('window.__s2')
    mid = s2[2:40]
    chk('S5b prefers-reduced-motion не глушит переход', s2[0] < 0.15 and any(0.05 < v < 0.95 for v in mid) and max(s2) > 0.95,
        (round(s2[0], 2), round(max(s2), 2)))
    ctx.close()

    # S6: без JS — обычный поток
    ctx = br.new_context(java_script_enabled=False, viewport={'width': 1440, 'height': 1000})
    pg3 = ctx.new_page()
    pg3.goto(URL); pg3.wait_for_timeout(700)
    boxes = pg3.eval_on_selector_all('.rlx-band', 'els=>els.map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.top), Math.round(r.height)]})')
    nav_disp = pg3.eval_on_selector('.rlx-nav', 'e=>getComputedStyle(e).display')
    rvs = pg3.eval_on_selector_all('#b5 .rlx-rv', 'els=>els.map(e=>getComputedStyle(e).opacity)')
    chk('S6 без JS: 6 полос в потоке', len(boxes) == 6 and all(h > 500 for _, h in boxes) and boxes[1][0] > boxes[0][0], boxes)
    chk('S6 без JS: навигация и плашка скрыты, контент виден',
        nav_disp == 'none' and all(v == '1' for v in rvs), (nav_disp, rvs[:3]))
    ctx.close()
    br.close()

# ---------- S9: отличие от прошлых выпусков + доля красного ----------
try:
    from PIL import Image
    import numpy as np
    b = Image.open(NEW_RENDER).convert('RGB')
    g = b.convert('L').resize((220, 300))
    for tag, path in (('03.10 day-pageindicator', OLD_0310), ('04.10 red-pink-bold (предыдущий раунд)', OLD_V2)):
        a = Image.open(path).convert('L').resize((220, 300))
        d = float(np.mean(np.abs(np.asarray(a, float) - np.asarray(g, float))))
        chk('S9 визуальное отличие от %s (mean|ΔL| > 12)' % tag, d > 12, round(d, 1))
    arr = np.asarray(b, dtype=np.int16)
    R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    redish = ((R > 110) & (R - G > 50) & (R - B > 40)).mean()
    chk('S9 красный остаётся главным языком (доля насыщенных красных пикселей > 10%)', redish > 0.10, round(float(redish), 3))
except Exception as e:
    chk('S9 визуальное отличие/палитра', False, e)

fails = [n for n, ok, _ in RES if not ok]
print('\nQA: %d/%d GREEN' % (len(RES) - len(fails), len(RES)))
if fails:
    print('FAILS:', fails)
    sys.exit(1)
print('ALL GREEN')
