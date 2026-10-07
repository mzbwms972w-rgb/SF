#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN · рендер полос выпуска 04.10.2026 (red-pink-bold): 6 PNG + композит.
Запуск из корня workspace: python3 sf-repo/worktmp/capture_0410_v2.py"""
import os
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = os.getcwd()
HTML_PATH = os.path.join(ROOT, 'sf-repo', 'anna-malboro', 'daily-04-10-2026.html')
OUT = os.path.join(ROOT, 'renders')
os.makedirs(OUT, exist_ok=True)
IDS = ['s1', 's2', 's3', 's4', 's5', 's6']

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={'width': 1440, 'height': 1000})
    pg.goto('file://' + HTML_PATH)
    pg.evaluate('document.fonts.ready.then(()=>1)')
    pg.wait_for_timeout(1200)
    for n, sid in enumerate(IDS):
        # долистать до нужной полосы стрелками (скрытые листы нельзя снять)
        for _ in range(8):
            if pg.evaluate("!document.getElementById('%s').classList.contains('is-off')" % sid):
                break
            pg.click('#navNext'); pg.wait_for_timeout(850)
        pg.evaluate('window.scrollTo(0,0)')
        pg.wait_for_timeout(1950)  # полный цикл временной плашки 1.6s — в кадр не попадает
        pg.locator('#' + sid).screenshot(path=os.path.join(OUT, 'd0410_v2_p%d.png' % (n + 1)))
        print('shot', sid)
    br.close()

thumbs = []
W = 520
for n in range(6):
    im = Image.open(os.path.join(OUT, 'd0410_v2_p%d.png' % (n + 1))).convert('RGB')
    h = round(im.height * W / im.width)
    thumbs.append(im.resize((W, h)))
cols, rows = 3, 2
H = max(t.height for t in thumbs)
canvas = Image.new('RGB', (cols * W + 40, rows * H + 30), (255, 255, 255))
for i, t in enumerate(thumbs):
    x = (i % cols) * (W + 10) + 10
    y = (i // cols) * (H + 10) + 10
    canvas.paste(t, (x, y))
canvas.save(os.path.join(OUT, 'preview-all-0410-v2.png'))
print('composite', canvas.size)
