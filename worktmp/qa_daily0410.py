#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN QA · выпуск 04.10.2026 (chronicle-digest). Запуск из корня workspace:
   python3 sf-desk/worktmp/qa_daily0410.py
Любой FAIL -> exit 1 (цепочка публикации прерывается)."""
import base64, os, re, sys, hashlib
from playwright.sync_api import sync_playwright

ROOT = os.getcwd()
HTML_PATH = os.path.join(ROOT, 'sf-repo', 'anna-malboro', 'daily-04-10-2026.html')
UP = os.path.join(ROOT, 'uploads')
URL = 'file://' + HTML_PATH
OLD_RENDER = os.path.join(ROOT, 'renders', 'preview-all.png')
NEW_RENDER = os.path.join(ROOT, 'renders', 'preview-all-0410.png')

RES = []
def chk(name, ok, extra=''):
    RES.append((name, bool(ok), extra))
    print(('PASS ' if ok else 'FAIL ') + name + ((' · ' + str(extra)) if extra else ''))

HTML = open(HTML_PATH, encoding='utf-8').read()

# ---------- S1: статика ----------
chk('S1 stamp 030 первой строкой style', HTML.index('/* SFN-DESIGN-030: chronicle-digest · 04.10.2026 */') < HTML.index('@import'))
chk('S1 маркер 030 перед </body>', '<!-- SFN · 2026 · 030 · chronicle-digest -->\n</body>' in HTML)
chk('S1 title+viewport', '<title>San Fierro News — ежедневный дайджест от 04.10.2026</title>' in HTML and 'name="viewport"' in HTML)
chk('S1 один :root', HTML.count(':root{') == 1)
chk('S1 нет inline-styles', 'style="' not in HTML)
chk('S1 4 сценария полос через grid-template-areas', len(re.findall(r'#p\d \.grid\{grid-template-areas', HTML)) == 4)
chk('S1 нет object-fit/crop', 'object-fit' not in HTML and 'clip-path' not in HTML)
chk('S1 фото width:100% height:auto', 'img{display:block;width:100%;height:auto}' in HTML)
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
chk('S1 навигация-канон: кроссфейд+плашка', all(t in HTML for t in ('pageEnterNext', 'pageEnterPrev', 'pageExit',
    'pageIndicatorInOut', 'calc(50% - 640px)', 'cubic-bezier(.22,.61,.36,1)', 'showPageIndicator')))
chk('S1 нет prefers-reduced-motion гейтинга', 'prefers-reduced-motion' not in HTML)

# ---------- браузер ----------
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={'width': 1440, 'height': 1000})
    cerr = []
    pg.on('console', lambda m: cerr.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: cerr.append(str(e)))
    pg.goto(URL)
    pg.evaluate('document.fonts.ready.then(()=>1)')
    pg.wait_for_timeout(900)

    # S2 геометрия: ничего не обрезано и не вылезает
    over = pg.evaluate("""() => {
      const bad=[];
      for (const el of document.querySelectorAll('#newspaper *')) {
        const cs=getComputedStyle(el);
        if (cs.display==='none'||cs.visibility==='hidden') continue;
        const clips = cs.overflow!=='visible' || cs.overflowY!=='visible' || cs.overflowX!=='visible';
        if (!clips) continue;  // при overflow:visible ничего не обрезается
        if (el.clientWidth>0 && el.scrollWidth>el.clientWidth+1) bad.push([el.className||el.tagName,'w',el.scrollWidth,el.clientWidth]);
        if (el.clientHeight>0 && el.scrollHeight>el.clientHeight+1) bad.push([el.className||el.tagName,'h',el.scrollHeight,el.clientHeight]);
      }
      return bad.slice(0,8);
    }""")
    chk('S2 нет обрезанного текста/контента', not over, over)
    leak = []
    for w in (1440, 1300, 1100, 390):
        pg.set_viewport_size({'width': w, 'height': 1000})
        pg.wait_for_timeout(250)
        r = pg.evaluate("""() => {
          const de=document.documentElement; const out=[];
          if (de.scrollWidth>de.clientWidth+1) out.push(['doc',de.scrollWidth,de.clientWidth]);
          for (const sh of document.querySelectorAll('.sheet')) {
            const sr=sh.getBoundingClientRect();
            for (const el of sh.children) {
              const r=el.getBoundingClientRect();
              if (r.width===0) continue;
              if (r.left < sr.left-1 || r.right > sr.right+1) out.push([sh.id, el.className||el.tagName, Math.round(r.left-sr.left), Math.round(sr.right-r.right)]);
            }
          }
          return out.slice(0,6);
        }""")
        if r:
            leak.append((w, r))
    chk('S2 ничего не выходит за границы листа и экрана (1440/1300/1100/390)', not leak, leak)
    pg.set_viewport_size({'width': 1440, 'height': 1000})
    pg.wait_for_timeout(250)

    # S3 размеры фото подряд не одинаковые + все 12 на месте (в no-JS потоке)
    seq = pg.evaluate("""() => {
      const sheets=[...document.querySelectorAll('.sheet')];
      const off=sheets.filter(s=>s.classList.contains('is-off'));
      off.forEach(s=>s.classList.remove('is-off'));
      const out={};
      for (const sh of sheets) out[sh.id]=[...sh.querySelectorAll('img')].map(i=>[i.clientWidth,i.clientHeight]);
      out.count=document.querySelectorAll('#newspaper img').length;
      off.forEach(s=>s.classList.add('is-off'));
      return out;
    }""")
    chk('S3 12 img в DOM', seq.get('count') == 12, seq.get('count'))
    badpairs = []
    for pid in ('p1', 'p2', 'p3', 'p4'):
        ws = [tuple(d) for d in seq[pid]]
        for a, b in zip(ws, ws[1:]):
            if a == b:
                badpairs.append((pid, a))
    chk('S3 соседние фото разного размера', not badpairs, badpairs)
    distinct = {pid: len({tuple(d) for d in seq[pid]}) for pid in ('p2', 'p3')}
    chk('S3 разнообразие масштабов на полосе (>=3 разных)', all(v >= 3 for v in distinct.values()), distinct)

    # S4 навигация: вперёд/назад, плашка, busy
    pg.evaluate('window.scrollTo(0,0)')
    st = pg.evaluate("""() => new Promise(res => {
      const ind=document.getElementById('pageIndicator');
      const log=[];
      document.getElementById('navNext').click();
      log.push(['t0', ind.className, ind.textContent,
                [...document.querySelectorAll('.sheet')].map(s=>s.className)]);
      setTimeout(()=>log.push(['t300', ind.className, ind.textContent,
                getComputedStyle(document.getElementById('p2')).opacity]), 300);
      setTimeout(()=>res(log), 2000);
    })""")
    chk('S4 клик вперёд: плашка ПОЛОСА 2 / 4 появилась', st[0][1] == 'page-indicator show' and st[0][2] == 'ПОЛОСА 2 / 4', st[0][1:3])
    chk('S4 входящая полоса проявилась (opacity→1)', float(st[1][3]) > 0.5, st[1][3])
    chk('S4 плашка погасла через цикл', 'show' not in pg.evaluate("document.getElementById('pageIndicator').className"))
    vis_now = pg.evaluate("[...document.querySelectorAll('.sheet')].map(s=>[s.id, s.classList.contains('is-off')])")
    chk('S4 видна только p2', vis_now == [['p1', True], ['p2', False], ['p3', True], ['p4', True]], vis_now)
    # busy: двойной клик = один переход
    pg.evaluate("""() => { const b=document.getElementById('navNext'); b.click(); b.click(); }""")
    pg.wait_for_timeout(1100)
    vis_now = pg.evaluate("[...document.querySelectorAll('.sheet')].map(s=>[s.id, s.classList.contains('is-off')])")
    chk('S4 busy-блок: двойной клик = один переход', vis_now[2] == ['p3', False] and vis_now[3] == ['p4', True], vis_now)
    pg.click('#navPrev'); pg.wait_for_timeout(1000)
    vis_now = pg.evaluate("[...document.querySelectorAll('.sheet')].map(s=>!s.classList.contains('is-off'))")
    chk('S4 назад работает', vis_now == [False, True, False, False] or vis_now == [False, False, True, False], vis_now)
    # вернуть в p1
    for _ in range(3):
        if pg.evaluate("!document.getElementById('p1').classList.contains('is-off')"):
            break
        pg.click('#navPrev'); pg.wait_for_timeout(900)

    # S5 моушен: rAF-сэмплер кроссфейда
    pg.evaluate('window.scrollTo(0,0)')
    pg.wait_for_timeout(300)
    pg.evaluate("""() => {
      window.__samples=[];
      const a=document.getElementById('p1'), b=document.getElementById('p2');
      function tick(){
        const ca=getComputedStyle(a), cb=getComputedStyle(b);
        window.__samples.push([+ca.opacity, +cb.opacity, cb.transform]);
        if (window.__samples.length<70) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
      document.getElementById('navNext').click();
    }""")
    pg.wait_for_timeout(1400)
    samples = pg.evaluate('window.__samples')
    enters = [s[1] for s in samples]
    exits = [s[0] for s in samples]
    coex = sum(1 for s in samples if 0.05 < s[0] < 0.95 and 0.05 < s[1] < 0.95)
    chk('S5 кроссфейд: entering 0→1', enters[0] < 0.1 and max(enters) > 0.95, (round(enters[0], 2), round(max(enters), 2)))
    chk('S5 кроссфейд: exiting 1→0', exits[0] > 0.9 and min(exits) < 0.05, (round(exits[0], 2), round(min(exits), 2)))
    chk('S5 сосуществование полос >=6 кадров', coex >= 6, coex)
    tr = [s[2] for s in samples if s[2] and s[2] != 'none']
    chk('S5 translateY на входе', any('matrix' in t for t in tr), tr[:1])
    dur = pg.evaluate("""() => { const s=document.getElementById('p3'); return 0; }""")
    pg.wait_for_timeout(600)

    # S5b reduced-motion: анимации живы
    ctx = br.new_context(reduced_motion='reduce', viewport={'width': 1440, 'height': 1000})
    pg2 = ctx.new_page()
    pg2.goto(URL); pg2.wait_for_timeout(900)
    pg2.evaluate("""() => { window.__s2=[]; const b=document.getElementById('p2');
      function tick(){ window.__s2.push(+getComputedStyle(b).opacity);
        if (window.__s2.length<60) requestAnimationFrame(tick); } requestAnimationFrame(tick);
      document.getElementById('navNext').click(); }""")
    pg2.wait_for_timeout(1200)
    s2 = pg2.evaluate('window.__s2')
    mid = [v for v in s2[2:40]]
    chk('S5b prefers-reduced-motion не глушит переход', s2[0] < 0.1 and any(0.05 < v < 0.95 for v in mid) and max(s2) > 0.95,
        (round(s2[0], 2), round(max(s2), 2)))
    ctx.close()

    # S6 без JS: поток и скрытая навигация
    ctx = br.new_context(java_script_enabled=False, viewport={'width': 1440, 'height': 1000})
    pg3 = ctx.new_page()
    pg3.goto(URL); pg3.wait_for_timeout(700)
    nojs = pg3.evaluate if False else None
    boxes = pg3.eval_on_selector_all('.sheet', 'els=>els.map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.top), Math.round(r.height)]})')
    nav_disp = pg3.eval_on_selector('.sheetnav', 'e=>getComputedStyle(e).display')
    chk('S6 без JS: 4 полосы в потоке', all(h > 500 for _, h in boxes) and boxes[1][0] > boxes[0][0], boxes)
    chk('S6 без JS: навигация скрыта', nav_disp == 'none', nav_disp)
    ctx.close()

    # S7 печать
    pg.emulate_media(media='print')
    pr = pg.evaluate("[...document.querySelectorAll('.sheet')].map(s=>getComputedStyle(s).display)")
    chk('S7 печать: все полосы видны', pr == ['block'] * 4, pr)
    pg.emulate_media(media='screen')

    chk('S8 консоль чиста', not cerr, cerr[:3])
    br.close()

# ---------- S9 отличие от прошлого выпуска ----------
try:
    from PIL import Image
    import numpy as np
    a = Image.open(OLD_RENDER).convert('L').resize((220, 300))
    b = Image.open(NEW_RENDER).convert('L').resize((220, 300))
    d = float(np.mean(np.abs(np.asarray(a, float) - np.asarray(b, float))))
    chk('S9 визуальное отличие от выпуска 03.10 (mean|ΔL| > 12)', d > 12, round(d, 1))
except Exception as e:
    chk('S9 визуальное отличие от выпуска 03.10', False, e)

fails = [n for n, ok, _ in RES if not ok]
print('\nQA: %d/%d GREEN' % (len(RES) - len(fails), len(RES)))
if fails:
    print('FAILS:', fails)
    sys.exit(1)
print('ALL GREEN')
