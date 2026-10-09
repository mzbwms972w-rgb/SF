#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN · QA ежедневного выпуска 09.10.2026, раунд 5 (SFN-DESIGN-034: full-plate).

Запуск:  python3 qa_daily0410_v5.py <путь-к-html> [путь-к-папке-с-12-оригиналами]
Проверяет бриф главреда от 10.10.2026 («убрать случайные пустоты, кадры — полноценные
участники композиции, каждая полоса — своя сцена, ничего не обрезано и не растянуто»)
плюс инварианты редакции (RP-чистота, байт-в-байт кадры, система rlx, вечные URL).
Выход: 0 = ALL GREEN.
"""
import base64, os, re, sys
from playwright.sync_api import sync_playwright

HTML = sys.argv[1]
UP = sys.argv[2] if len(sys.argv) > 2 else None
S = open(HTML, encoding='utf-8', errors='replace').read()
OK, FAIL = [], []
def chk(name, cond, extra=''):
    (OK if cond else FAIL).append(name + ((' — ' + extra) if extra and not cond else ''))

# ---------- 1. штампы, маркеры, мета ----------
chk('штамп 034 первой строкой CSS', S.lstrip().startswith('<!DOCTYPE html>') and
    '/* SFN-DESIGN-034: full-plate · 09.10.2026 */' in S[:S.index('</style>')])
chk('маркер 034 перед </body>', '<!-- SFN · 2026 · 034 · full-plate -->' in S[-400:])
chk('нет старых штампов 031/032/033', not re.search(r'SFN-DESIGN-03[123]', S))
chk('title есть', '<title>' in S[:4000])
chk('viewport есть', 'name="viewport"' in S[:4000])
chk('meta description есть', 'name="description"' in S[:4000])

# ---------- 2. RP-чистота видимого текста ----------
vis = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', S, flags=re.S)
vis = re.sub(r'base64,[A-Za-z0-9+/=]+', '', vis)
vis = re.sub(r'<[^>]+>', ' ', vis)
for nm, rx in [('Evolve Role Play', r'Evolve\s+Role\s+Play'), ('Evolve RP', r'Evolve\s+RP'),
               ('Saint-Louis', r'Saint[- ]Louis'), ('слово «чат»', r'\bчат[а-я]*\b'),
               ('underscore в имени', r'[A-Z][a-z]+_[A-Z][a-z]+')]:
    chk('RP-чистота: нет «%s»' % nm, not re.search(rx, vis, re.I))
# оговорки о незнании (бриф главреда от 10.10.2026: не напоминать читателю о нехватке сведений)
HEDGE = r'неизвестно|не уточняется|не раскрываются|не поступало|не сообщаются|не приводит|устанавливаются|редакция не сообщает|подробностей нет|данных нет'
chk('нет оговорок о незнании в видимом тексте', not re.search(HEDGE, vis, re.I),
    re.search(HEDGE, vis, re.I).group(0) if re.search(HEDGE, vis, re.I) else '')
# репортаж «Самолёт рухнул в Сан-Фиерро» (бриф главреда от 10.10.2026: 2-3 абзаца, без повторов заголовка)
m12 = re.search(r'<h3 class="rlx-h3">Самолёт рухнул в Сан-Фиерро</h3>(.*?)</div>', S, re.S)
if m12:
    paras = re.findall(r'<p class="rlx-tx">(.*?)</p>', m12.group(1), re.S)
    txt = ' '.join(re.sub(r'<[^>]+>', '', p) for p in paras)
    chk('репортаж m12: 2-3 абзаца текста', 2 <= len(paras) <= 3, str(len(paras)))
    chk('репортаж m12: объём >= 300 знаков', len(txt) >= 300, str(len(txt)))
    chk('репортаж m12: не повторяет заголовок и подзаголовок',
        'Самолёт рухнул в Сан-Фиерро' not in txt and 'На месте работают экстренные службы' not in txt)
else:
    chk('репортаж m12: материал найден', False)
# репортаж «Санта-Мария: берег закрыт» (бриф главреда от 10.10.2026: 2-3 абзаца, без повтора заголовка)
m08 = re.search(r'<h3 class="rlx-h3">Санта-Мария: берег закрыт</h3>(.*?)</div>', S, re.S)
if m08:
    paras = re.findall(r'<p class="rlx-tx">(.*?)</p>', m08.group(1), re.S)
    txt = ' '.join(re.sub(r'<[^>]+>', '', p) for p in paras)
    chk('репортаж m08: 3-4 абзаца текста', 3 <= len(paras) <= 4, str(len(paras)))
    chk('репортаж m08: объём >= 400 знаков', len(txt) >= 400, str(len(txt)))
    chk('репортаж m08: не повторяет заголовок и подзаголовок',
        'Санта-Мария: берег закрыт' not in txt and 'Доступ на пирс перекрыт' not in txt)
    chk('репортаж m08: раскрыты пункты брифа (службы, маски, переговоры, самолёт, отказ)',
        all(k in txt for k in ['медицинской службы', 'в масках', 'переговоры', 'самолёт', 'отказались'])
        and 'у самой воды' in txt)
    chk('репортаж m08: нет домыслов о маскированных и связи самолёта',
        not re.search(r'маскированны[ех]|банда|ОПГ|причин[аы] крушения|связан с происшествием', txt, re.I))
    chk('репортаж m08: одно тело, без множественного числа',
        ('тело одного человека' in txt or 'тело человека' in txt)
        and not re.search(r'тел людей|тела людей|несколько тел|двоих тел', txt),
        txt[:80])
else:
    chk('репортаж m08: материал найден', False)

# ---------- 3. кадры: байт-в-байт, по одному разу, без кропа и растяжения ----------
blobs = re.findall(r'data:image/(jpeg|png);base64,([A-Za-z0-9+/=]+)', S)
chk('12 вшитых кадров', len(blobs) == 12, str(len(blobs)))
chk('все 12 кадров уникальны', len({b[1] for b in blobs}) == 12)
if UP:
    ph = dict(re.findall(r"'(m\d\d)':\s*\(\s*'([^']+)'", open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_daily_0410_v5.py'),
        encoding='utf-8').read()))
    good = True
    for k, fn in ph.items():
        raw = open(os.path.join(UP, fn), 'rb').read()
        tok = 'data:%s;base64,%s' % ('image/jpeg' if fn.endswith('.jpg') else 'image/png',
                                     base64.b64encode(raw).decode())
        if S.count(tok) != 1:
            good = False
    chk('каждый оригинал входит байт-в-байт ровно один раз', good)
chk('нет object-fit (кроп запрещён)', 'object-fit' not in S)
chk('нет урезающих классов ширины 033', not re.search(r'rlx-w7[268]', S))

# ---------- 4. система rlx на месте ----------
for nm in ['rlxBandIn', 'rlxBandOut', 'rlxRise', 'rlxFlag', 'rlxDraw',
           'st-off', 'st-in', 'st-out', 'st-live', 'rlx-nav', 'rlx-flag', 'rlx-spine']:
    chk('система rlx: %s' % nm, nm in S)
chk('6 полос', len(re.findall(r'class="rlx-band', S)) == 6)
chk('нет наследия старых навигаций', not re.search(
    r'pageEnter|pageExit|pageIndicator|sfn-rise|sfn-fade|navbtn|pages-stage', S))

# ---------- 5. композиция: каждая полоса — свой сценарий ----------
rows = re.findall(r'class="rlx-row (r-[\d-]+|r-1|r-cover-foot)"', S)
chk('ряды с разными пропорциями', len(set(rows)) >= 5, str(sorted(set(rows))))

# ---------- 6. геометрия и пустоты (playwright) ----------
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--disable-dev-shm-usage', '--no-sandbox'])
    errs = []
    for W in (1440, 1300, 1100, 760, 390):
        pg = br.new_page(viewport={'width': W, 'height': 1000})
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + os.path.abspath(HTML))
        pg.evaluate('document.fonts.ready.then(()=>1)')
        pg.wait_for_timeout(2600)
        ov = pg.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
        chk('нет горизонтального переполнения @%d' % W, ov <= 0, 'overflow=%d' % ov)
        if W == 1440:
            # кроссфейд и плашка — с чистого состояния (полоса 1)
            pg.click('#rlxNext'); pg.wait_for_timeout(300)
            st = pg.evaluate("document.getElementById('b2').className")
            chk('кроссфейд: входящая полоса в st-in', 'st-in' in st, st)
            pg.wait_for_timeout(900)
            flag = pg.evaluate("document.getElementById('rlxFlag').textContent")
            chk('плашка «ПОЛОСА 2 / 6»', '2 / 6' in flag, flag)
            # пустоты: низ контента упирается в нижнее поле полосы
            for n in range(1, 7):
                sid = 'b%d' % n
                for _ in range(8):
                    if pg.evaluate("!document.getElementById('%s').classList.contains('st-off')" % sid):
                        break
                    pg.click('#rlxNext'); pg.wait_for_timeout(700)
                pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(2300)
                d = pg.evaluate("""(sid)=>{const b=document.getElementById(sid);
                  const m=b.querySelector('.rlx-main').getBoundingClientRect();
                  let mb=0; b.querySelectorAll('.rlx-main *').forEach(e=>{
                    const r=e.getBoundingClientRect(); if(r.height>0) mb=Math.max(mb,r.bottom);});
                  const rows=[...b.querySelectorAll(':scope > .rlx-main > .rlx-row')].map(r=>{
                    const k=[...r.children].map(c=>c.getBoundingClientRect().bottom);
                    return k.length>1?Math.round(Math.abs(k[0]-k[1])):0;});
                  return {void:Math.round(m.bottom-mb), rows:rows, h:Math.round(m.height)};}""", sid)
                pad = 46 if n != 6 else 40
                chk('полоса %d: нет дыры снизу (только поле)' % n, d['void'] <= pad + 6,
                    'void=%d' % d['void'])
                chk('полоса %d: низы колонок каждого ряда совпадают' % n,
                    all(x == 0 for x in d['rows']), str(d['rows']))
        pg.close()
    # без JS: все шесть полос в потоке — здесь измеряем геометрию кадров
    pg = br.new_page(viewport={'width': 1440, 'height': 1000}, java_script_enabled=False)
    pg.goto('file://' + os.path.abspath(HTML))
    pg.wait_for_timeout(1500)
    nb = pg.locator('.rlx-band').count()
    vis_b = pg.locator('.rlx-band:visible').count()
    chk('без JS шесть полос в потоке', nb == 6 and vis_b == 6, '%d/%d' % (vis_b, nb))
    ar = pg.evaluate("""()=>[...document.querySelectorAll('.rlx-fig img')].map(i=>{
        const r=i.getBoundingClientRect();
        return Math.abs((r.width/r.height)-(i.naturalWidth/i.naturalHeight))<0.02;})""")
    chk('пропорции всех 12 кадров сохранены', all(ar) and len(ar) == 12, str(ar))
    ws = pg.evaluate("""()=>{const m=document.querySelector('#b2 .rlx-main');
        const cs=getComputedStyle(m);
        const w=m.getBoundingClientRect().width-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
        return [...document.querySelectorAll('.rlx-fig img')].map(
        i=>i.getBoundingClientRect().width/w);}""")
    chk('полнополосный кадр обложки (>=95% поля)', max(ws) >= 0.95, '%.2f' % max(ws))
    chk('крупные кадры присутствуют (>=3 шире 55% поля)', len([x for x in ws if x > 0.55]) >= 3,
        'ширин: %s' % ','.join('%.2f' % x for x in ws))
    chk('средние кадры-партнёры (>=4 в диапазоне 45-56%)',
        len([x for x in ws if 0.45 <= x <= 0.56]) >= 4,
        'ширин: %s' % ','.join('%.2f' % x for x in ws))
    chk('нет кадров-маргиналов (все >=48% поля)', min(ws) >= 0.48, '%.2f' % min(ws))
    pg.close()
    chk('консоль чиста', not errs, '; '.join(errs[:2]))
    br.close()

print('SFN QA 034 full-plate: %d/%d ALL GREEN' % (len(OK), len(OK) + len(FAIL)) if not FAIL
      else 'SFN QA 034: ПРОВАЛЕНО %d из %d' % (len(FAIL), len(OK) + len(FAIL)))
for f in FAIL:
    print('  FAIL:', f)
sys.exit(1 if FAIL else 0)
