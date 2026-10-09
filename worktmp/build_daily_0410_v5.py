#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN · сборщик ежедневного выпуска 09.10.2026, раунд 5 (anna-malboro/daily-04-10-2026.html).

Новая композиционная система «полнополосные кадры» по брифу главреда от 10.10.2026,
штамп SFN-DESIGN-034. Бриф: убрать случайные пустоты, фотографии — полноценные участники
композиции (крупные и разные по размеру), каждая полоса — своя законченная сцена,
текст читаем, кадры не кропаются и не растягиваются, характер выпуска сохранён и
не повторяет предыдущую сборку (terra-ivory, SFN-DESIGN-033).

ЧТО МЕНЯЕТСЯ ОТНОСИТЕЛЬНО РАУНДА 4 (только композиция, не содержание):
— Архитектура полос: вместо одного grid с жёсткими областями и align-content:start
  (главный источник дыр под содержимым) — колонка из РЯДОВ (.rlx-row), у каждого ряда
  свои пропорции колонок; элементы ряда растягиваются (align-items:stretch), а внутри
  материала содержимое распределяется (justify-content:space-between), поэтому остаток
  высоты читается как воздух между ставкой и подписью, а не как забытая дыра.
— Фотографии больше НЕ урезаются классами ширины 72/76/78%: каждый кадр занимает всю
  ширину своей колонки; размер кадра задаётся шириной колонки и местом в сцене,
  поэтому в выпуске соседствуют полнополосные, колонные и парные кадры.
— Обложка: кадр вертолёта стал полнополосной пластиной под титулом (был колонкой 600px
  справа), вступление и мета вынесены в нижний ряд — титул и кадр равноправны и полоса
  заполнена сверху донизу.
— «Тоннель» и «Город»: зеркальные сцены (кадр справа → кадр слева и наоборот), чтобы
  глаз шёл по полосе диагональю; прежняя раскладка оставляла до 40% пустой колонки.
— Финал без фото заполнен типографикой: крупнее титул, просторнее лента из 12 событий
  с вертикальным разделителем колонок, колофон прижат к низу полосы.
— Палитра терра/бумага, корешок-спайн, шрифтовая иерархия, навигация и моушен системы rlx
  НЕ меняются (байт-в-байт из раундов 3–4): right-hand инвариант редакции.
— Тексты материалов, подписи, плашки, 12 фотографий — байт-в-байт, каждый кадр ровно один раз.

Запуск:  python3 build_daily_0410_v5.py <путь-к-папке-с-12-фото> <путь-к-файлу-вывода>
Фото читаются байт-в-байт, base64 без перекодирования.
"""
import base64, os, re, sys

UP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), 'uploads')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), 'out.html')
assert os.path.isdir(UP), UP

STAMP = '/* SFN-DESIGN-034: full-plate · 09.10.2026 */'
MARKER = '<!-- SFN · 2026 · 034 · full-plate -->'
COPY = '<!-- © 2026 San Fierro News. Дизайн и вёрстка защищены: CC BY-NC-ND 4.0. Копирование и переработка запрещены. -->'

# ---- 12 фотографий: ключ -> (имя файла, mime) ----
PH = {
 'm01': ('Массовое убийство на трассе Лас-Вентураса — четверо погибших, включая офицера полиции.jpg', 'image/jpeg'),
 'm02': ('Тело мужчины обнаружено в тоннеле между Лос-Сантосом и Сан-Фиерро — есть задержанный.png', 'image/png'),
 'm03': ('Вертолёт обнаружен посреди тоннеля между Лос-Сантосом и Сан-Фиерро.jpg', 'image/jpeg'),
 'm04': ('В тоннеле между Лос-Сантосом и Сан-Фиерро обнаружен сотрудник полиции без сознания.jpg', 'image/jpeg'),
 'm05': ('Кровавая расправа на трассе между Лас-Вентурасом и Сан-Фиерро — двое погибших.jpg', 'image/jpeg'),
 'm06': ('Двойная трагедия на дороге в Лос-Сантосе — два тела на месте происшествия.jpg', 'image/jpeg'),
 'm07': ('В Сан-Фиерро перевернулась фура — движение на перекрёстке парализовано.png', 'image/png'),
 'm08': ('Пирс на пляже Санта-Мария перекрыт — полиция и скорая на месте.jpg', 'image/jpeg'),
 'm09': ('Тело женщины обнаружено у пляжа Санта-Мария в Лос-Сантосе.png', 'image/png'),
 'm10': ('У полицейского участка в Лос-Сантосе замечено массовое скопление полиции и машина редакции LSN.png', 'image/png'),
 'm11': ('В мэрии Лос-Сантоса выставлен на продажу бизнес Carsharing Guaranteed за рекордные $1.800.000.000.jpg', 'image/jpeg'),
 'm12': ('В Сан-Фиерро упал самолёт — на месте работают экстренные службы.jpg', 'image/jpeg'),
}
DATA = {}
for k, (fn, mime) in PH.items():
    p = os.path.join(UP, fn)
    assert os.path.isfile(p), p
    raw = open(p, 'rb').read()
    DATA[k] = 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode('ascii'))

# ============================== CSS ==============================
CSS = STAMP + """
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans+Condensed:wght@700;900&family=Inter:wght@400;500;600;700;800&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
img{display:block;width:100%;height:auto}
/* ==== ЕДИНСТВЕННАЯ система переменных: терра и бумага (не меняется с раунда 4) ==== */
:root{--ink:#232a31;--night:#191e24;--paper:#f5f0e6;--porc:#ebe2d0;--acc:#ab5233;--acc-deep:#8a3f26;
--acc-soft:#d9906c;--och:#bd8a3f;--mut:#6f685c;--fog:#c3bcae;--body:#4b453b;--spine:64px;--gut:30px;--pad:46px}
::selection{background:var(--acc);color:#fff}
html{-webkit-text-size-adjust:100%}
body{background:#1e2126;color:var(--ink);font-family:"Inter","Helvetica Neue",Arial,sans-serif;padding:0 0 80px}
/* ==== полосы-экраны: корешок + основное поле ==== */
.rlx-deck{display:block}
.rlx-band{max-width:1160px;margin:0 auto 36px;min-height:100vh;background:var(--paper);color:var(--ink);
position:relative;display:grid;grid-template-columns:var(--spine) 1fr;grid-template-areas:"spine main";
box-shadow:0 30px 80px rgba(0,0,0,.45);overflow:hidden}
.rlx-spine{grid-area:spine;background:var(--ink);color:var(--paper);display:flex;flex-direction:column;
align-items:center;justify-content:space-between;padding:20px 0 18px}
.rlx-spine span{writing-mode:vertical-rl;transform:rotate(180deg);font:700 12px/1 "Inter";
letter-spacing:.42em;text-transform:uppercase;white-space:nowrap}
.rlx-spine b{width:38px;height:38px;background:var(--acc);color:#fff;display:grid;place-items:center;
font:900 14px/1 "Fira Sans Condensed","Inter",sans-serif;letter-spacing:.02em}
.rlx-graph{background:var(--ink);color:var(--paper)}
.rlx-graph .rlx-spine{background:var(--acc);color:#fff}
.rlx-graph .rlx-spine b{background:var(--paper);color:var(--ink)}
.rlx-ink{background:var(--night);color:#efe9dd}
.rlx-ink .rlx-spine{background:var(--acc)}
.rlx-ink .rlx-spine b{background:var(--paper);color:var(--night)}
.rlx-porc{background:var(--porc)}
/* ==== поле полосы: колонка из рядов, остаток высоты — воздухом МЕЖДУ рядами ==== */
.rlx-main{grid-area:main;padding:var(--pad) var(--pad) var(--pad) 42px;display:flex;
flex-direction:column;gap:var(--gut);justify-content:space-between}
.rlx-row{display:grid;gap:var(--gut);align-items:stretch}
.rlx-row.r-55-45{grid-template-columns:55fr 45fr}
.rlx-row.r-45-55{grid-template-columns:45fr 55fr}
.rlx-row.r-58-42{grid-template-columns:58fr 42fr}
.rlx-row.r-42-58{grid-template-columns:42fr 58fr}
.rlx-row.r-46-54{grid-template-columns:46fr 54fr}
.rlx-row.r-54-46{grid-template-columns:54fr 46fr}
.rlx-row.r-62-38{grid-template-columns:62fr 38fr}
.rlx-row.r-38-62{grid-template-columns:38fr 62fr}
.rlx-row.r-66-34{grid-template-columns:66fr 34fr}
.rlx-row.r-50-50{grid-template-columns:50fr 50fr}
.rlx-row.r-1{grid-template-columns:1fr}
/* ==== типографика и компоненты системы ==== */
.rlx-kick{display:inline-block;background:var(--ink);color:var(--paper);font:700 11.5px/1 "Inter";
letter-spacing:.22em;text-transform:uppercase;padding:9px 13px}
.rlx-kick-inv{background:var(--acc);color:#fff}
.rlx-ink .rlx-kick{background:var(--acc-soft);color:var(--night)}
.rlx-head{display:flex;flex-direction:column;gap:14px;align-items:flex-start}
.rlx-h2{font-family:"Fira Sans Condensed","Inter",sans-serif;font-weight:900;
font-size:clamp(36px,5.2vw,70px);line-height:.96;letter-spacing:-.005em}
.rlx-graph .rlx-h2,.rlx-ink .rlx-h2{color:var(--paper)}
.rlx-rd{color:var(--acc)}
.rlx-rs{color:var(--acc-soft)}
.rlx-sub{font:600 15.5px/1.5 "Inter";color:var(--mut);max-width:720px}
.rlx-ink .rlx-sub,.rlx-graph .rlx-sub{color:var(--fog)}
.rlx-rule{height:6px;width:100%;background:var(--acc);transform-origin:left center;margin-top:6px}
.rlx-graph .rlx-rule,.rlx-ink .rlx-rule{background:var(--acc-soft)}
.rlx-item{display:flex;flex-direction:column;gap:16px}
.rlx-item.rlx-mid{justify-content:center}
.rlx-stack{display:flex;flex-direction:column;gap:26px}
.rlx-note{display:flex;flex-direction:column;gap:7px}
.rlx-h3{font-family:"Fira Sans Condensed","Inter",sans-serif;font-weight:700;
font-size:clamp(21px,1.9vw,27px);line-height:1.04;text-transform:uppercase;letter-spacing:.012em}
.rlx-ink .rlx-h3{color:var(--paper)}
.rlx-lead{font:700 14.5px/1.4 "Inter";color:var(--acc)}
.rlx-ink .rlx-lead{color:var(--acc-soft)}
.rlx-tx{font:400 14.5px/1.62 "Inter";color:var(--body)}
.rlx-ink .rlx-tx{color:var(--fog)}
.rlx-plate{display:inline-block;align-self:flex-start;background:var(--acc);color:#fff;
font:700 12px/1 "Inter";letter-spacing:.16em;text-transform:uppercase;padding:11px 15px}
.rlx-ink .rlx-plate{background:var(--acc-soft);color:var(--night)}
.rlx-mount{box-shadow:14px 14px 0 var(--acc)}
.rlx-olw{color:transparent;-webkit-text-stroke:2.5px var(--acc-soft)}
@supports not (-webkit-text-stroke:1px red){.rlx-olw{color:var(--acc-soft)}}
/* ==== обложка ==== */
.rlx-brand{display:flex;gap:18px;align-items:center}
.rlx-mark{width:62px;height:62px;border:3px solid var(--paper);display:grid;place-items:center;
font:900 24px/1 "Fira Sans Condensed","Inter",sans-serif;color:var(--paper);flex:none}
.rlx-bname{font:900 30px/1 "Fira Sans Condensed","Inter",sans-serif;letter-spacing:.04em;color:var(--paper)}
.rlx-btag{font:700 11px/1.4 "Inter";letter-spacing:.28em;text-transform:uppercase;color:var(--acc-soft);margin-top:7px}
.rlx-ttlblk{display:flex;flex-direction:column;gap:18px;align-items:flex-start}
.rlx-ttl{font-family:"Fira Sans Condensed","Inter",sans-serif;font-weight:900;text-transform:uppercase;
font-size:clamp(52px,7.4vw,104px);line-height:.94;letter-spacing:.005em;color:var(--paper)}
.rlx-intro{display:flex;flex-direction:column;gap:10px;max-width:640px}
.rlx-lead-w{font:600 18px/1.45 "Inter";color:var(--paper)}
.rlx-tx-w{font:400 14.5px/1.6 "Inter";color:var(--fog)}
.rlx-meta{align-self:end;justify-self:end;font:700 11.5px/1.5 "Inter";letter-spacing:.24em;text-transform:uppercase;
color:var(--acc-soft);border-top:2px solid rgba(245,240,230,.35);padding-top:14px;max-width:340px}
/* ==== полнополосная пластина обложки ==== */
.rlx-cframe{position:relative;background:var(--acc);padding:13px;box-shadow:0 26px 64px rgba(0,0,0,.38)}
.rlx-ckick{position:absolute;top:-16px;left:24px;background:var(--paper);color:var(--ink)}
/* ==== бизнес-врезка: горизонтальная панель, кадр — половина панели ==== */
.rlx-biz{background:var(--ink);color:var(--paper);padding:20px;display:grid;
grid-template-columns:56fr 44fr;gap:26px;align-items:center}
.rlx-bizcol{display:flex;flex-direction:column;gap:12px;align-items:flex-start}
.rlx-biz .rlx-kick-inv{align-self:flex-start}
.rlx-biznum{font-family:"Fira Sans Condensed","Inter",sans-serif;font-weight:900;
font-size:clamp(26px,3.4vw,48px);line-height:1;letter-spacing:-.01em;color:var(--acc-soft)}
.rlx-biztx{font:500 13.5px/1.5 "Inter";color:var(--fog)}
/* ==== финал ==== */
.rlx-sign{display:inline-block;align-self:flex-start;border:2px solid var(--acc-soft);color:var(--paper);
font:700 12px/1 "Inter";letter-spacing:.26em;text-transform:uppercase;padding:11px 16px}
.rlx-fin{font-family:"Fira Sans Condensed","Inter",sans-serif;font-weight:900;text-transform:uppercase;
font-size:clamp(50px,8.2vw,116px);line-height:.95;color:var(--paper)}
.rlx-idx{display:grid;grid-template-columns:1fr 1fr;column-gap:56px;row-gap:0;width:100%}
.rlx-ix{display:flex;gap:16px;align-items:baseline;
border-bottom:1px solid rgba(245,240,230,.22);padding:17px 2px}
.rlx-ix:nth-child(even){border-left:1px solid rgba(245,240,230,.16);padding-left:56px;margin-left:-56px}
.rlx-ixn{font:900 19px/1.2 "Fira Sans Condensed","Inter",sans-serif;color:var(--och);min-width:26px;flex:none}
.rlx-ixt{font:600 14.5px/1.45 "Inter";color:var(--paper)}
.rlx-colo{display:flex;justify-content:space-between;align-items:center;gap:20px;
border-top:2px solid rgba(245,240,230,.35);padding-top:18px;
font:700 11.5px/1.5 "Inter";letter-spacing:.2em;text-transform:uppercase;color:var(--fog)}
.rlx-mark-s{width:40px;height:40px;background:var(--paper);color:var(--ink);display:grid;place-items:center;
font:900 15px/1 "Fira Sans Condensed","Inter",sans-serif;flex:none}
/* ==== сцена обложки: марка, титул, полнополосный кадр, нижний ряд ==== */
#b1 .rlx-main{padding:40px 52px 46px 42px;gap:26px}
#b1 .rlx-row.r-cover-foot{grid-template-columns:1fr auto;align-items:end;gap:54px}
/* ==== сцена финала: типографика заполняет полосу ==== */
#b6 .rlx-main{padding:48px 52px 40px 46px;gap:30px}
/* ==== навигация выпуска (система rlx, без изменений с раунда 3) ==== */
.rlx-nav{position:fixed;top:50%;left:calc(50% + 604px);transform:translateY(-50%);
display:flex;flex-direction:column;gap:10px;z-index:60}
.rlx-btn{width:52px;height:52px;background:var(--acc);border:none;padding:0;cursor:pointer;
display:grid;place-items:center;color:#fff;transition:background .18s ease,transform .18s ease}
.rlx-btn svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:2.4;
stroke-linecap:round;stroke-linejoin:round}
.rlx-btn:hover{background:var(--acc-deep)}
#rlxPrev:hover{transform:translateY(-3px)}
#rlxNext:hover{transform:translateY(3px)}
.rlx-btn:active{transform:scale(.93)}
.rlx-btn:focus-visible{outline:3px solid #fff;outline-offset:2px}
.rlx-flag{position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(18px);
background:var(--paper);color:var(--ink);font:700 12.5px/1 "Inter";letter-spacing:.2em;text-transform:uppercase;
padding:13px 22px;opacity:0;pointer-events:none;z-index:70}
.rlx-flag.on{animation:rlxFlag 1.75s cubic-bezier(.2,.7,.2,1) both}
html:not(.sfn-js) .rlx-nav,html:not(.sfn-js) .rlx-flag{display:none}
/* ==== моушен выпуска: keyframes и логика rlx (без изменений с раунда 3) ==== */
@keyframes rlxBandIn{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
@keyframes rlxBandOut{from{opacity:1;transform:translateY(0)}to{opacity:0;transform:translateY(-16px)}}
@keyframes rlxRise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes rlxFlag{0%{opacity:0;transform:translateX(-50%) translateY(18px)}
12%{opacity:1;transform:translateX(-50%) translateY(0)}
80%{opacity:1;transform:translateX(-50%) translateY(0)}
100%{opacity:0;transform:translateX(-50%) translateY(-10px)}}
@keyframes rlxDraw{from{transform:scaleX(0)}to{transform:scaleX(1)}}
html.sfn-js .rlx-deck{display:grid;grid-template-columns:1fr}
html.sfn-js .rlx-band{grid-area:1/1;margin-bottom:0}
html.sfn-js .rlx-band.st-off{display:none}
html.sfn-js .rlx-band.st-in{animation:rlxBandIn .62s cubic-bezier(.16,.84,.24,1) both}
html.sfn-js .rlx-band.st-out{animation:rlxBandOut .48s cubic-bezier(.45,.05,.55,.95) both}
html.sfn-js .rlx-rv{opacity:0}
html.sfn-js .st-live .rlx-rv{animation:rlxRise .55s cubic-bezier(.16,.84,.24,1) both}
html.sfn-js .st-live .rlx-rv[data-r="2"]{animation-delay:.07s}
html.sfn-js .st-live .rlx-rv[data-r="3"]{animation-delay:.14s}
html.sfn-js .st-live .rlx-rv[data-r="4"]{animation-delay:.21s}
html.sfn-js .st-live .rlx-rv[data-r="5"]{animation-delay:.28s}
html.sfn-js .st-live .rlx-rv[data-r="6"]{animation-delay:.35s}
html.sfn-js .st-live .rlx-rule{animation:rlxDraw .7s .1s cubic-bezier(.16,.84,.24,1) both}
/* ==== узкие экраны: коридор под навигацию справа ==== */
@media (max-width:1339px){
html.sfn-js body{padding:0 70px 80px 10px}
.rlx-nav{left:auto;right:10px}
}
/* ==== мобильный сценарий: корешок — верхняя планка, полосы — стек ==== */
@media (max-width:760px){
html.sfn-js body{padding:0 58px 70px 6px}
.rlx-nav{right:6px;gap:8px}
.rlx-btn{width:46px;height:46px}
.rlx-btn svg{width:21px;height:21px}
.rlx-band{grid-template-columns:1fr;grid-template-areas:"spine" "main"}
.rlx-spine{flex-direction:row;justify-content:space-between;align-items:center;padding:11px 16px;gap:12px}
.rlx-spine span{writing-mode:horizontal-tb;transform:none;letter-spacing:.26em;font-size:10px}
.rlx-spine b{width:30px;height:30px;font-size:12px}
.rlx-main{padding:26px 20px 30px;gap:22px;justify-content:flex-start}
.rlx-row.r-55-45,.rlx-row.r-45-55,.rlx-row.r-58-42,.rlx-row.r-42-58,.rlx-row.r-46-54,
.rlx-row.r-54-46,.rlx-row.r-62-38,.rlx-row.r-38-62,.rlx-row.r-66-34,.rlx-row.r-50-50,
.rlx-row.r-1,#b1 .rlx-row.r-cover-foot{grid-template-columns:1fr}
.rlx-biz{grid-template-columns:1fr;gap:16px}
.rlx-cframe{padding:10px}
.rlx-ckick{top:-14px;left:18px}
.rlx-mount{box-shadow:9px 9px 0 var(--acc)}
.rlx-idx{grid-template-columns:1fr}
.rlx-ix:nth-child(even){border-left:none;padding-left:2px;margin-left:0}
.rlx-meta{max-width:none;align-self:start;justify-self:start}
.rlx-ttl{font-size:clamp(38px,10.5vw,60px)}
.rlx-fin{font-size:clamp(40px,11vw,60px)}
.rlx-h2{font-size:clamp(30px,7.8vw,44px)}
.rlx-biznum{font-size:clamp(22px,6.4vw,30px)}
}
/* ==== печать: статика, все полосы в потоке ==== */
@media print{
body{background:#fff;padding:0}
.rlx-nav,.rlx-flag{display:none!important}
*{animation:none!important;transition:none!important}
html.sfn-js .rlx-deck{display:block}
html.sfn-js .rlx-band.st-off{display:grid}
html.sfn-js .rlx-rv{opacity:1}
.rlx-band{box-shadow:none;margin:0 auto;page-break-after:always;min-height:0}
}
"""

# ============================== БЛОКИ ==============================
SPINE = '<div class="rlx-spine" aria-hidden="true"><span>San Fierro News · 09.10.2026</span><b>SFN</b></div>'

def fig(mid, alt, cls='', r=None, plate=None, kick=None):
    rv = ' rlx-rv' if r else ''
    dr = ' data-r="%d"' % r if r else ''
    cap = '<figcaption class="rlx-plate">%s</figcaption>' % plate if plate else ''
    kp = '<p class="rlx-kick rlx-ckick">%s</p>' % kick if kick else ''
    return '<figure class="rlx-fig%s%s"%s>%s<img src="%s" alt="%s">%s</figure>' % (
        (' ' + cls) if cls else '', rv, dr, kp, '@@%s@@' % mid.upper(), alt, cap)

def note(h3, lead, tx, r=None):
    rv = ' rlx-rv' if r else ''
    dr = ' data-r="%d"' % r if r else ''
    leadh = '<p class="rlx-lead">%s</p>' % lead if lead else ''
    paras = ''.join('<p class="rlx-tx">%s</p>' % t.strip() for t in tx.split('\n\n'))
    return '<div class="rlx-note%s"%s><h3 class="rlx-h3">%s</h3>%s%s</div>' % (
        rv, dr, h3, leadh, paras)

# ---- ПОЛОСА 1 · ОБЛОЖКА: марка, титул, полнополосный кадр, нижний ряд ----
B1 = """
<section class="rlx-band rlx-graph" id="b1">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-row r-1"><div class="rlx-brand rlx-rv" data-r="1"><b class="rlx-mark">SFN</b>
<div><p class="rlx-bname">San Fierro News</p><p class="rlx-btag">Ежедневный выпуск · Лос-Сантос / Сан-Фиерро</p></div></div></div>
<div class="rlx-row r-1"><div class="rlx-ttlblk rlx-rv" data-r="2">
<h1 class="rlx-ttl">Вертолёт —<br>посреди <span class="rlx-olw">тоннеля</span></h1></div></div>
<div class="rlx-row r-1">""" + fig('m03', 'Вертолёт в тоннеле между Лос-Сантосом и Сан-Фиерро', 'rlx-cframe', 3,
          kick='Главный кадр дня') + """</div>
<div class="rlx-row r-cover-foot">
<div class="rlx-intro rlx-rv" data-r="4">
<p class="rlx-lead-w">Воздушное судно обнаружили прямо внутри тоннеля между Лос-Сантосом и Сан-Фиерро.</p>
<p class="rlx-tx-w">Как борт оказался внутри тоннеля, ещё предстоит объяснить: машина стоит посреди проезжей части, под сводами перегона.</p></div>
<p class="rlx-meta rlx-rv" data-r="5">Выпуск 09.10.2026 · 12 событий · Лос-Сантос · Сан-Фиерро · Лас-Вентурас</p>
</div>
</div>
</section>"""

# ---- ПОЛОСА 2 · ТРАССЫ: пара материалов в равных колонках, затем герой с ставкой рядом ----
B2 = """
<section class="rlx-band" id="b2">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-row r-1"><div class="rlx-head rlx-rv" data-r="1">
<p class="rlx-kick">Блок 01 · Трассы</p>
<h2 class="rlx-h2">Тяжёлая сводка <b class="rlx-rd">трасс</b></h2>
<p class="rlx-sub">Три происшествия на дорогах — от Лас-Вентураса до Лос-Сантоса.</p>
<div class="rlx-rule"></div></div></div>
<div class="rlx-row r-50-50">
<div class="rlx-item rlx-rv" data-r="2">
""" + fig('m01', 'Массовое убийство на трассе Лас-Вентураса: на месте работают службы', '', 2) + """
""" + note('Четверо погибших на трассе Лас-Вентураса', 'Среди жертв — офицер полиции.',
           'Массовое убийство унесло четыре жизни — самое тяжёлое происшествие дорожной сводки выпуска.', 3) + """
</div>
<div class="rlx-item rlx-rv" data-r="4">
""" + fig('m05', 'Последствия расправы на трассе между Лас-Вентурасом и Сан-Фиерро', '', 4) + """
""" + note('Расправа на перегоне Лас-Вентурас — Сан-Фиерро', 'Двое погибших.',
           'Трагедия на перегоне Лас-Вентурас — Сан-Фиерро продолжила тяжёлую дорожную сводку дня.', 5) + """
</div>
</div>
<div class="rlx-row r-62-38">
""" + fig('m06', 'Двойная трагедия на дороге в Лос-Сантосе', '', 6) + """
<div class="rlx-item rlx-mid rlx-rv" data-r="6">
<div class="rlx-rule"></div>
""" + note('Два тела на дороге в Лос-Сантосе', 'Двойная трагедия.',
           'Третий адрес дорожной сводки дня: тела двоих погибших найдены прямо на дороге.', 6) + """
</div>
</div>
</div>
</section>"""

# ---- ПОЛОСА 3 · ТОННЕЛЬ: два крупных кадра навстречу друг другу ----
B3 = """
<section class="rlx-band rlx-ink" id="b3">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-row r-1"><div class="rlx-head rlx-rv" data-r="1">
<p class="rlx-kick">Блок 02 · Тоннель</p>
<h2 class="rlx-h2">Узел между <b class="rlx-rs">двумя городами</b></h2>
<p class="rlx-sub">Один тоннель — и два разных происшествия.</p>
<div class="rlx-rule"></div></div></div>
<div class="rlx-row r-62-38">
<div class="rlx-item rlx-rv" data-r="2">
""" + fig('m02', 'Тело мужчины обнаружено в тоннеле между Лос-Сантосом и Сан-Фиерро', '', 2,
          plate='Тело мужчины · есть задержанный') + """
</div>
<div class="rlx-item rlx-mid rlx-rv" data-r="3">
<div class="rlx-note"><h3 class="rlx-h3">Погибший в тоннеле</h3>
<p class="rlx-lead">Тоннель между Лос-Сантосом и Сан-Фиерро.</p>
<p class="rlx-tx">В тоннеле обнаружено тело мужчины; по делу проходит задержанный — единственная трагедия выпуска с подозреваемым.</p></div>
<div class="rlx-rule"></div>
</div>
</div>
<div class="rlx-row r-38-62">
<div class="rlx-item rlx-mid rlx-rv" data-r="5">
<div class="rlx-rule"></div>
""" + note('Офицер без сознания', 'Второй эпизод того же перегона.',
           'Сотрудника полиции нашли в тоннеле без сознания; перегон между городами дал выпуску три сюжета из двенадцати.', 5) + """
</div>
<div class="rlx-item rlx-rv" data-r="4">
""" + fig('m04', 'Сотрудник полиции без сознания в тоннеле', '', 4) + """
</div>
</div>
</div>
</section>"""

# ---- ПОЛОСА 4 · ГОРОД: герой-кадр со ставкой, затем пара равных материалов ----
B4 = """
<section class="rlx-band rlx-porc" id="b4">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-row r-1"><div class="rlx-head rlx-rv" data-r="1">
<p class="rlx-kick">Блок 03 · Город</p>
<h2 class="rlx-h2">От перевёрнутой фуры — до <b class="rlx-rd">упавшего самолёта</b></h2>
<p class="rlx-sub">Городская сводка: Сан-Фиерро и Лос-Сантос.</p>
<div class="rlx-rule"></div></div></div>
<div class="rlx-row r-58-42">
<div class="rlx-item rlx-mid rlx-rv" data-r="2">
""" + fig('m12', 'Самолёт упал в Сан-Фиерро, на месте работают экстренные службы', 'rlx-mount', 2) + """
</div>
<div class="rlx-item rlx-mid rlx-rv" data-r="3">
""" + note('Самолёт рухнул в Сан-Фиерро', 'На месте работают экстренные службы.',
           'Журналисты San Fierro News оказались у места крушения первыми и начали фиксировать происходящее с первых минут после падения борта.\n\n'
           'Через несколько минут к месту подоспели сотрудники полиции и медицинской службы; городские службы включались в работу на глазах у корреспондентов, и редакция передавала картину происходящего непосредственно с места событий.\n\n'
           'Для новостного издания возможность оказаться на месте событий раньше других — не престиж, а ремесло: первые кадры и первые проверенные факты позволяют читателю увидеть происшедшее таким, каким его застали, без пересказов и домыслов.', 3) + """
<div class="rlx-rule"></div>
</div>
</div>
<div class="rlx-row r-50-50">
<div class="rlx-item rlx-rv" data-r="4">
""" + fig('m07', 'Перевёрнутая фура на перекрёстке в Сан-Фиерро', 'rlx-mount', 4) + """
""" + note('Фура легла на бок', 'Перекрёсток парализован.',
           'Грузовик опрокинулся на пересечении улиц, и городское движение вокруг замерло.', 5) + """
</div>
<div class="rlx-item rlx-rv" data-r="6">
""" + fig('m10', 'Скопление полиции у участка в Лос-Сантосе, рядом машина редакции LSN', 'rlx-mount', 6) + """
""" + note('Скопление у полицейского участка', 'Лос-Сантос.',
           'Силы департамента стянуты к участку единым массивом; рядом замечен автомобиль редакции LSN.', 6) + """
</div>
</div>
</div>
</section>"""

# ---- ПОЛОСА 5 · БЕРЕГ И БИЗНЕС: пара равных кадров, затем деловая панель во всю ширину ----
B5 = """
<section class="rlx-band" id="b5">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-row r-1"><div class="rlx-head rlx-rv" data-r="1">
<p class="rlx-kick">Блок 04 · Берег и бизнес</p>
<h2 class="rlx-h2">Пляж перекрыт, лот — <b class="rlx-rd">на миллиарды</b></h2>
<div class="rlx-rule"></div></div></div>
<div class="rlx-row r-50-50">
<div class="rlx-item rlx-rv" data-r="2">
""" + fig('m08', 'Пирс на пляже Санта-Мария перекрыт, на месте полиция и скорая', '', 2,
          plate='Пирс перекрыт · полиция и скорая') + """
""" + note('Санта-Мария: берег закрыт', 'Доступ на пирс перекрыт.',
           'Полиция и скорая помощь вышли на пляж Санта-Мария и работают у самой воды.', 3) + """
</div>
<div class="rlx-item rlx-rv" data-r="4">
""" + fig('m09', 'Тело женщины обнаружено у пляжа Санта-Мария в Лос-Сантосе', '', 4) + """
""" + note('Тело у пляжа', 'Лос-Сантос.',
           'У пляжа Санта-Мария обнаружено тело женщины — второй тревожный адрес берега за день.', 5) + """
</div>
</div>
<div class="rlx-row r-1"><aside class="rlx-biz rlx-rv" data-r="6">
""" + fig('m11', 'Продажа бизнеса Carsharing Guaranteed в мэрии Лос-Сантоса') + """
<div class="rlx-bizcol">
<p class="rlx-kick rlx-kick-inv">Деловая строка</p>
<p class="rlx-biznum">$1.800.000.000</p>
<p class="rlx-biztx">Carsharing Guaranteed выставлен на продажу в мэрии Лос-Сантоса. Заявленная цена — рекордная.</p>
</div>
</aside></div>
</div>
</section>"""

# ---- ПОЛОСА 6 · ФИНАЛ: типографика заполняет полосу ----
IDX = [
 'Трасса Лас-Вентураса — четверо погибших, среди них офицер полиции',
 'Перегон Лас-Вентурас — Сан-Фиерро — двое погибших',
 'Дорога в Лос-Сантосе — два тела на месте происшествия',
 'Тоннель между городами — тело мужчины, есть задержанный',
 'Тоннель между городами — сотрудник полиции без сознания',
 'Тоннель между городами — вертолёт, главный кадр выпуска',
 'Сан-Фиерро — упал самолёт, работают экстренные службы',
 'Сан-Фиерро — перевёрнутая фура, перекрёсток парализован',
 'Лос-Сантос — скопление полиции у участка, рядом машина LSN',
 'Санта-Мария — пирс перекрыт, на месте полиция и скорая',
 'Санта-Мария — тело женщины у пляжа',
 'Мэрия Лос-Сантоса — лот Carsharing Guaranteed за $1.800.000.000',
]
IDXH = ''.join('<div class="rlx-ix"><span class="rlx-ixn">%02d</span><span class="rlx-ixt">%s</span></div>'
               % (n + 1, t) for n, t in enumerate(IDX))

B6 = """
<section class="rlx-band rlx-graph" id="b6">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-row r-1"><p class="rlx-sign rlx-rv" data-r="1">San Fierro News · сводная лента дня</p></div>
<div class="rlx-row r-1"><h2 class="rlx-fin rlx-rv" data-r="2">Линия <span class="rlx-olw">закрыта</span></h2></div>
<div class="rlx-row r-1"><p class="rlx-sub rlx-rv" data-r="3">Двенадцать событий выпуска — одним списком: от трасс Лас-Вентураса до мэрии Лос-Сантоса.</p></div>
<div class="rlx-row r-1"><div class="rlx-idx rlx-rv" data-r="4">""" + IDXH + """</div></div>
<div class="rlx-row r-1"><div class="rlx-colo rlx-rv" data-r="5"><span>San Fierro News — ежедневная редакция</span>
<span>Выпуск 09.10.2026</span><b class="rlx-mark-s">SFN</b></div></div>
</div>
</section>"""

NAV = """
<nav class="rlx-nav" id="rlxNav" aria-label="Навигация по полосам выпуска">
<button class="rlx-btn" id="rlxPrev" type="button" aria-label="Предыдущая полоса"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 14l7-7 7 7"/></svg></button>
<button class="rlx-btn" id="rlxNext" type="button" aria-label="Следующая полоса"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 10l7 7 7-7"/></svg></button>
</nav>
<div class="rlx-flag" id="rlxFlag" role="status"></div>"""

# ============================== JS (байт-в-байт из раундов 3–4) ==============================
JS = """<script>
/* SFN · 2026 · terra-ivory: навигация и моушен выпуска — самостоятельная система rlx,
   собранная в раунде 3; в раундах 4 и 5 не меняется (правятся только палитра, обложка и композиция). */
(function(){
  var root=document.documentElement;
  root.classList.add('sfn-js');
  var deck=document.getElementById('rlxDeck');
  if(!deck)return;
  var bands=deck.querySelectorAll('.rlx-band');
  var flag=document.getElementById('rlxFlag');
  var bPrev=document.getElementById('rlxPrev');
  var bNext=document.getElementById('rlxNext');
  if(bands.length!==6||!flag||!bPrev||!bNext)return;
  var cur=0,busy=false,flagTimer=0;
  for(var i=1;i<bands.length;i++){bands[i].classList.add('st-off');}
  bands[0].classList.add('st-live');
  function mark(n){
    flag.textContent='\\u041f\\u041e\\u041b\\u041e\\u0421\\u0410 '+(n+1)+' / '+bands.length;
    flag.classList.remove('on');
    void flag.offsetWidth;
    flag.classList.add('on');
    clearTimeout(flagTimer);
    flagTimer=setTimeout(function(){flag.classList.remove('on');},1780);
  }
  function glide(to){
    var from=window.pageYOffset,dist=to-from,t0=null;
    if(Math.abs(dist)<2)return;
    function step(ts){
      if(t0===null)t0=ts;
      var p=Math.min(1,(ts-t0)/480),e=1-Math.pow(1-p,3);
      window.scrollTo(0,from+dist*e);
      if(p<1)requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  function go(step){
    if(busy)return;
    var to=cur+step;
    if(to<0||to>=bands.length)return;
    busy=true;
    var outB=bands[cur],inB=bands[to];
    outB.classList.add('st-out');
    inB.classList.remove('st-off');
    void inB.offsetWidth;
    inB.classList.add('st-in');
    inB.classList.add('st-live');
    glide(deck.getBoundingClientRect().top+window.pageYOffset-14);
    setTimeout(function(){
      outB.classList.remove('st-out');
      outB.classList.remove('st-live');
      outB.classList.add('st-off');
      inB.classList.remove('st-in');
      cur=to;busy=false;mark(to);
    },660);
  }
  bPrev.addEventListener('click',function(){go(-1);});
  bNext.addEventListener('click',function(){go(1);});
  document.addEventListener('keydown',function(e){
    if(e.metaKey||e.ctrlKey||e.altKey)return;
    if(e.key==='ArrowRight'||e.key==='ArrowDown'||e.key==='PageDown'){e.preventDefault();go(1);}
    else if(e.key==='ArrowLeft'||e.key==='ArrowUp'||e.key==='PageUp'){e.preventDefault();go(-1);}
  });
  setTimeout(function(){mark(0);},420);
})();
</script>"""

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>San Fierro News — ежедневный выпуск от 09.10.2026</title>
<meta name="description" content="Ежедневный выпуск San Fierro News от 09.10.2026: двенадцать событий дня — трассы Лас-Вентураса, тоннель между городами, происшествия Сан-Фиерро и Лос-Сантоса, пляж Санта-Мария и рекордный деловой лот.">
<style>""" + CSS + """</style>
</head>
<body>
<div class="rlx-deck" id="rlxDeck">""" + B1 + B2 + B3 + B4 + B5 + B6 + """
</div>""" + NAV + """
""" + JS + """
""" + COPY + """
""" + MARKER + """
</body>
</html>
"""

for k, uri in DATA.items():
    tok = '@@%s@@' % k.upper()
    assert HTML.count(tok) == 1, (tok, HTML.count(tok))
    HTML = HTML.replace(tok, uri)

# ============================== САМОПРОВЕРКА ==============================
FORBID = ['pageEnter', 'pageExit', 'pageIndicator', 'showPageIndicator', 'sfn-rise', 'sfn-fade',
          'navbtn', 'pages-stage', 'page-indicator', 'sheetnav', 'navPrev', 'navNext', 'is-off',
          'js-nav', 'cubic-bezier(.22,.61,.36,1)', 'calc(50% - 640px)', 'calc(50% + 640px)',
          'SFN-DESIGN-031', 'SFN-DESIGN-032', 'SFN-DESIGN-033', 'class="sheet', 'class="grid"', 'class="m"', 'class="ph',
          'th-red', 'th-ink', 'th-blush', 'Bricolage', 'Source Serif', 'Space Mono', 'prefers-reduced-motion',
          'rlx-w72', 'rlx-w76', 'rlx-w78', 'object-fit']
for f in FORBID:
    assert f not in HTML, 'запрещённый фрагмент: %s' % f
vis = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', HTML, flags=re.S)
vis = re.sub(r'base64,[A-Za-z0-9+/=]+', '', vis)
vis = re.sub(r'<[^>]+>', ' ', vis)
assert not re.search(r'Evolve\s+(Role\s*Play|RP)', vis, re.I)
assert not re.search(r'Saint[- ]Louis', vis, re.I)
assert not re.search(r'\bчат[а-я]*\b', vis, re.I)
assert '2504' not in vis
assert not re.search(r'[A-Za-zА-Яа-я]_[A-Za-zА-Яа-я]', vis)
# каждая фотография ровно один раз, байт-в-байт
for k, (fn, mime) in PH.items():
    raw = open(os.path.join(UP, fn), 'rb').read()
    tok = 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode())
    assert HTML.count(tok) == 1, k
# well-formedness
from html.parser import HTMLParser
VOID = {'meta', 'img', 'br', 'hr', 'link', 'input', 'path', 'source'}
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.st = []
    def handle_starttag(self, tag, attrs):
        if tag not in VOID: self.st.append(tag)
    def handle_endtag(self, tag):
        if tag in VOID: return
        assert self.st and self.st[-1] == tag, (self.st[-3:], tag)
        self.st.pop()
p = P(); p.feed(HTML); p.close()
assert not p.st, p.st

os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(HTML)
print('OK ->', OUT)
print('размер: %.2f MB · полос: 6 · фото: 12 · штамп: SFN-DESIGN-034: full-plate'
      % (len(HTML.encode('utf-8')) / 1048576))
