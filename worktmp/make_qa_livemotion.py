#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN: трансформер qa_navglide.py -> qa_livemotion.py (day-livemotion, 04.10.2026).

Отличия QA нового раунда:
— штамп/маркер day-livemotion;
— контроль покоя — синхронный рендер day-navglide (88b5c86);
— новые статики S18–S20 (RM удалён, ховер всегда, печать статична);
— RM-блок перевёрнут в LM-блок: prefers-reduced-motion:reduce теперь ОБЯЗАН
  проигрывать и загрузочный day-motion, и кроссфейд, и плавную прокрутку;
— рендеры v18_* -> v19_*.
Запуск: python3 worktmp/make_qa_livemotion.py
"""
import os
import py_compile

ROOT = os.getcwd()
SRC = os.path.join(ROOT, 'worktmp', 'qa_navglide.py')
DST = os.path.join(ROOT, 'worktmp', 'qa_livemotion.py')

src = open(SRC, encoding='utf-8').read()

REPL = []

# --- докстринг ---------------------------------------------------------------
REPL.append((
    '"""SFN QA day-navglide: стрелки вплотную к газете + живой кроссфейд полос (03.10.2026).',
    '"""SFN QA day-livemotion: моушен всегда жив, RM-гейтинг удалён (04.10.2026).',
    1))
REPL.append((
    'Проверяет: статику HTML (штамп day-navglide, keyframes pageEnterNext/pageEnterPrev/',
    'Проверяет: статику HTML (штамп day-livemotion, keyframes pageEnterNext/pageEnterPrev/',
    1))
REPL.append((
    '''— hammer, края, геометрия идентична потоковой версии без JS, ширины 1300/1100/390,
  prefers-reduced-motion, печать, консоль;
— покадровую идентичность полос в покое синхронному контролю day-navfade (0cdfa1a).
В конце — рендеры v18_* и композит preview-all.png.''',
    '''— hammer, края, геометрия идентична потоковой версии без JS, ширины 1300/1100/390,
  печать, консоль;
— LM-блок: prefers-reduced-motion:reduce больше НЕ глушит анимации — загрузочный
  day-motion, кроссфейд и прокрутка проигрываются и при системном «уменьшить движение»;
— статику S18–S20: RM-код удалён целиком, ховер фото без RM-условия, печать статична;
— покадровую идентичность полос в покое синхронному контролю day-navglide (88b5c86).
В конце — рендеры v19_* и композит preview-all.png.''',
    1))

# --- штамп/маркер ------------------------------------------------------------
REPL.append((
    "chk('S1 штамп day-navglide', '/* SFN-DESIGN-029: day-navglide · 03.10.2026 */' in h)",
    "chk('S1 штамп day-livemotion', '/* SFN-DESIGN-029: day-livemotion · 03.10.2026 */' in h)",
    1))
REPL.append((
    "chk('S2 маркер day-navglide', '<!-- SFN · 2026 · 029 · day-navglide -->' in h)",
    "chk('S2 маркер day-livemotion', '<!-- SFN · 2026 · 029 · day-livemotion -->' in h)",
    1))

# --- новые статики S18–S20 (вставляются перед браузерным блоком) -------------
REPL.append((
    '''
# ------------------------------ браузер -------------------------------------''',
    '''chk('S18 RM-гейтинг удалён полностью: анимации живут всегда',
    'prefers-reduced-motion' not in h and 'mqRM' not in h and 'matchMedia' not in h)
chk('S19 ховер фото — на любом hover-устройстве, без RM-условия',
    '@media (hover:hover){.ph:hover img{transform:scale(1.02)}}' in h)
chk('S20 печать по-прежнему статична',
    '@media print{*{animation:none!important;transition:none!important}}' in h)

# ------------------------------ браузер -------------------------------------''',
    1))

# --- контроль покоя: day-navglide (88b5c86) ----------------------------------
REPL.append((
    '# контрольная версия (day-navfade) для проверки идентичности покоя — из истории git',
    '# контрольная версия (day-navglide) для проверки идентичности покоя — из истории git',
    1))
REPL.append(("OLD_SHA = '0cdfa1a'", "OLD_SHA = '88b5c86'", 1))
REPL.append((
    "OLD_HTML = os.path.join(SCRATCH, 'old_day_navfade.html')",
    "OLD_HTML = os.path.join(SCRATCH, 'old_day_navglide.html')",
    1))
REPL.append((
    "print('WARN: контрольная версия day-navfade недоступна:', e)",
    "print('WARN: контрольная версия day-navglide недоступна:', e)",
    1))
REPL.append((
    '    # --- синхронный контроль прошлой версии (day-navfade): рендеры покоя ---',
    '    # --- синхронный контроль прошлой версии (day-navglide): рендеры покоя ---',
    1))
REPL.append((
    "chk('I1 полосы в покое идентичны day-navfade (синхр. контроль)', not bad_i, bad_i)",
    "chk('I1 полосы в покое идентичны day-navglide (синхр. контроль)', not bad_i, bad_i)",
    1))
REPL.append((
    "chk('I2 мобильная p1 идентична day-navfade (синхр. контроль)', False, (a.size, b.size))",
    "chk('I2 мобильная p1 идентична day-navglide (синхр. контроль)', False, (a.size, b.size))",
    1))
REPL.append((
    "chk('I2 мобильная p1 идентична day-navfade (синхр. контроль, ниже навигации)',",
    "chk('I2 мобильная p1 идентична day-navglide (синхр. контроль, ниже навигации)',",
    1))
REPL.append((
    "chk('I1/I2 идентичность (нет контроля day-navfade)', False, 'нет blob в git')",
    "chk('I1/I2 идентичность (нет контроля day-navglide)', False, 'нет blob в git')",
    1))

# --- RM-блок -> LM-блок -------------------------------------------------------
OLD_RM = '''    # --- prefers-reduced-motion ---
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
    ctx.close()'''
NEW_LM = '''    # --- LM: prefers-reduced-motion больше НЕ глушит анимации (day-livemotion) ---
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    pr = ctx.new_page()
    pr.goto(URL, wait_until='load')
    lm = pr.evaluate("""() => {
      const c = getComputedStyle(document.getElementById('a01'));
      const s = getComputedStyle(document.getElementById('p1'));
      return {aName: c.animationName, aDur: c.animationDuration, sDur: s.animationDuration,
              rm: window.matchMedia('(prefers-reduced-motion: reduce)').matches};
    }""")
    chk('LM1 reduce: ОС просит уменьшить движение, но day-motion жив (0.55s/0.65s, не 0.01ms)',
        lm['rm'] and lm['aName'] == 'sfn-rise' and lm['aDur'] == '0.55s'
        and lm['sDur'] == '0.65s', lm)
    pr.wait_for_timeout(900)
    rec_rm = pr.evaluate(SAMPLER, {'y0': 0, 'btn': 'navNext', 'n': 55})
    both_rm = [f for f in rec_rm if sum(1 for s in f['s'] if s['d'] != 'none') >= 2]
    mids_rm = sorted({s['o'] for f in both_rm for s in f['s'] if 0.02 < s['o'] < 0.98})
    chk('LM2 reduce: кроссфейд проигрывается (сосуществование полос, промежуточные opacity)',
        len(both_rm) >= 8
        and any('page-exit' in s['c'] for f in rec_rm for s in f['s'])
        and any('page-enter-next' in s['c'] for f in rec_rm for s in f['s'])
        and len(mids_rm) >= 3, (len(both_rm), mids_rm[:4]))
    chk('LM3 reduce: финал перехода — scrollY=0, уходящая полоса снята',
        rec_rm[-1]['y'] == 0
        and rec_rm[-1]['s'][0]['d'] == 'none' and rec_rm[-1]['s'][1]['d'] == 'block',
        rec_rm[-1]['y'])
    pr.wait_for_timeout(1200)
    r2 = pr.evaluate(STATE)
    chk('LM4 reduce: после оседания p2 активна, счётчик 2 / 4, блокировка и minHeight вычищены',
        r2['counter'] == '2 / 4' and r2['disp'] == ['none', 'block', 'none', 'none']
        and not any(r2['busyCls']) and r2['minH'] == '', r2['counter'])
    ctx.close()'''
REPL.append((OLD_RM, NEW_LM, 1))

# --- применения замен (сначала точечные REPL, затем рендерные пути) ----------
for i, (old, new, cnt) in enumerate(REPL, 1):
    got = src.count(old)
    assert got == cnt, f'REPL#{i}: найдено {got}, ожидалось {cnt}: {old[:70]!r}'
    src = src.replace(old, new)

# --- рендеры v18_ -> v19_ -----------------------------------------------------
n18 = src.count('v18_')
src = src.replace('v18_', 'v19_')
print(f'замен v18_ -> v19_: {n18}')
assert n18 >= 8, 'подозрительно мало рендерных имён v18_'

assert 'day-navfade' not in src, 'в QA осталось упоминание day-navfade'
assert 'RM1' not in src and 'RM2 reduced' not in src, 'старый RM-блок уцелел'
assert src.count('day-livemotion') >= 3

with open(DST, 'w', encoding='utf-8') as fh:
    fh.write(src)
py_compile.compile(DST, doraise=True)
print('создан', DST, f'({len(src)} байт), компилируется')
