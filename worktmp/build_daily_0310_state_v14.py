#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN: сборщик выпуска 03.10.2026 (v14, «Единая сетка дня» — цельная концепция).

Архитектура (после аудита и полной очистки, бриф главреда от 04.10.2026):
— ОДНА HTML-структура: материал = <article class="m t-ТИП"> с одним набором
  детей (nn → заголовок → лид → текст → кадр); никаких inline-стилей;
— ОДНА система переменных: единственный :root;
— ОДНА система композиции: страница = 12-колоночная сетка с одним gutter;
  у каждой полосы СВОЙ сценарий раскладки (grid-template-areas), материалы
  получают только место (grid-area), но не индивидуальную композицию;
— ОДИН набор стилей на ТИП материала: t-lead, t-side-a, t-side-b, t-wide,
  t-split, t-finale + типографические элементы (stand, txt, cols2/3, stat);
— номера материалов: номерная строка (Anton-цифра + рубрика на базовой
  линейке, снизу линейка-якорь) — номер физически принадлежит материалу;
  кегль цифры задаётся типом материала (контраст масштаба внутри системы);
— пустота намеренная: тониrowанные ячейки-паузы .void с одной служебной
  строкой (на П3 — дословный вынос из материала 08, на П4 — конец хроники);
— фото — композиционные блоки: полноширинные регистры с чёрной плашкой-
  подписью либо врезки в долю блока, без рамок-«карточек»;
— внешний фон и оболочка листа НЕ ТРОНУТЫ; текст и 12 кадров — дословно;
— главный заголовок уменьшен ещё на ~21% (38→30px) при сохранении веса
  (Oswald 700, кап, вторая строка охрой, толстая линейка-якорь);
— номер борта 2504 удалён из всех полей (правка главреда, замены утверждены).
Содержание импортируется из сборщика v4 (канон текстов) без правок, кроме
утверждённой замены 2504. Фото: width:100% + height:auto, кадры целиком.
Навигация полос (day-navglide, бриф главреда 04.10.2026): фиксированные стрелки
← → вплотную к газете — в 24px от краёв листа, по центру видимой области (на
узких экранах — компактный блок у верха экрана), счётчик N / 4; переход —
одновременный кроссфейд: уходящая полоса исчезает слоем поверх сцены, входящая
появляется (opacity 0→1 + translateY(±14px→0), 600мс, cubic-bezier(.22,.61,.36,1)),
прокрутка к началу новой полосы — плавная, той же кривой; без 3D-перелистывания.
Выход: anna-malboro/daily-03-10-2026.html (очередь подшивки).
Запуск из корня:  python3 worktmp/build_daily_0310_state_v14.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(ROOT, 'worktmp', 'build_daily_0310_state_v4.py')
OUT = os.path.join(ROOT, 'anna-malboro', 'daily-03-10-2026.html')

src = open(V4, encoding='utf-8').read()
src = src.replace("OUT = os.path.join(ROOT, 'anna-malboro', 'daily-03-10-2026.html')",
                  "OUT = os.devnull")
ns = {'__name__': 'sfn_v4_data', '__file__': V4}
exec(compile(src, V4, 'exec'), ns)
IMG, A = ns['IMG'], ns['A']

# ---- правка главреда: номер борта 2504 удалён полностью ----
REPL = [
    ('человек с предметом, похожим на оружие', 'сотрудник полиции с предметом, похожим на оружие'),
    ('у двери седана — человек с предметом, похожим на оружие',
     'у двери седана — сотрудник полиции с предметом, похожим на оружие'),
    ('от ярких кроссоверов до лимузина у крыла', 'от ярких кроссоверов до фургона у крыла'),
    ('Борт 2504 и автомобиль', 'Патрульный автомобиль и машина'),
    ('Борт 2504 и легковушка', 'Патрульный автомобиль и легковушка'),
    ('Борт 2504:', 'Патрульный автомобиль:'),
    ('Патрульный борт 2504 остановил', 'Патрульный автомобиль остановил'),
]
for _a in A.values():
    for _f in ('k', 't', 's', 'cap', 'alt'):
        for _o, _n in REPL:
            _a[_f] = _a[_f].replace(_o, _n)
    _newp = []
    for _pp in _a['p']:
        for _o, _n in REPL:
            _pp = _pp.replace(_o, _n)
        _newp.append(_pp)
    _a['p'] = _newp
for _key, _a in A.items():
    for _f in ('k', 't', 's', 'cap', 'alt'):
        assert '2504' not in _a[_f], f'2504 остался в {_key}.{_f}'
    for _pp in _a['p']:
        assert '2504' not in _pp, f'2504 остался в {_key}.p'

# ---- правка главреда (04.10.2026): рубрика материала 01 — обычная тематическая,
# как у всех материалов; «Главное сегодня» удалено, приоритет — только размером ----
assert A['fallen']['k'] == 'Главное сегодня · Лас-Вентурас', 'рубрика 01 неожиданно изменена'
A['fallen']['k'] = 'Происшествия · Лас-Вентурас'
for _key, _a in A.items():
    for _f in ('k', 't', 's', 'cap', 'alt'):
        assert 'Главное' not in _a[_f], f'«Главное» осталось в {_key}.{_f}'
    for _pp in _a['p']:
        assert 'Главное' not in _pp, f'«Главное» осталось в {_key}.p'

IDX = {'fallen': '01', 'crash': '02', 'gas': '03', 'kpp': '04', 'truck': '05', 'square': '06',
       'stop': '07', 'hwy': '08', 'dragons': '09', 'caligula': '10', 'heli': '11', 'yacht': '12'}

CSS = """/* SFN-DESIGN-029: day-navglide · 03.10.2026 */
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Oswald:wght@500;600;700&family=PT+Mono&family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
img{display:block;max-width:100%}
/* ==== ЕДИНСТВЕННАЯ система переменных ==== */
:root{--paper:#f2ede3;--ink:#1a1714;--ox:#9e2b25;--mut:#6d675c;--hair:#cfc7b4;
--tint:#e7dfcd;--gut:24px;--pad:46px}
/* ==== внешняя среда и оболочка: НЕ ТРОГАТЬ (байт-в-байт как до всех правок) ==== */
body{background:var(--paper);color:var(--ink);font-family:"PT Serif",Georgia,serif;
-webkit-font-size-adjust:100%;padding:0 0 60px}
.sheet{max-width:1120px;margin:0 auto 26px;background:var(--paper);padding:0 0 40px;
box-shadow:0 16px 40px rgba(20,24,28,.22);position:relative}
.sheet+.sheet{margin-top:34px}
/* ==== страница: 12 колонок, один gutter; сценарий полосы = grid-template-areas ==== */
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:16px 22px;
padding:20px var(--pad) 0}
/* размещение материалов по сценарию полосы (только место, без композиции) */
#p1 .grid{row-gap:12px;grid-template-areas:"a01 a01 a01 a01 a01 a01 a01 a01 a02 a02 a02 a02"
 "hs hs hs hs hs hs hs hs hs hs hs hs"
 "a03 a03 a03 a03 a03 a03 a03 a04 a04 a04 a04 a04"}
#p1 #a01{border-right:1px solid var(--hair);padding-right:var(--gut)}
#p1 #a02 h3{font-size:clamp(18px,2.05vw,26px);margin-bottom:9px}
#p1 #a02 .stand{margin-bottom:10px}
#p1 #a03{border-right:1px solid var(--hair);padding-right:var(--gut)}
#p1 #a04 .nmeta{display:none}
#p1 #a04{grid-template-areas:"n" "h" "ph" "s" "t" "e"}
.hsep{grid-area:hs;border-top:1px solid var(--hair)}
#p2 .grid{grid-template-areas:"kr kr kr kr kr kr kr kr kr kr kr kr"
 "a05 a05 a05 a05 a05 a05 a05 a05 a05 a05 a05 a05"
 "a06 a06 a06 a06 a06 a07 a07 a07 a07 a07 a07 a07"}
#p3 .grid{grid-template-areas:"a08 a08 a08 a08 a08 a08 a08 a08 a08 a08 a08 a08"
 "a09 a09 a09 a09 a09 a09 a09 a10 a10 a10 a10 a10"}
#p4 .grid{grid-template-areas:"a11 a11 a11 a11 a11 a11 a11 a11 a11 a11 a11 a11"
 "a12 a12 a12 a12 a12 a12 a12 a12 a12 a12 a12 a12"}
#a01{grid-area:a01}#a02{grid-area:a02}#a03{grid-area:a03}#a04{grid-area:a04}
#a05{grid-area:a05}#a06{grid-area:a06}#a07{grid-area:a07}#a08{grid-area:a08}
#a09{grid-area:a09}#a10{grid-area:a10}#a11{grid-area:a11}#a12{grid-area:a12}
/* ==== материал: общая анатомия ==== */
.m{display:grid;align-content:start}
.m .nn{grid-area:n;display:flex;align-items:baseline;gap:14px;
border-bottom:1px solid var(--hair);padding-bottom:7px;margin-bottom:10px}
.m .num{font-family:Anton,sans-serif;font-weight:400;line-height:.84;color:var(--ink);
font-size:38px;letter-spacing:.01em}
.m .k{font-family:"PT Mono",monospace;font-weight:700;font-size:9.5px;letter-spacing:.24em;
text-transform:uppercase;color:var(--ox)}
.m .nmeta{margin-left:auto;align-self:center;font-family:"PT Mono",monospace;font-weight:700;
font-size:8.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--mut)}
.m .end{grid-area:e;display:flex;align-items:center;gap:10px;margin-top:12px;align-self:end}
.m .end::before{content:"";width:6px;height:6px;background:var(--ox);flex:0 0 6px}
.m .end::after{content:"";flex:1;border-top:1px solid var(--hair)}
.pagefoot{margin:18px var(--pad) 0;border-top:1px solid var(--hair);padding-top:10px;
display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;
font-family:"PT Mono",monospace;font-weight:700;font-size:8.5px;letter-spacing:.2em;
text-transform:uppercase;color:var(--mut)}
.m h1,.m h3{grid-area:h;font-family:Oswald,sans-serif;font-weight:700;text-transform:uppercase;
color:var(--ink);letter-spacing:.006em;line-height:1.08;margin-bottom:9px}
.m h3{font-size:clamp(16px,1.75vw,22px);font-weight:600;margin-bottom:7px}
.m .stand{grid-area:s;font:italic 400 13.5px/1.58 "PT Serif",serif;color:var(--mut);
border-left:2px solid var(--ox);padding-left:11px;margin-bottom:9px}
.m .txt,.m .cols2,.m .cols3{grid-area:t;align-self:start;margin-top:5px}
.m .stand{align-self:start}
.txt p{font:400 14px/1.68 "PT Serif",serif;margin:0 0 8px}
.cols2{columns:2;column-gap:26px}
.cols3{columns:3;column-gap:26px}
.cols2 p,.cols3 p{font:400 14px/1.68 "PT Serif",serif;margin:0 0 8px}
.m figure{grid-area:ph;margin:0}
.ph img{width:100%;height:auto;transition:filter .45s}
.ph:hover img{filter:contrast(1.04)}
figcaption{font-family:"PT Mono",monospace;font-size:9.5px;line-height:1.55;letter-spacing:.05em;
color:var(--mut);margin-top:5px}
.ph.bandcap figcaption{background:var(--ink);color:var(--paper);margin:0;padding:8px 12px;
font-weight:700;letter-spacing:.06em}
.stat{grid-area:x}
.stat b{display:block;font-family:Anton,sans-serif;font-weight:400;font-size:clamp(28px,3.3vw,44px);
line-height:.95;color:var(--ox);white-space:nowrap;margin:0 0 4px}
.stat small{display:block;font-family:"PT Mono",monospace;font-weight:700;font-size:8.5px;
letter-spacing:.2em;text-transform:uppercase;color:var(--mut);margin-bottom:10px}
/* ==== ТИПЫ материалов: один набор стилей на тип ==== */
.t-lead{grid-template-columns:70fr 30fr;column-gap:var(--gut);
grid-template-rows:auto auto auto auto 1fr;
grid-template-areas:"n n" "h h" "ph t" "s t" "e e"}
.t-lead .end{align-self:start}
.t-lead .nn{border-bottom:3px solid var(--ink)}
.t-lead .num{font-size:56px}
.t-lead h1{font-size:clamp(21px,2.3vw,30px)}
.t-lead h1 .ln1{color:var(--ink)}
.t-lead h1 .ln2{color:var(--ox)}
.t-side-a{grid-template-columns:1fr;grid-template-rows:auto auto auto auto auto 1fr;grid-template-areas:"n" "ph" "h" "s" "t" "e"}
.t-side-b{grid-template-columns:1fr;grid-template-rows:auto auto auto auto auto 1fr;grid-template-areas:"n" "h" "s" "t" "ph" "e"}
.t-wide{grid-template-columns:1fr;grid-template-rows:auto auto auto auto auto 1fr;grid-template-areas:"n" "h" "s" "ph" "t" "e"}
.t-wide .num{font-size:44px}
.t-wide h3{font-size:clamp(19px,2.3vw,30px)}
.t-split{grid-template-columns:1fr;
grid-template-areas:"n" "h" "s" "x" "ph" "t" "e"}
.t-split .num{font-size:38px}
.t-split .stat b{font-size:clamp(34px,4.2vw,58px)}
.t-showcase{grid-template-columns:35fr 65fr;column-gap:var(--gut);
grid-template-rows:auto auto auto auto auto 1fr;
grid-template-areas:"n n" "h h" "s s" "ph ph" "cap t" "e e"}
.t-showcase .num{font-size:44px}
.t-showcase figure{display:contents}
.t-showcase figure img{grid-area:ph;width:100%;height:auto}
.t-showcase figcaption{grid-area:cap;margin-top:9px}
.t-showcase .txt{grid-area:t}


.t-finale{grid-template-columns:8fr 16fr;column-gap:var(--gut);row-gap:14px;
grid-template-rows:auto auto auto 1fr auto;
grid-template-areas:"n n" "h ph" "s ph" "t ph" "e e"}
.t-finale .nn{border-bottom:3px solid var(--ink)}
.t-finale .num{font-size:44px}
.t-finale h3{font-size:clamp(18px,2.1vw,27px)}
#p4 #a12 .ph{margin-right:calc(-1 * var(--pad))}
/* ==== дословный вынос-якорь (функциональный элемент материала) ==== */
/* ==== редакционные инфоблоки из существующих фактов (единый набор) ==== */
.info{border-top:3px solid var(--ink);padding-top:10px;margin-top:14px}
.info .ih{font-family:Oswald,sans-serif;font-weight:600;font-size:12px;letter-spacing:.22em;
text-transform:uppercase;color:var(--ink);margin-bottom:8px}
.info .isub{font-family:"PT Mono",monospace;font-weight:700;font-size:8.5px;letter-spacing:.2em;
text-transform:uppercase;color:var(--mut);margin-bottom:8px}
.info .li{display:flex;gap:10px;align-items:baseline;font-family:"PT Mono",monospace;font-size:10px;
line-height:1.45;color:var(--ink)}
.info .li b{color:var(--ox);font-weight:700;flex:0 0 auto}
.info .li+.li{border-top:1px solid var(--hair);margin-top:6px;padding-top:6px}
.info.kr{grid-area:kr;display:grid;grid-template-columns:repeat(3,1fr);gap:0 26px;
border-top:3px solid var(--ink);padding:10px 0 12px;margin:2px 0 0}
.info.kr .ih{grid-column:1/-1;margin-bottom:8px}
.info.kr .li{border-top:0;margin-top:0;padding-top:0;border-left:1px solid var(--hair);
padding-left:12px}
.info.kr .li:first-of-type{border-left:0;padding-left:0}
/* ==== мебель страниц (единый набор) ==== */
.mtop{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;
padding:14px var(--pad) 10px;font-family:"PT Mono",monospace;font-weight:700;font-size:9.5px;
letter-spacing:.16em;text-transform:uppercase;color:var(--mut)}
.brand{padding:14px var(--pad) 4px;display:flex;align-items:baseline;gap:.22em;flex-wrap:wrap}
.b1,.b2{font-family:Anton,sans-serif;font-weight:400;text-transform:uppercase;line-height:.92;
letter-spacing:.004em;font-size:clamp(50px,8.2vw,104px)}
.b1{color:var(--ink)}
.b2{color:var(--ox)}
.mrule{margin:6px var(--pad) 0;border-top:4px solid var(--ink)}
.mmeta{margin:0 var(--pad);padding:9px 0 11px;border-bottom:1px solid var(--ink);display:flex;
flex-wrap:wrap;justify-content:space-between;gap:4px 22px;font-family:"PT Mono",monospace;
font-weight:700;font-size:9.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink)}
.mmeta b{color:var(--ox)}
.folio{display:flex;justify-content:space-between;align-items:baseline;gap:14px;flex-wrap:wrap;
padding:10px var(--pad);border-bottom:2px solid var(--ink);font-family:"PT Mono",monospace;
font-weight:700;font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink)}
.folio b{color:var(--ox)}
.folio .f3{background:var(--ink);color:var(--paper);padding:2px 8px}
.sect{display:flex;align-items:center;gap:18px;margin:0 0 clamp(4px,0.8vw,12px)}
.sect .snum{font-family:Anton,sans-serif;font-weight:400;font-size:clamp(40px,5.2vw,64px);
line-height:1;color:var(--ox);padding:6px 0 6px var(--pad)}
.sect h2{font-family:Oswald,sans-serif;font-weight:700;font-size:clamp(22px,3vw,38px);
text-transform:uppercase;letter-spacing:.04em;color:var(--ink)}
.sect .stail{flex:1;border-bottom:3px solid var(--ink);margin:0 20px 0 4px}
.sect .sdate{font-family:"PT Mono",monospace;font-weight:700;font-size:9px;letter-spacing:.2em;
text-transform:uppercase;color:var(--mut);padding-right:var(--pad)}
.pressline{margin:22px var(--pad) 0;background:var(--ink);color:var(--paper);padding:14px 20px;
display:flex;justify-content:space-between;align-items:baseline;gap:14px;flex-wrap:wrap}
.pressline .pl1{font-family:Oswald,sans-serif;font-weight:600;font-size:20px;
text-transform:uppercase;letter-spacing:.05em}
.pressline .pl1 i{font-style:normal;color:#e8897f}
.pressline .pl2{font-family:"PT Mono",monospace;font-weight:700;font-size:9px;letter-spacing:.2em;
text-transform:uppercase;color:#c9c2b4}
.colophon{margin:32px var(--pad) 0;border:1px solid var(--ink);padding:20px 24px;display:flex;
justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap;position:relative}
.colophon::before{content:"";position:absolute;top:-4px;left:-4px;width:8px;height:8px;
background:var(--ox);border-radius:50%}
.colophon .credits{font-family:"PT Mono",monospace;font-size:10.5px;letter-spacing:.06em;
color:var(--ink)}
.colophon .made{margin-top:7px;font-family:"PT Mono",monospace;font-size:9px;letter-spacing:.16em;
text-transform:uppercase;color:var(--mut)}
.backpill{display:inline-block;padding:10px 20px;border:1.5px solid var(--ox);color:var(--ox);
font-family:"PT Mono",monospace;font-weight:700;font-size:10.5px;letter-spacing:.12em;
text-transform:uppercase;text-decoration:none;transition:.2s;white-space:nowrap}
.backpill:hover{background:var(--ox);color:var(--paper)}
/* ==== SFN MOTION · day-motion: тонкий слой движения (только transform/opacity) ==== */
/* Появление при загрузке: полосы и материалы — opacity 0→1 + translateY(10px→0), 550–650мс,
   мягкий каскад задержек; заголовки выходят вместе со своим материалом с коротким сдвигом;
   красный декор (номера разделов, хвосты материалов, стат-блок, точка колофона) проявляется
   с небольшой задержкой. Ховер фото — очень лёгкое увеличение scale(1.02) внутри исходного
   контейнера (overflow:hidden): без изменения layout, пропорций, обрезки в покое и скролла.
   Размеры блоков, высота полос, тексты, цвета и геометрия не меняются. */
@keyframes sfn-rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes sfn-fade{from{opacity:0}to{opacity:1}}
.sheet{animation:sfn-rise .65s cubic-bezier(.22,.61,.36,1) both}
#p2.sheet{animation-delay:.06s}
#p3.sheet{animation-delay:.12s}
#p4.sheet{animation-delay:.18s}
.m,.info.kr{animation:sfn-rise .55s cubic-bezier(.22,.61,.36,1) both;animation-delay:var(--md,.12s)}
#a01,#a05,#a08,#a11{--md:.10s}
#a02,#a06,#a09{--md:.17s}
#a03,#a07,#a10,#a12{--md:.24s}
#a04{--md:.28s}
.info.kr{--md:.06s}
.m h1,.m h3{animation:sfn-fade .5s ease both;animation-delay:calc(var(--md,.12s) + .09s)}
.m .end,.m .stat{animation:sfn-fade .6s ease both;animation-delay:calc(var(--md,.12s) + .16s)}
.sect{animation:sfn-fade .6s ease both;animation-delay:.05s}
.colophon{animation:sfn-fade .6s ease both;animation-delay:.2s}
.ph{overflow:hidden}
.ph img{transition:filter .45s,transform .35s ease}
@media (hover:hover) and (prefers-reduced-motion:no-preference){.ph:hover img{transform:scale(1.02)}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;animation-delay:0s!important;transition-duration:.01ms!important}}
@media print{*{animation:none!important;transition:none!important}}
/* ==== SFN NAVGLIDE · day-navglide: стрелки вплотную к газете + живой кроссфейд полос (бриф главреда 04.10.2026) ==== */
/* Меняются только положение стрелок, логика навигации, анимация перехода между
   полосами и прокрутка; дизайн, тексты, фото, размеры материалов, сетка, цвета,
   типографика и композиция не тронуты. Режим одной полосы включает скрипт в
   конце body (html.js-nav): из полос #p1–#p4 в потоке только текущая.
   Переход — настоящий кроссфейд: уходящая и входящая полосы существуют
   одновременно. Уходящая становится слоем поверх сцены (.pages-stage =
   #newspaper, position:relative; page-exit → pageExit: opacity 1→0, .6s) и
   после анимации снимается из активного состояния (is-off); входящая плавно
   появляется в потоке: вперёд — page-enter-next → pageEnterNext (opacity 0→1 +
   translateY(14px→0)), назад — page-enter-prev → pageEnterPrev (opacity 0→1 +
   translateY(-14px→0)), обе .6s cubic-bezier(.22,.61,.36,1). Одновременно вид
   плавно (та же кривая, 600мс, rAF) возвращается к началу новой полосы — она
   всегда открывается сверху, без резкого скачка. Никаких 3D-поворотов,
   горизонтальных слайдов и мгновенной замены. Без скрипта полосы остаются в
   обычном потоке, как раньше, навигация скрыта.
   Навигация фиксирована рядом с газетой и доступна при прокрутке. Широкий
   экран (≥1300px): ← и → стоят не у краёв монитора, а вплотную к листу — в
   боковых полях, в 24px от краёв полосы (отсчёт от центральной оси: лист
   1120px, calc(50% ∓ 640px)), вертикально по центру видимой области;
   содержимое газеты не перекрывают. Счётчик N / 4 — там же, в левом поле под
   стрелкой ←. Узкий экран: боковых полей нет, поэтому весь компактный блок
   ← N / 4 → автоматически встает у верха экрана. Повторные нажатия во время
   перехода гасит блокировка busy. */
.sheetnav{display:none;position:fixed;z-index:120;top:8px;left:50%;
transform:translateX(-50%);align-items:center;gap:8px;
background:var(--paper);border:1.5px solid var(--ink);padding:4px 6px;
box-shadow:0 6px 18px rgba(20,24,28,.18)}
.sheetnav .navbtn{width:44px;height:34px;background:var(--paper);border:1.5px solid var(--ink);
color:var(--ink);font-family:"PT Mono",monospace;font-size:16px;line-height:1;padding:0 0 3px;
cursor:pointer;transition:background .2s,color .2s,opacity .2s}
.sheetnav .navbtn:hover:not(:disabled){background:var(--ink);color:var(--paper)}
.sheetnav .navbtn:focus-visible{outline:2px solid var(--ox);outline-offset:2px}
.sheetnav .navbtn:disabled{opacity:.28;cursor:default}
.sheetnav .navcount{min-width:52px;text-align:center;font-family:"PT Mono",monospace;
font-size:12px;letter-spacing:.14em;color:var(--mut);-webkit-user-select:none;user-select:none}
html.js-nav .sheetnav{display:flex}
html.js-nav{overflow-anchor:none}
html.js-nav #newspaper.pages-stage{position:relative}
html.js-nav #newspaper .sheet{margin-top:0}
html.js-nav #newspaper .sheet.is-off{display:none}
html.js-nav #newspaper .sheet.is-on{animation:none}
html.js-nav #newspaper .sheet.is-on *{animation:none}
html.js-nav #newspaper .sheet.page-exit{position:absolute;top:0;left:0;right:0;z-index:3;
pointer-events:none;animation:pageExit .6s cubic-bezier(.22,.61,.36,1) both}
html.js-nav #newspaper .sheet.page-enter-next{z-index:2;
animation:pageEnterNext .6s cubic-bezier(.22,.61,.36,1) both}
html.js-nav #newspaper .sheet.page-enter-prev{z-index:2;
animation:pageEnterPrev .6s cubic-bezier(.22,.61,.36,1) both}
@keyframes pageEnterNext{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes pageEnterPrev{from{opacity:0;transform:translateY(-14px)}to{opacity:1;transform:translateY(0)}}
@keyframes pageExit{from{opacity:1}to{opacity:0}}
@media (min-width:1300px){
html.js-nav .sheetnav{display:contents}
html.js-nav .sheetnav #navPrev{position:fixed;left:calc(50% - 640px);top:50%;transform:translateY(-50%);
width:56px;height:56px;font-size:20px;padding:0 0 4px;box-shadow:0 6px 18px rgba(20,24,28,.18)}
html.js-nav .sheetnav #navNext{position:fixed;right:calc(50% - 640px);top:50%;transform:translateY(-50%);
width:56px;height:56px;font-size:20px;padding:0 0 4px;box-shadow:0 6px 18px rgba(20,24,28,.18)}
html.js-nav .sheetnav .navcount{position:fixed;left:calc(50% - 640px);top:50%;transform:translateY(38px);
width:56px;min-width:0;padding:6px 0;background:var(--paper);border:1.5px solid var(--ink);
color:var(--ink);box-shadow:0 6px 18px rgba(20,24,28,.18)}
}
@media print{
.sheetnav{display:none!important}
html.js-nav #newspaper{min-height:0!important}
html.js-nav #newspaper .sheet{display:block!important;position:relative!important;
opacity:1!important;transform:none!important}
}
/* ==== мобильная версия: одна колонка, сценарии складываются ==== */
@media(max-width:920px){
 :root{--pad:18px}
 .grid{gap:26px}
 #p1 .grid,#p2 .grid,#p3 .grid,#p4 .grid{grid-template-columns:1fr;grid-template-areas:none}
 #a01,#a02,#a03,#a04,#a05,#a06,#a07,#a08,#a09,#a10,#a11,#a12,#vd3,#vd4{grid-area:auto}
 .t-lead{grid-template-columns:1fr;grid-template-areas:"n" "h" "ph" "s" "t" "e"}
.t-showcase{grid-template-columns:1fr;grid-template-areas:"n" "h" "s" "ph" "cap" "t" "e"}
.t-finale{grid-template-columns:1fr;grid-template-areas:"n" "h" "s" "ph" "t" "e"}
.info.kr{grid-template-columns:1fr;grid-area:auto}
 .hsep{grid-area:auto}
 #p4 #a12 .ph{margin-right:0}
.info.kr .li{border-left:0;padding-left:0}
.info.kr .li+.li{border-top:1px solid var(--hair);margin-top:6px;padding-top:6px}
 .cols2,.cols3{columns:1}
 .void.vband{flex-direction:column;align-items:flex-start;gap:6px}
}
"""


def fig(key, band=False):
    a = A[key]
    return (f'<figure class="ph{" bandcap" if band else ""}">'
            f'<img src="{IMG[key]}" alt="{a["alt"]}"><figcaption>{a["cap"]}</figcaption></figure>')


PAGE = {'fallen': 1, 'crash': 1, 'gas': 1, 'kpp': 1, 'truck': 2, 'square': 2, 'stop': 2,
        'hwy': 3, 'dragons': 3, 'caligula': 3, 'heli': 4, 'yacht': 4}


def nn(key, short=False):
    meta = (f'материал {IDX[key]} из 12' if short else
            f'03.10.2026 · полоса {PAGE[key]} · материал {IDX[key]} из 12')
    return (f'<div class="nn"><span class="num">{IDX[key]}</span>'
            f'<span class="k">{A[key]["k"]}</span>'
            f'<span class="nmeta">{meta}</span></div>')


def end():
    return '<span class="end" aria-hidden="true"></span>' 


def txt(key, cls='txt'):
    return f'<div class="{cls}">' + ''.join(f'<p>{p}</p>' for p in A[key]['p']) + '</div>'


# lead-заголовок: компактный двухстрочный лок-ап
_w = A['fallen']['t'].split()
A['fallen']['h1html'] = (f'<h1><span class="ln1">{" ".join(_w[:4])}</span> '
                         f'<span class="ln2">{" ".join(_w[4:])}</span></h1>')

NAV_JS = '''<script>
/* SFN · 2026 · day-navglide: живое переключение полос выпуска. Уходящая и
   входящая полосы существуют одновременно: уходящая становится слоем поверх
   сцены и плавно исчезает (page-exit → pageExit: opacity 1→0, 600мс), входящая
   появляется в потоке — вперёд снизу вверх (page-enter-next → pageEnterNext:
   opacity 0→1 + translateY(14px→0)), назад сверху вниз (page-enter-prev →
   pageEnterPrev: opacity 0→1 + translateY(-14px→0)), обе 600мс
   cubic-bezier(.22,.61,.36,1). Вид параллельно плавно возвращается к началу
   новой полосы (rAF, та же кривая, 600мс) — она всегда открывается сверху,
   без резкого скачка. Высота сцены на время перехода фиксируется minHeight,
   чтобы диапазон прокрутки не схлопывался; после завершения анимации уходящая
   полоса снимается из активного состояния (is-off), классы перехода чистятся.
   Флаг busy гасит повторные нажатия; prefers-reduced-motion — мгновенное
   переключение. */
(function(){
  var wrap=document.getElementById('newspaper');
  if(!wrap)return;
  var sheets=[].slice.call(wrap.querySelectorAll('.sheet'));
  if(sheets.length!==4)return;
  var btnP=document.getElementById('navPrev'),btnN=document.getElementById('navNext'),
      cnt=document.getElementById('navCount');
  if(!btnP||!btnN||!cnt)return;
  var root=document.documentElement;
  var mqRM=window.matchMedia?window.matchMedia('(prefers-reduced-motion: reduce)'):null;
  var DUR=600;
  var cur=0,busy=false,raf=0;
  function counter(n){cnt.textContent=(n+1)+' / '+sheets.length;}
  function buttons(n){btnP.disabled=(n===0);btnN.disabled=(n===sheets.length-1);}
  function cb(t,a,b){var u=1-t;return 3*u*u*t*a+3*u*t*t*b+t*t*t;}
  function ease(x){var lo=0,hi=1,t,i;
    for(i=0;i<20;i++){t=(lo+hi)/2;if(cb(t,.22,.36)<x)lo=t;else hi=t;}
    return cb((lo+hi)/2,.61,1);}
  function glideTop(){
    var y0=window.pageYOffset||root.scrollTop||0,t0=null;
    if(y0<=0)return;
    if(raf)cancelAnimationFrame(raf);
    function step(ts){
      if(t0===null)t0=ts;
      var p=(ts-t0)/DUR;
      if(p>=1){window.scrollTo(0,0);raf=0;return;}
      window.scrollTo(0,Math.round(y0*(1-ease(p))));
      raf=requestAnimationFrame(step);
    }
    raf=requestAnimationFrame(step);
  }
  function settle(from,to){
    if(raf){cancelAnimationFrame(raf);raf=0;}
    window.scrollTo(0,0);
    sheets[from].classList.remove('is-on','page-exit');
    sheets[from].classList.add('is-off');
    sheets[to].classList.remove('page-enter-next','page-enter-prev');
    wrap.style.minHeight='';
    busy=false;
    buttons(to);
  }
  function go(dir){
    if(busy)return;
    var ni=cur+dir;
    if(ni<0||ni>=sheets.length)return;
    busy=true;
    btnP.disabled=true;btnN.disabled=true;
    counter(ni);
    if(mqRM&&mqRM.matches){
      sheets[cur].classList.remove('is-on');
      sheets[cur].classList.add('is-off');
      sheets[ni].classList.remove('is-off');
      sheets[ni].classList.add('is-on');
      cur=ni;
      window.scrollTo(0,0);
      busy=false;
      buttons(cur);
      return;
    }
    var from=cur;
    cur=ni;
    var vh=window.innerHeight||root.clientHeight;
    var y0=window.pageYOffset||root.scrollTop||0;
    var oldH=sheets[from].offsetHeight;
    sheets[ni].classList.remove('is-off');
    sheets[ni].classList.add('is-on',dir>0?'page-enter-next':'page-enter-prev');
    var newH=sheets[ni].offsetHeight;
    wrap.style.minHeight=Math.max(oldH,newH,y0+vh)+'px';
    sheets[from].classList.add('page-exit');
    glideTop();
    setTimeout(function(){settle(from,ni);},DUR+120);
  }
  btnP.addEventListener('click',function(){go(-1);});
  btnN.addEventListener('click',function(){go(1);});
  root.classList.add('js-nav');
  for(var i=1;i<sheets.length;i++)sheets[i].classList.add('is-off');
  counter(0);
  buttons(0);
})();
</script>
'''

P = []
P.append("""<!DOCTYPE html>
<html lang="ru">
<head>
<!-- © 2026 San Fierro News. Дизайн и вёрстка защищены: CC BY-NC-ND 4.0. Копирование и переработка запрещены. -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>San Fierro News — ежедневный выпуск по штату от 03.10.2026</title>
<meta name="description" content="Ежедневный выпуск по штату San Andreas: гибель двоих полицейских на трассе под Лас-Вентурасом, торги за AngelPine Gas со ставкой $100 млн, военный КПП, вертолёт в тоннеле и яхта в парковом пруду — 12 кадров дня.">
<style>
""")
P.append(CSS)
P.append('</style>\n</head>\n<body>\n')
P.append('<div id="newspaper" class="pages-stage">\n')

# ================= ПОЛОСА 1: витрина =================
a, c, g, k = A['fallen'], A['crash'], A['gas'], A['kpp']
P.append('<section class="sheet" id="p1">')
P.append('<div class="mtop"><span>Независимая редакция · штат San Andreas</span>'
         '<span>суббота, 3 октября 2026</span></div>')
P.append('<div class="brand"><span class="b1">San Fierro</span><span class="b2">News</span></div>')
P.append('<div class="mrule" aria-hidden="true"></div>')
P.append('<div class="mmeta"><span><b>№ 30</b> · ежедневный выпуск</span>'
         '<span>Лос-Сантос — Лас-Вентурас — трассы штата</span>'
         '<span>12 материалов · 4 полосы · 03.10.2026</span>'
         '<span>Кадры: Anna Malboro · Фоторедактор: Sonya Malboro</span>'
         '</div>')
P.append('<div class="grid">')
P.append('<div class="hsep" aria-hidden="true"></div>')
P.append(f'<article class="m t-lead" id="a01">{nn("fallen")}{a["h1html"]}'
         f'{fig("fallen", band=True)}<div class="stand">{a["s"]}</div>'
         f'{txt("fallen")}{end()}</article>')
P.append(f'<article class="m t-side-a" id="a02">{nn("crash", short=True)}<h3>{c["t"]}</h3>'
         f'<div class="stand">{c["s"]}</div>{fig("crash")}{txt("crash")}{end()}</article>')
P.append(f'<article class="m t-split" id="a03">{nn("gas", short=True)}<h3>{g["t"]}</h3>'
         f'<div class="stand">{g["s"]}</div>'
         f'{fig("gas", band=True)}'
         f'<div class="stat"><b>$100 000 000</b><small>предыдущая ставка торгов</small></div>'
         f'{txt("gas")}{end()}</article>')
P.append(f'<article class="m t-wide" id="a04">{nn("kpp", short=True)}<h3>{k["t"]}</h3>'
         f'<div class="stand">{k["s"]}</div>{fig("kpp")}{txt("kpp")}{end()}</article>')
P.append('</div>')
P.append('<footer class="pressline"><span class="pl1">Выпуск № 30 · четыре полосы · '
         '<i>двенадцать материалов</i></span>'
         '<span class="pl2">San Fierro News · ежедневное издание штата San Andreas · 03.10.2026</span>'
         '</footer>')
P.append('</section>\n')

# ================= ПОЛОСА 2: регистр происшествий =================
t, q, s = A['truck'], A['square'], A['stop']
P.append('<section class="sheet" id="p2">')
P.append('<div class="folio"><span><b>San Fierro News</b> · выпуск № 30 · происшествия</span>'
         '<span>суббота, 3 октября 2026</span><span class="f3">полоса 2</span></div>')
P.append('<header class="sect"><span class="snum">01</span><h2>Происшествия</h2>'
         '<span class="stail" aria-hidden="true"></span><span class="sdate">03.10.2026</span></header>')
P.append('<div class="grid">')
P.append('<aside class="info kr"><div class="ih">Кратко</div>'
         '<div class="li"><b>05</b><span>у оставленного грузовика нашли тело человека</span></div>'
         '<div class="li"><b>06</b><span>тело на пустой площади: фургон стоял в отдалении</span></div>'
         '<div class="li"><b>07</b><span>патрульный автомобиль остановил седан у обочины</span></div>'
         '</aside>')
P.append(f'<article class="m t-wide" id="a05">{nn("truck")}<h3>{t["t"]}</h3>'
         f'<div class="stand">{t["s"]}</div>{fig("truck", band=True)}{txt("truck", "cols2")}{end()}</article>')
P.append(f'<article class="m t-side-a" id="a06">{nn("square", short=True)}<h3>{q["t"]}</h3>'
         f'<div class="stand">{q["s"]}</div>{fig("square")}{txt("square")}{end()}</article>')
P.append(f'<article class="m t-showcase" id="a07">{nn("stop", short=True)}<h3>{s["t"]}</h3>'
         f'<div class="stand">{s["s"]}</div>{fig("stop")}{txt("stop")}{end()}</article>')
P.append('</div>')
P.append('<footer class="pagefoot"><span>полоса 2 · выпуск № 30 · происшествия</span>'
         '<span>San Fierro News · 03.10.2026</span></footer>')
P.append('</section>\n')

# ================= ПОЛОСА 3: криминал и экономика с паузой =================
h, d, cc = A['hwy'], A['dragons'], A['caligula']
P.append('<section class="sheet" id="p3">')
P.append('<div class="folio"><span><b>San Fierro News</b> · выпуск № 30 · криминал · экономика</span>'
         '<span>суббота, 3 октября 2026</span><span class="f3">полоса 3</span></div>')
P.append('<header class="sect"><span class="snum">02</span><h2>Криминал · Экономика</h2>'
         '<span class="stail" aria-hidden="true"></span><span class="sdate">03.10.2026</span></header>')
P.append('<div class="grid">')
P.append(f'<article class="m t-wide" id="a08">{nn("hwy")}<h3>{h["t"]}</h3>'
         f'<div class="stand">{h["s"]}</div>'
         f'{fig("hwy", band=True)}{txt("hwy", "cols2")}'
         f'{end()}</article>')
P.append(f'<article class="m t-side-b" id="a09">{nn("dragons", short=True)}<h3>{d["t"]}</h3>'
         f'<div class="stand">{d["s"]}</div>{txt("dragons")}{fig("dragons")}{end()}</article>')
P.append(f'<article class="m t-side-a" id="a10">{nn("caligula", short=True)}<h3>{cc["t"]}</h3>'
         f'<div class="stand">{cc["s"]}</div>{fig("caligula")}{txt("caligula")}{end()}</article>')
P.append('</div>')
P.append('<footer class="pagefoot"><span>полоса 3 · выпуск № 30 · криминал · экономика</span>'
         '<span>San Fierro News · 03.10.2026</span></footer>')
P.append('</section>\n')

# ================= ПОЛОСА 4: финал с замком =================
he, y = A['heli'], A['yacht']
P.append('<section class="sheet" id="p4">')
P.append('<div class="folio"><span><b>San Fierro News</b> · выпуск № 30 · необычные истории</span>'
         '<span>суббота, 3 октября 2026</span><span class="f3">полоса 4</span></div>')
P.append('<header class="sect"><span class="snum">03</span><h2>Необычные истории</h2>'
         '<span class="stail" aria-hidden="true"></span><span class="sdate">03.10.2026</span></header>')
P.append('<div class="grid">')
P.append(f'<article class="m t-wide" id="a11">{nn("heli")}<h3>{he["t"]}</h3>'
         f'<div class="stand">{he["s"]}</div>{fig("heli", band=True)}{txt("heli", "cols2")}'
         f'{end()}</article>')
P.append(f'<article class="m t-finale" id="a12">{nn("yacht")}<h3>{y["t"]}</h3>'
         f'<div class="stand">{y["s"]}</div>{fig("yacht", band=True)}{txt("yacht")}'
         f'{end()}</article>')
P.append('</div>')
P.append('<footer class="colophon"><div>'
         '<div class="credits">Кадры: Anna Malboro · Фоторедактор: Sonya Malboro</div>'
         '<div class="made">выпуск очереди подшивки · 03.10.2026 · '
         'дизайн и вёрстка — редакция San Fierro News</div></div>'
         '<a class="backpill" href="newsroom.html">← Посмотреть все выпуски редакции</a></footer>')
P.append('</section>\n')

P.append('</div>\n')
P.append('<nav class="sheetnav" aria-label="Полосы выпуска">\n'
         '<button class="navbtn" id="navPrev" type="button" aria-label="Предыдущая полоса" disabled>←</button>\n'
         '<span class="navcount" id="navCount" aria-live="polite">1 / 4</span>\n'
         '<button class="navbtn" id="navNext" type="button" aria-label="Следующая полоса">→</button>\n'
         '</nav>\n')
P.append(NAV_JS)
P.append('<!-- SFN · 2026 · 029 · day-navglide -->\n</body>\n</html>\n')

html = ''.join(P)

# ---- самопроверка ----
assert '2504' not in html, 'в выпуске остался номер 2504'
assert 'Происшествия · Лас-Вентурас' in html, 'нет новой рубрики материала 01'
assert 'Главное сегодня' not in html, '«Главное сегодня» осталось в выпуске'
assert html.count('data:image/jpeg;base64,') == 12, 'кадров не 12'
assert 'style="' not in html, 'inline-стили вернулись'
for n in range(1, 13):
    assert f'id="a{n:02d}"' in html, f'нет материала a{n:02d}'
assert 'SFN-DESIGN-029: day-navglide' in html and '<!-- SFN · 2026 · 029 · day-navglide -->' in html
assert '@keyframes pageEnterNext{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}' in html, 'нет входа вперёд (translateY 14px→0)'
assert '@keyframes pageEnterPrev{from{opacity:0;transform:translateY(-14px)}to{opacity:1;transform:translateY(0)}}' in html, 'нет входа назад (translateY -14px→0)'
assert '@keyframes pageExit{from{opacity:1}to{opacity:0}}' in html, 'нет слоя исчезновения'
assert html.count('.6s cubic-bezier(.22,.61,.36,1) both') == 3, 'длительность/кривая перехода сбиты'
assert 'page-enter-next' in html and 'page-enter-prev' in html and 'page-exit' in html, 'нет состояний перехода полос'
assert 'class="pages-stage"' in html and 'html.js-nav #newspaper.pages-stage{position:relative}' in html, 'нет сцены полос'
assert 'left:calc(50% - 640px)' in html and 'right:calc(50% - 640px)' in html, 'стрелки не вплотную к листу'
for _bad in ('rotateY', 'perspective', 'backface-visibility', 'transform-origin',
             'flipshade', 'js-flip', 'transitionend', 'pageFadeIn', 'pageFadeOut',
             'is-turn', 'left:18px', 'right:18px'):
    assert _bad not in html, f'старая навигация/3D уцелели: {_bad}'
for _kf in ('pageEnterNext', 'pageEnterPrev', 'pageExit'):
    _i = html.find('@keyframes ' + _kf)
    assert _i != -1 and 'translateX' not in html[_i:_i + 200] \
        and 'rotate' not in html[_i:_i + 200] and 'scale' not in html[_i:_i + 200], \
        f'слайд/поворот/масштаб в {_kf}'
assert 'position:fixed' in html and 'display:contents' in html, 'навигация не фиксирована'
assert 'requestAnimationFrame' in html and 'minHeight' in html and 'DUR=600' in html, 'нет плавной прокрутки к началу полосы'
assert 'id="newspaper"' in html and 'id="navPrev"' in html and 'id="navNext"' in html and 'id="navCount"' in html
assert '<script>' in html and 'setTimeout' in html and 'busy' in html and 'js-nav' in html
for _pid in ('p1', 'p2', 'p3', 'p4'):
    assert '<section class="sheet" id="' + _pid + '">' in html, 'нет полосы ' + _pid
assert '<title>' in html[:4000] and 'viewport' in html[:4000] and 'name="description"' in html[:4000]
assert 'дизайн и вёрстка — редакция San Fierro News' in html
assert 'href="newsroom.html"' in html

with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write(html)
words = sum(len((a_['s'] + ' ' + ' '.join(a_['p'])).split()) for a_ in A.values())
print(f'собрано v14 (day-navglide): {OUT}')
print(f'  размер: {len(html)//1024} КБ · полос: 4 · кадров: {len(IMG)} · слов: {words}')
print('  inline-стилей: 0 · типов материалов: 6 · переменных: один :root')
