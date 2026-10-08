#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN · рендер полос выпуска 04.10.2026 (terra-ivory): 6 PNG + композит + гифка перехода.
Запуск из корня workspace: python3 sf-repo/worktmp/capture_0410_v4.py"""
import os
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = os.getcwd()
HTML_PATH = os.path.join(ROOT, 'sf-repo', 'anna-malboro', 'daily-04-10-2026.html')
OUT = os.path.join(ROOT, 'renders')
os.makedirs(OUT, exist_ok=True)
IDS = ['b1', 'b2', 'b3', 'b4', 'b5', 'b6']

with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--disable-dev-shm-usage', '--no-sandbox'])
    pg = br.new_page(viewport={'width': 1440, 'height': 1000})
    pg.goto('file://' + HTML_PATH)
    pg.evaluate('document.fonts.ready.then(()=>1)')
    pg.wait_for_timeout(2800)  # стартовая плашка «ПОЛОСА 1 / 6» должна погаснуть
    for n, sid in enumerate(IDS):
        for _ in range(8):
            if pg.evaluate("!document.getElementById('%s').classList.contains('st-off')" % sid):
                break
            pg.click('#rlxNext'); pg.wait_for_timeout(900)
        pg.evaluate('window.scrollTo(0,0)')
        pg.wait_for_timeout(2600)  # полный цикл временной плашки (~2.44s) — в кадр не попадает
        pg.locator('#' + sid).screenshot(path=os.path.join(OUT, 'd0410_v4_p%d.png' % (n + 1)))
        print('shot', sid)
    # гифка перехода b1 -> b2: 5 кадров кроссфейда
    pg.set_viewport_size({'width': 900, 'height': 640})
    pg.evaluate('window.scrollTo(0,0)')
    pg.wait_for_timeout(2600)
    shots, delays = [], [0, 140, 160, 160, 240]
    pg.click('#rlxNext')
    for d in delays:
        pg.wait_for_timeout(d)
        p = os.path.join(OUT, '_tr%d.png' % len(shots))
        pg.screenshot(path=p)
        shots.append(p)
    br.close()

thumbs = []
W = 520
for n in range(6):
    im = Image.open(os.path.join(OUT, 'd0410_v4_p%d.png' % (n + 1))).convert('RGB')
    h = round(im.height * W / im.width)
    thumbs.append(im.resize((W, h)))
cols, rows = 3, 2
H = max(t.height for t in thumbs)
canvas = Image.new('RGB', (cols * W + 40, rows * H + 30), (30, 33, 38))
for i, t in enumerate(thumbs):
    x = (i % cols) * (W + 10) + 10
    y = (i // cols) * (H + 10) + 10
    canvas.paste(t, (x, y))
canvas.save(os.path.join(OUT, 'preview-all-0410-v4.png'))
print('composite', canvas.size)

frames = []
for p in shots:
    im = Image.open(p).convert('RGB').resize((900, 640)).quantize(colors=128, method=Image.ADAPTIVE)
    frames.append(im)
    os.remove(p)
frames[0].save(os.path.join(OUT, 'anim-terra-transition.gif'), save_all=True,
               append_images=frames[1:], duration=260, loop=0)
print('gif ok')
