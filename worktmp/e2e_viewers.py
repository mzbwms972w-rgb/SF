#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN e2e — проверка анимаций через РЕАЛЬНЫЕ пути просмотра главреда:
  A) htmlpreview.github.io (ссылка, которую даём Анне)
  B) raw.githack.com (запасной прямой просмотр)
  C) локальный файл при prefers-reduced-motion: reduce (гипотеза «анимации не работают»)
  D) локальный файл, контроль no-preference
Запуск: python3 worktmp/e2e_viewers.py  (cwd = корень клона sf-desk)
"""
import asyncio
import json
import os
import time

from playwright.async_api import async_playwright

BASE = os.getcwd()
LOC = 'file://' + os.path.join(BASE, 'anna-malboro', 'daily-03-10-2026.html')
HP = ('https://htmlpreview.github.io/?https://github.com/mzbwms972w-rgb/SF/'
      'blob/main/anna-malboro/daily-03-10-2026.html?v=day-navglide-e2e')
RG = 'https://raw.githack.com/mzbwms972w-rgb/SF/main/anna-malboro/daily-03-10-2026.html'

SAMPLER = """(cfg) => new Promise(res => {
  const g = i => document.getElementById('p' + i);
  window.scrollTo(0, cfg.y0);
  const rec = [];
  requestAnimationFrame(function tick(){
    const fr = {y: Math.round(window.scrollY), s: []};
    for (let i = 1; i <= 4; i++){
      const c = getComputedStyle(g(i));
      fr.s.push({d: c.display, o: +(+c.opacity).toFixed(3), t: c.transform, c: g(i).className});
    }
    rec.push(fr);
    if (rec.length === 3) document.getElementById(cfg.btn)
      .dispatchEvent(new MouseEvent('click', {bubbles: true}));
    if (rec.length < cfg.n) requestAnimationFrame(tick); else res(rec);
  });
})"""


def analyse(rec):
    both = [f for f in rec if sum(1 for s in f['s'] if s['d'] != 'none') >= 2]
    mids = sorted({s['o'] for f in both for s in f['s'] if 0.02 < s['o'] < 0.98})
    tys = []
    for f in both:
        for s in f['s']:
            if 'page-enter' in s['c'] and s['t'].startswith('matrix'):
                tys.append(round(float(s['t'].split(',')[5]), 1))
    return {
        'frames': len(rec),
        'both_visible_frames': len(both),
        'mid_opacities': mids[:8],
        'enter_ty_range': [min(tys), max(tys)] if tys else None,
        'exit_class_seen': any('page-exit' in s['c'] for f in rec for s in f['s']),
        'enter_class_seen': any('page-enter-next' in s['c'] for f in rec for s in f['s']),
        'final': [{'d': s['d'], 'o': s['o']} for s in rec[-1]['s']],
        'scroll_vals': sorted({f['y'] for f in rec}),
    }


async def find_frame(page, timeout=100):
    t0 = time.time()
    while time.time() - t0 < timeout:
        for fr in page.frames:
            try:
                ok = await fr.evaluate(
                    "!!document.getElementById('newspaper') && "
                    "!!document.getElementById('navNext')")
                if ok:
                    return fr
            except Exception:
                pass
        await asyncio.sleep(0.5)
    return None


async def probe(browser, label, url, reduced=None):
    kw = {'viewport': {'width': 1440, 'height': 900}}
    if reduced:
        kw['reduced_motion'] = reduced
    ctx = await browser.new_context(**kw)
    page = await ctx.new_page()
    out = {'label': label, 'reduced_motion': reduced or 'default'}
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:120]))
    try:
        t0 = time.time()
        await page.goto(url, wait_until='domcontentloaded', timeout=120000)
        fr = await find_frame(page)
        out['load_s'] = round(time.time() - t0, 1)
        if fr is None:
            # может, контент прямо в основной странице (локальный файл)
            try:
                ok = await page.evaluate("!!document.getElementById('navNext')")
            except Exception:
                ok = False
            fr = page.main_frame if ok else None
        out['frame_found'] = bool(fr)
        if fr is not None:
            out['frame_url'] = fr.url[:90]
            st = await fr.evaluate("""() => ({
                jsnav: document.documentElement.className.includes('js-nav'),
                navdisp: getComputedStyle(document.querySelector('.sheetnav')).display,
                counter: (document.getElementById('navCount')||{}).textContent,
                rm: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
                stamp: (document.body.innerHTML.match(/SFN-DESIGN-029: ([a-z0-9-]+)/)||[])[1] || null,
                disp: [1,2,3,4].map(i=>getComputedStyle(document.getElementById('p'+i)).display)
            })""")
            out.update(st)
            rec = await fr.evaluate(SAMPLER, {'y0': 0, 'btn': 'navNext', 'n': 55})
            out['sampler'] = analyse(rec)
            # день-моушен: есть ли day-in/day-motion элементы и анимируются ли
            dm = await fr.evaluate("""() => {
                const el = document.querySelector('.day-motion');
                if (!el) return {present:false};
                const c = getComputedStyle(el);
                return {present:true, cls: el.className, dur: c.animationDuration,
                        opacity: c.opacity};
            }""")
            out['day_motion_probe'] = dm
    except Exception as e:
        out['error'] = str(e)[:200]
    out['pageerrors'] = errs[:3]
    await ctx.close()
    return out


async def main():
    results = []
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        for label, url, rm in [
            ('A htmlpreview (ссылка Анны)', HP, None),
            ('B raw.githack (прямой)', RG, None),
            ('C локальный + reduce (гипотеза)', LOC, 'reduce'),
            ('D локальный контроль', LOC, 'no-preference'),
        ]:
            r = await probe(br, label, url, rm)
            results.append(r)
            print(json.dumps(r, ensure_ascii=False, indent=1)[:1600])
            print('=' * 60)
        await br.close()
    json.dump(results, open(os.path.join(BASE, 'worktmp', 'e2e_viewers_result.json'), 'w'),
              ensure_ascii=False, indent=1)


asyncio.run(main())
