#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN capture: превью-ролик временного индикатора полосы (day-pageindicator).

Сценарий (1360×860): лист 2 в покое → клик → → кроссфейд 2→3 и одновременно
плашка «ПОЛОСА 3 / 4» (появление → пауза → уход) → плашка гаснет, кадр чистый.
Запись — CDP Page.startScreencast (JPEG-кадры), декодирование потоковое.
Сборка:
  renders/anim-indicator.mp4      (30 fps, libx264) — сцена целиком;
  renders/anim-indicator.gif      (12 fps, 860px) — то же, лёгкий GIF;
  renders/anim-indicator-top.gif  (12 fps, крупный план верха) — цикл плашки.
Запуск из корня клона: python3 worktmp/capture_pageindicator.py
"""
import base64
import gc
import io
import os
import time

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.getcwd()
URL = 'file://' + os.path.join(ROOT, 'anna-malboro', 'daily-03-10-2026.html')
REND = os.path.join(os.path.dirname(ROOT), 'renders')
W_MAX = 1360

frames = []  # (timestamp, jpeg-bytes)


def run():
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={'width': 1360, 'height': 860})
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(2500)
        pg.click('#navNext')          # сразу на полосу 2: ролик про индикатор
        pg.wait_for_timeout(2600)
        pg.mouse.move(0, 0)
        client = pg.context.new_cdp_session(pg)

        def on_frame(ev):
            frames.append((ev['metadata']['timestamp'], base64.b64decode(ev['data'])))
            try:
                client.send('Page.screencastFrameAck', {'sessionId': ev['sessionId']})
            except Exception:
                pass

        client.on('Page.screencastFrame', on_frame)
        client.send('Page.startScreencast',
                    {'format': 'jpeg', 'quality': 70,
                     'maxWidth': W_MAX, 'maxHeight': 860, 'everyNthFrame': 1})
        pg.wait_for_timeout(600)      # покой: счётчика нигде нет
        pg.click('#navNext')          # переход 2→3 + плашка «ПОЛОСА 3 / 4»
        pg.wait_for_timeout(2600)     # кроссфейд 0.6s + цикл плашки 1.6s + хвост
        client.send('Page.stopScreencast')
        pg.wait_for_timeout(300)
        br.close()


def pick(ts, t, idx):
    while idx + 1 < len(ts) and ts[idx + 1] <= t:
        idx += 1
    return idx


def main():
    t0 = time.time()
    run()
    span = frames[-1][0] - frames[0][0]
    print(f'кадров снято: {len(frames)} за {span:.2f} c',
          f'(~{len(frames) / max(span, .1):.0f} fps)')
    ts = [f[0] - frames[0][0] for f in frames]
    size = Image.open(io.BytesIO(frames[0][1])).size
    print('размер кадра:', size)

    # --- MP4: потоковое декодирование, 30 fps ---
    import imageio
    mp4 = os.path.join(REND, 'anim-indicator.mp4')
    w = imageio.get_writer(mp4, fps=30, codec='libx264', quality=8,
                           pixelformat='yuv420p', macro_block_size=2)
    n = int(span * 30)
    idx = 0
    for k in range(n):
        t = ts[0] + k / 30.0
        idx = pick(ts, t, idx)
        im = Image.open(io.BytesIO(frames[idx][1])).convert('RGB')
        w.append_data(np.asarray(im))
    w.close()
    gc.collect()
    print('mp4 кадров:', n, os.path.getsize(mp4) // 1024, 'КБ')

    # --- GIF: вся сцена, 12 fps, покадровая палитра ---
    gf, gf_top = [], []
    idx = 0
    t = ts[0]
    while t < ts[-1] - 0.05:
        idx = pick(ts, t, idx)
        im = Image.open(io.BytesIO(frames[idx][1])).convert('RGB')
        w860 = im.resize((860, round(im.height * 860 / im.width)), Image.LANCZOS)
        gf.append(w860.convert('P', palette=Image.ADAPTIVE, colors=192))
        # крупный план верха: плашка и верх листа (в координатах исходного кадра)
        cx = im.width // 2
        top = im.crop((cx - 420, 0, cx + 420, 190))
        gf_top.append(top.resize((720, round(top.height * 720 / top.width)),
                                 Image.LANCZOS).convert('P', palette=Image.ADAPTIVE,
                                                         colors=128))
        t += 1.0 / 12
    gp = os.path.join(REND, 'anim-indicator.gif')
    gf[0].save(gp, save_all=True, append_images=gf[1:], duration=83, loop=0,
               optimize=True)
    print('gif кадров:', len(gf), os.path.getsize(gp) // 1024, 'КБ')
    gt = os.path.join(REND, 'anim-indicator-top.gif')
    gf_top[0].save(gt, save_all=True, append_images=gf_top[1:], duration=83, loop=0,
                   optimize=True)
    print('gif-top кадров:', len(gf_top), os.path.getsize(gt) // 1024, 'КБ')
    print(f'готово за {time.time() - t0:.0f} c')


main()
