#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN capture: живой превью-ролик анимаций day-livemotion (04.10.2026).

Сценарий (1200px ширина): перезагрузка полосы 1 — виден загрузочный каскад
day-motion (sfn-rise/sfn-fade) → клик → кроссфейд 1→2 с плавной прокруткой.
Запись — CDP Page.startScreencast (JPEG-кадры с метками времени). Память бережём:
JPEG-байты храним сырыми, декодируем потоково. Сборка:
  renders/anim-preview.mp4 (30 fps, libx264) — ролик целиком;
  renders/anim-load.gif    (12 fps, палитра покадрово) — каскад + кроссфейд.
Запуск из корня клона: python3 worktmp/capture_anim.py
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
        pg.wait_for_timeout(300)
        pg.reload(wait_until='load')          # загрузочный каскад day-motion
        pg.wait_for_timeout(2100)
        pg.click('#navNext')                  # кроссфейд 1→2
        pg.wait_for_timeout(1700)
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
    mp4 = os.path.join(REND, 'anim-preview.mp4')
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

    # --- GIF: всё окно записи, 12 fps, покадровая палитра ---
    gf = []
    idx = 0
    t = ts[0]
    while t < ts[-1] - 0.05:
        idx = pick(ts, t, idx)
        im = Image.open(io.BytesIO(frames[idx][1])).convert('RGB')
        im = im.resize((860, round(im.height * 860 / im.width)), Image.LANCZOS)
        gf.append(im.convert('P', palette=Image.ADAPTIVE, colors=192))
        t += 1.0 / 12
    gp = os.path.join(REND, 'anim-load.gif')
    gf[0].save(gp, save_all=True, append_images=gf[1:], duration=83, loop=0,
               optimize=True)
    print('gif кадров:', len(gf), os.path.getsize(gp) // 1024, 'КБ')
    print(f'готово за {time.time() - t0:.0f} c')


main()
