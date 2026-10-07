#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN verify: выпуск 03.10.2026 не тронут новым коммитом (04.10.2026).

Синхронный контроль в ОДНОЙ сессии одним протоколом:
  A = blob abbfefe (наш опубликованный day-pageindicator);
  B = текущий anna-malboro/daily-03-10-2026.html (= origin/main = загрузка Анны 008565a);
  C = blob 008565a (загрузка Анны) — сверка байт-в-байт с B.
Ожидание: A и B отличаются ТОЛЬКО в строке заголовка a10 (правка Анны
«стоянка молчит» → «стоянка пустует») и ведущим \\r; всё остальное — 0 пикселей.
Плюс рендер полосы 1 обоих выпусков для композита.
Запуск из корня клона: python3 worktmp/verify_old_intact.py
"""
import hashlib
import os

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = os.getcwd()
REND = os.path.join(os.path.dirname(ROOT), 'renders')
SCRATCH = os.path.join(os.path.dirname(ROOT), 'scratch_qa')
OLD_NOW = os.path.join(ROOT, 'anna-malboro', 'daily-03-10-2026.html')
OLD_ABB = os.path.join(SCRATCH, 'old_abbfefe.html')
OLD_UP = os.path.join(SCRATCH, 'old_anna_upload.html')
NEW = os.path.join(ROOT, 'anna-malboro', 'daily-04-10-2026.html')

res = []


def chk(name, ok, note=''):
    res.append((name, bool(ok), note))
    print(f"[{'OK ' if ok else 'FAIL'}] {name} {note}")


def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def diff(a, b):
    ia = np.asarray(Image.open(a).convert('L'), dtype=np.int16)
    ib = np.asarray(Image.open(b).convert('L'), dtype=np.int16)
    if ia.shape != ib.shape:
        return None, None, f'разные размеры {ia.shape} vs {ib.shape}'
    d = np.abs(ia - ib)
    ys, xs = np.where(d > 8)
    box = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else None
    return int((d > 8).sum()), int(d.max()), box


def main():
    # --- 1. байт-уровень ---
    chk('B == C (текущий файл = загрузка Анны 008565a)', sha1(OLD_NOW) == sha1(OLD_UP),
        sha1(OLD_NOW)[:12])
    chk('B != A (отличается от нашей сборки только правкой Анны)', sha1(OLD_NOW) != sha1(OLD_ABB))
    a = open(OLD_ABB, encoding='utf-8').read()
    b = open(OLD_NOW, encoding='utf-8').read()
    chk('штамп 03.10 не изменился: SFN-DESIGN-029: day-pageindicator',
        'SFN-DESIGN-029: day-pageindicator' in b and 'SFN · 2026 · 029 · day-pageindicator' in b)
    chk('правка Анны на месте: «стоянка пустует»', 'стоянка пустует' in b and 'стоянка молчит' not in b)
    chk('в нашей сборке abbfefe было «стоянка молчит»', 'стоянка молчит' in a)
    chk('размер правки: только заголовок + ведущий \\r',
        b.lstrip('\r\n').replace('пустует', 'молчит') == a.lstrip('\r\n').replace('пустует', 'молчит'))
    chk('навигация-канон цела: плашка pageIndicatorInOut, счётчик navCount удалён',
        'pageIndicatorInOut' in b and 'navCount' not in b)
    chk('новый выпуск 04.10 — отдельный файл, 03.10 не перезаписан',
        os.path.basename(NEW) != os.path.basename(OLD_NOW) and sha1(NEW) != sha1(OLD_NOW))

    # --- 2. рендер-контроль одной сессией, одним протоколом ---
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={'width': 1440, 'height': 1000})
        def walk(pg, url, prefix, pages):
            pg.goto('file://' + url)
            pg.wait_for_timeout(900)
            pg.evaluate('document.fonts.ready.then(()=>1)')
            pg.wait_for_timeout(400)
            pg.mouse.move(0, 0)
            out = {}
            for i in pages:
                while True:                      # листаем до нужной полосы
                    vis = pg.evaluate(
                        '(()=>{const e=document.getElementById("p%d");'
                        'return !!e && e.offsetParent!==null})()' % i)
                    if vis:
                        break
                    pg.click('#navNext')
                    pg.wait_for_timeout(1100)
                pg.wait_for_timeout(350)
                out[i] = os.path.join(REND, f'{prefix}_p{i}.png')
                pg.locator(f'#p{i}').screenshot(path=out[i])
            return out

        A = walk(pg, OLD_ABB, 'verify-0310-abbfefe', (1, 3))
        B = walk(pg, OLD_NOW, 'verify-0310-origin', (1, 2, 3, 4))
        pg2 = br.new_page(viewport={'width': 1440, 'height': 1000})
        N = walk(pg2, NEW, 'verify-0410-origin', (1,))
        br.close()
        pa, pa3 = A[1], A[3]
        pb, pb3 = B[1], B[3]
        pn = N[1]

    n, mx, box = diff(pa, pb)
    chk('полоса 1: 03.10 сейчас == наша сборка day-pageindicator (пиксельно)',
        n is not None and n == 0, f'пикселей с Δ>8: {n}, max Δ: {mx}')
    n3, mx3, box3 = diff(pa3, pb3)
    chk('полоса 3: отличие только в строке заголовка a10 (правка Анны)',
        n3 is not None and 0 < n3 < 6000 and box3 is not None
        and (box3[3] - box3[1]) < 80 and (box3[2] - box3[0]) < 1000,
        f'пикселей с Δ>8: {n3}, max Δ: {mx3}, область: {box3}')

    # --- 3. композит «старая / новая» ---
    from PIL import ImageFont
    FP = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    FPR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    f_h = ImageFont.truetype(FP, 20) if os.path.exists(FP) else ImageFont.load_default()
    f_s = ImageFont.truetype(FPR, 15) if os.path.exists(FPR) else ImageFont.load_default()
    im_old = Image.open(pb).convert('RGB')
    im_new = Image.open(pn).convert('RGB')
    h = max(im_old.height, im_new.height)
    gap, pad, head = 28, 24, 92
    W = pad * 2 + im_old.width + gap + im_new.width
    canvas = Image.new('RGB', (W, h + head + pad), '#e8e4dc')
    canvas.paste(im_old, (pad, head))
    canvas.paste(im_new, (pad + im_old.width + gap, head))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, head - 6], fill='#16283c')
    d.rectangle([0, head - 9, W, head - 6], fill='#c8102e')
    d.text((pad, 14), 'ВЫПУСК 03.10.2026 — НЕ ТРОНУТ: байт-в-байт как был',
           font=f_h, fill='#f4f1ea')
    d.text((pad, 44), f'SFN-DESIGN-029: day-pageindicator · sha1 {sha1(OLD_NOW)[:8]}… · '
                      'правка главреда «стоянка пустует» на месте', font=f_s, fill='#c9d3df')
    d.text((pad + im_old.width + gap, 14), 'ВЫПУСК 04.10.2026 — НОВЫЙ, отдельный файл',
           font=f_h, fill='#f4f1ea')
    d.text((pad + im_old.width + gap, 44), 'SFN-DESIGN-030: chronicle-digest · 12 кадров',
           font=f_s, fill='#c9d3df')
    d.line([pad + im_old.width + gap // 2, head, pad + im_old.width + gap // 2, h + head],
           fill='#c8102e', width=3)
    out = os.path.join(REND, 'verify-old-intact.png')
    canvas.save(out)
    print('композит:', out, canvas.size)

    ok = all(r[1] for r in res)
    print(f'\n=== {sum(1 for r in res if r[1])}/{len(res)} проверок '
          f'{"ALL GREEN" if ok else "ЕСТЬ ПРОВАЛЫ"} ===')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
