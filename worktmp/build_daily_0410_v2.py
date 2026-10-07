#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN · сборщик ежедневного выпуска 04.10.2026, раунд 2 (anna-malboro/daily-04-10-2026.html).

Концепция по брифу главреда от 04.10.2026 (раунд 2): «bold red/pink pitch deck» —
современное визуальное медиа по мотивам Canva-шаблона Red and Pink Bold Pitch Deck:
сверхкрупная конденсированная типографика (Fira Sans Condensed 900 + Inter),
насыщенный красный и розовый как главный визуальный язык, большие цветовые поля,
смелая асимметрия, шесть экранов с шестью РАЗНЫМИ композициями (обложка / гигантский
заголовок + один кадр + вставка / типографический акцент + разномасштабные кадры /
цветовое поле + гигантская цифра + малый кадр / коллаж с тезисом / финал), минимум
декора. Никакой старой газетной сетки, номеров-плакатов и повторяющихся карточек.
Навигация и моушен — канон day-pageindicator (байт-в-байт из опубликованного 03.10),
единственная адаптация: guard числа полос 4 -> 6 (sheets.length!==6).

Запуск:  python3 build_daily_0410_v2.py   (из корня workspace)
Фото читаются из uploads/ (12 файлов, байт-в-байт, base64 без перекодирования).
"""
import base64, os, re, sys

ROOT = os.getcwd()  # запускать из корня workspace
UP = os.path.join(ROOT, 'uploads')
CANON = os.path.join(ROOT, 'sf-repo', 'anna-malboro', 'daily-03-10-2026.html')
OUT = os.path.join(ROOT, 'sf-repo', 'anna-malboro', 'daily-04-10-2026.html')
assert os.path.isdir(UP) and os.path.isfile(CANON), (UP, CANON)

STAMP = '/* SFN-DESIGN-031: red-pink-bold · 04.10.2026 */'
MARKER = '<!-- SFN · 2026 · 031 · red-pink-bold -->'

# ---- 12 фотографий: имя файла -> (mime) ----
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
    raw = open(os.path.join(UP, fn), 'rb').read()
    DATA[k] = 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode('ascii'))

# ---- навигация/моушен: канон байт-в-байт + адаптация числа полос 4 -> 6 ----
canon = open(CANON, encoding='utf-8').read()
i0 = canon.index('/* ==== SFN NAVGLIDE')
i1 = canon.index('@media (max-width:1299px){html.js-nav .page-indicator{top:60px}}')
i1 = canon.index('\n', i1)
j0 = canon.index('@media print{.page-indicator{display:none!important}}', i1)
j1 = canon.index('}', j0) + 1
NAV_CSS = canon[i0:j1]
assert 'pageEnterNext' in NAV_CSS and 'pageIndicatorInOut' in NAV_CSS and 'calc(50% - 640px)' in NAV_CSS
s0 = canon.index('<script>\n/* SFN · 2026 · day-navglide:')
s1 = canon.index('</script>', s0) + len('</script>')
NAV_JS = canon[s0:s1]
assert 'showPageIndicator' in NAV_JS and 'busy' in NAV_JS and 'sheets.length!==4' in NAV_JS
NAV_JS = NAV_JS.replace('sheets.length!==4', 'sheets.length!==6')  # единственная адаптация: шесть полос
assert 'sheets.length!==6' in NAV_JS
COPY = '<!-- © 2026 San Fierro News. Дизайн и вёрстка защищены: CC BY-NC-ND 4.0. Копирование и переработка запрещены. -->'
assert COPY in canon

CSS = STAMP + """
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans+Condensed:wght@700;900&family=Inter:wght@400;500;600;700;800&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
img{display:block;width:100%;height:auto}
/* ==== ЕДИНСТВЕННАЯ система переменных ==== */
:root{--ink:#171011;--paper:#ffffff;--blush:#fbe9ec;--red:#a81219;--maroon:#700b10;
--rose:#e42a63;--pink:#f6d5db;--mut:#7c6a6d;--ox:#a81219;--gut:26px;--pad:64px}
/* ==== оболочка: светлый стол, листы-экраны ==== */
body{background:var(--blush);color:var(--ink);font-family:"Inter","Helvetica Neue",Arial,sans-serif;
-webkit-font-size-adjust:100%;padding:0 0 72px}
.sheet{max-width:1120px;margin:0 auto 34px;min-height:100vh;background:var(--paper);
padding:50px var(--pad) 40px;position:relative;display:flex;flex-direction:column;
box-shadow:0 26px 70px rgba(112,11,16,.16)}
.sheet>.grid{flex:1 1 auto}
.pagefoot{margin-top:26px;border-top:2px solid currentColor;padding-top:10px;
display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;
font-size:9.5px;font-weight:800;letter-spacing:.24em;text-transform:uppercase;opacity:.72}
/* ==== тематические поля ==== */
.th-red{background:var(--red);color:var(--pink)}
.th-ink{background:var(--ink);color:var(--pink)}
.th-blush{background:var(--blush);color:var(--ink)}
.th-red .txt p,.th-ink .txt p{color:var(--pink);opacity:.9}
.th-red .lead,.th-ink .lead{color:var(--paper)}
/* ==== типографика ==== */
h1,h2,h3{font-family:"Fira Sans Condensed","Arial Narrow",Impact,sans-serif;font-weight:900;
text-transform:uppercase;line-height:.88;letter-spacing:-.008em;color:inherit}
h3{font-weight:700;line-height:.96;letter-spacing:0}
.lead{font-weight:600;font-size:15px;line-height:1.4}
.txt p{font-size:13px;line-height:1.62;color:var(--mut)}
.tag{display:inline-block;align-self:start;font-size:10px;font-weight:800;letter-spacing:.26em;
text-transform:uppercase;padding:7px 11px 6px;background:var(--rose);color:var(--paper)}
.line{font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--mut)}
/* ==== сетка: сценарий экрана = grid-template-areas ==== */
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:22px var(--gut);align-content:start}
.ph{margin:0}
/* ==== экран 1: обложка ==== */
#s1 .grid{grid-template-areas:"tp tp tp tp tp tp tp tp tp tp tp tp"
 "br br br br br br br br br br br br"
 "ph ph ph ph ph ph ph ph cl cl cl cl"
 "ph ph ph ph ph ph ph ph cl cl cl cl"
 "tx tx tx tx tx tx tx tx cl cl cl cl"
 "bd bd bd bd bd bd bd bd bd bd bd bd"}
#s1 .tp{grid-area:tp;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;
font-size:10px;font-weight:800;letter-spacing:.28em;text-transform:uppercase;color:var(--pink);opacity:.9}
#s1 .brand{grid-area:br;font-family:"Fira Sans Condensed","Arial Narrow",Impact,sans-serif;
font-weight:900;text-transform:uppercase;font-size:clamp(64px,9.7vw,140px);line-height:.84;
letter-spacing:-.012em;color:var(--pink)}
#s1 .ph{grid-area:ph}
#s1 .cl{grid-area:cl;display:grid;gap:14px;align-content:start}
#s1 .cl h2{font-size:clamp(34px,3.3vw,50px);color:var(--paper)}
#s1 .cl .lead{font-size:16px}
#s1 .tx{grid-area:tx;align-self:start}
#s1 .bd{grid-area:bd;display:flex;align-items:flex-end;justify-content:space-between;gap:18px;flex-wrap:wrap}
#s1 .bd .dg{font-family:"Fira Sans Condensed","Arial Narrow",Impact,sans-serif;font-weight:900;
font-size:clamp(64px,9.6vw,150px);line-height:.8;letter-spacing:-.01em;color:var(--maroon)}
#s1 .bd .line{color:var(--pink);padding-bottom:14px}
/* ==== экран 2: гигантский заголовок + кадр + вставка ==== */
#s2 .grid{grid-template-areas:"kd kd kd kd kd kd kd kd kd kd kd kd"
 "hd hd hd hd hd hd hd hd in in in in"
 "hd hd hd hd hd hd hd hd in in in in"
 "f12 f12 f12 f12 f12 f12 f12 f12 f12 f12 f12 f12"
 "f12 f12 f12 f12 f12 f12 f12 f12 f12 f12 f12 f12"
 "f12 f12 f12 f12 f12 f12 f12 f12 f12 f12 f12 f12";
 align-content:stretch;grid-template-rows:auto 1fr 1fr auto auto auto}
#s2 .kd{grid-area:kd;display:flex;align-items:center;gap:16px}
#s2 .kd .rule{flex:1;height:2px;background:var(--ink)}
#s2 h1{grid-area:hd;font-size:clamp(48px,6.6vw,100px);align-self:center}
#s2 .in{grid-area:in;background:var(--rose);color:var(--paper);padding:26px 24px;
display:grid;gap:12px;align-content:start}
#s2 .in .lead{font-size:17px;line-height:1.35}
#s2 .in .txt p{color:var(--paper);opacity:.92}
#s2 .ph{grid-area:f12;align-self:start}
/* ==== экран 3: типографический акцент + разномасштабные кадры ==== */
#s3 .grid{grid-template-areas:"tt tt tt tt tt tt tt tt tt tt tt tt"
 "sb sb sb sb sb sb sb sb sb sb sb sb"
 "f3 f3 f3 f3 f3 f3 f3 f4 f4 f4 f4 f4"
 "f3 f3 f3 f3 f3 f3 f3 f4 f4 f4 f4 f4"
 "t3 t3 t3 t3 t3 t3 t3 t4 t4 t4 t4 t4"
 "f2 f2 f2 f2 f2 f2 n2 n2 n2 n2 n2 n2"
 "f2 f2 f2 f2 f2 f2 n2 n2 n2 n2 n2 n2"}
#s3 .tt{grid-area:tt;font-family:"Fira Sans Condensed","Arial Narrow",Impact,sans-serif;
font-weight:900;text-transform:uppercase;font-size:clamp(80px,12vw,190px);line-height:.8;
letter-spacing:-.012em}
#s3 .tt .dot{color:var(--rose)}
#s3 .sb{grid-area:sb}
#s3 .f3{grid-area:f3}#s3 .f4{grid-area:f4;margin-top:46px;width:92%}#s3 .f2{grid-area:f2}
#s3 .t3{grid-area:t3;display:grid;gap:9px;align-content:start}
#s3 .t4{grid-area:t4;display:grid;gap:9px;align-content:start}
#s3 .n2{grid-area:n2;display:grid;gap:10px;align-content:start}
#s3 h3{font-size:clamp(19px,1.9vw,27px)}
#s3 .n2 h3{font-weight:900;font-size:clamp(30px,3.2vw,50px);line-height:.9}
#s3 .n2 .tag{background:var(--ink)}
/* ==== экран 4: цветовое поле + гигантская цифра + малый кадр ==== */
#s4 .grid{grid-template-areas:"bg bg bg bg bg bg bg bg bg bg bg bg"
 "hd hd hd hd hd hd hd hd f11 f11 f11 f11"
 "hd hd hd hd hd hd hd hd f11 f11 f11 f11"
 "tx tx tx tx tx tx tx tx f11 f11 f11 f11"
 "tx tx tx tx tx tx tx tx f11 f11 f11 f11"
 "gh gh gh gh gh gh gh gh gh gh gh gh";
 align-content:stretch;grid-template-rows:auto 1fr 1fr 1fr 1fr auto}
#s4 .bg{grid-area:bg;font-family:"Fira Sans Condensed","Arial Narrow",Impact,sans-serif;
font-weight:900;font-size:clamp(52px,8.4vw,136px);line-height:.82;letter-spacing:-.008em;color:var(--pink)}
#s4 .hd{grid-area:hd;display:grid;gap:16px;align-content:center}
#s4 h2{font-size:clamp(40px,5.4vw,84px);color:var(--paper)}
#s4 .tx{grid-area:tx;display:grid;gap:10px;align-content:center}
#s4 .ph{grid-area:f11;align-self:center;width:94%}
#s4 .gh{grid-area:gh;font-family:"Fira Sans Condensed","Arial Narrow",Impact,sans-serif;
font-weight:900;text-transform:uppercase;font-size:clamp(36px,5.8vw,92px);line-height:.84;
letter-spacing:-.008em;color:var(--maroon)}
/* ==== экран 5: коллаж + тезис ==== */
#s5 .grid{grid-template-areas:"th th th th th th th th th th th th"
 "f5 f5 f5 f5 f5 f5 f5 f8 f8 f8 f8 f8"
 "f5 f5 f5 f5 f5 f5 f5 f8 f8 f8 f8 f8"
 "c5 c5 c5 c5 c5 c5 c5 c8 c8 c8 c8 c8"
 "tt tt tt tt tt tt tt tt tt tt tt tt"
 "f6 f6 f6 f6 f7 f7 f7 f7 f7 f7 f7 f7"
 "f6 f6 f6 f6 f7 f7 f7 f7 f7 f7 f7 f7"
 "c6 c6 c6 c6 c7 c7 c7 c7 c7 c7 c7 c7"}
#s5 .th{grid-area:th;display:flex;align-items:center;gap:16px}
#s5 .tt{grid-area:tt;font-family:"Fira Sans Condensed","Arial Narrow",Impact,sans-serif;
font-weight:900;text-transform:uppercase;font-size:clamp(44px,6.6vw,104px);line-height:.86;
letter-spacing:-.01em;color:var(--red)}
#s5 .f5{grid-area:f5;width:96%}#s5 .f8{grid-area:f8;margin-top:58px;width:88%}
#s5 .f6{grid-area:f6;margin-top:64px;width:86%}#s5 .f7{grid-area:f7;width:90%}
#s5 .c5{grid-area:c5}#s5 .c8{grid-area:c8}#s5 .c6{grid-area:c6}#s5 .c7{grid-area:c7}
#s5 .cap{display:grid;gap:8px;align-content:start}
#s5 h3{font-size:clamp(19px,1.9vw,27px)}
/* ==== экран 6: финал ==== */
#s6 .grid{grid-template-areas:"f9 f9 f9 f9 f9 f9 f9 f9 f10 f10 f10 f10"
 "f9 f9 f9 f9 f9 f9 f9 f9 f10 f10 f10 f10"
 "c9 c9 c9 c9 c9 c9 c9 c9 c10 c10 c10 c10"
 "ff ff ff ff ff ff ff ff ff ff ff ff"
 "sb sb sb sb sb sb sb sb sb sb sb sb"
 "cc cc cc cc cc cc cc cc cc cc cc cc"}
#s6 .f9{grid-area:f9;width:94%}#s6 .f10{grid-area:f10;margin-top:78px;width:90%}
#s6 .c9{grid-area:c9}#s6 .c10{grid-area:c10}
#s6 .cap{display:grid;gap:8px;align-content:start}
#s6 h3{font-size:clamp(19px,1.9vw,27px);color:var(--paper)}
#s6 .lead{font-size:13.5px}
#s6 .ff{grid-area:ff;font-family:"Fira Sans Condensed","Arial Narrow",Impact,sans-serif;
font-weight:900;text-transform:uppercase;font-size:clamp(60px,9.4vw,150px);line-height:.84;
letter-spacing:-.012em;color:var(--pink)}
#s6 .ff .dot{color:var(--rose)}
#s6 .sb{grid-area:sb;font-size:14px;font-weight:600;color:var(--pink);opacity:.85}
#s6 .cc{grid-area:cc;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;
font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--pink);opacity:.8}
#s6 .cc .end{color:var(--rose);font-weight:800;opacity:1}
/* ==== узкий экран: гиганты ужимаются, поля листа тоньше ==== */
@media (max-width:700px){
.sheet{padding:36px 22px 30px}
.grid{gap:18px 12px;grid-template-columns:1fr}
#s1 .grid{grid-template-areas:"tp" "br" "ph" "cl" "tx" "bd"}
#s2 .grid{grid-template-areas:"kd" "hd" "in" "f12"}
#s3 .grid{grid-template-areas:"tt" "sb" "f3" "t3" "f4" "t4" "f2" "n2"}
#s4 .grid{grid-template-areas:"bg" "hd" "tx" "f11" "gh"}
#s5 .grid{grid-template-areas:"th" "f5" "c5" "f8" "c8" "tt" "f6" "c6" "f7" "c7"}
#s6 .grid{grid-template-areas:"f9" "c9" "f10" "c10" "ff" "sb" "cc"}
#s4 .bg{font-size:clamp(26px,8.6vw,136px)}
#s3 .tt{font-size:clamp(56px,12vw,190px)}
#s6 .ff{font-size:clamp(44px,9.4vw,150px)}
#s1 .bd .dg{font-size:clamp(44px,9.6vw,150px)}
#s2 h1{font-size:clamp(40px,9vw,148px)}
}
/* ==== печать: статично ==== */
@media print{
body{background:#fff;padding:0}
.sheet{min-height:auto;box-shadow:none;margin:0 0 12mm;max-width:none;padding:10mm}
}
""" + NAV_CSS + """
"""

# =================РАЗМЕТКА=================
def fig(mid, cls, alt):
    return '<figure class="ph %s"><img src="%s" alt="%s"></figure>' % (cls, DATA[mid], alt)

def note(cls, tag, h, lead, txt):
    out = '<article class="cap %s">' % cls
    if tag:
        out += '<span class="tag">%s</span>' % tag
    out += '<h3>%s</h3><div class="lead">%s</div><div class="txt"><p>%s</p></div></article>' % (h, lead, txt)
    return out

S1 = """<section class="sheet th-red" id="s1"><div class="grid">
<div class="tp"><span>независимая редакция штата San Andreas</span><span>воскресенье · 04.10.2026</span></div>
<div class="brand">San Fierro News</div>
@@F01@@
<div class="cl"><span class="tag">главный кадр дня</span>
<h2>Четверо на трассе Лас-Вентураса</h2>
<div class="lead">Массовое убийство на трассе: среди погибших — офицер полиции.</div></div>
<div class="tx"><p>Перекрёсток шоссе с высоты: патруль у обочины, тела рядом с фургоном и две тёмные легковушки на полотне. Как развернулась расправа — не сообщается.</p></div>
<div class="bd"><span class="dg">04.10.2026</span><span class="line">внутри — один день и двенадцать кадров</span></div>
</div>
<footer class="pagefoot"><span>san fierro news · обложка</span><span>04.10.2026 · воскресенье</span></footer></section>"""

S2 = """<section class="sheet" id="s2"><div class="grid">
<div class="kd"><span class="tag">сан-фиерро · ночной кадр</span><span class="rule"></span></div>
<h1>Самолёт рухнул в Сан-Фиерро</h1>
<div class="in"><div class="lead">Экстренные службы работают на месте падения.</div>
<div class="txt"><p>Тёмный фюзеляж поперёк дороги у отеля с пальмами: ночной кадр, которым день закрылся.</p></div></div>
@@F12@@
</div>
<footer class="pagefoot"><span>полоса 2 · сан-фиерро</span><span>san fierro news · 04.10.2026</span></footer></section>"""

S3 = """<section class="sheet th-blush" id="s3"><div class="grid">
<div class="tt">Тоннель<span class="dot">.</span></div>
<div class="sb line">три события под землёй · тоннель Лос-Сантос — Сан-Фиерро · 04.10.2026</div>
@@F03@@
@@F04@@
<article class="cap t3"><h3>Вертолёт посреди тоннеля</h3>
<div class="lead">Белая машина с красными полозьями стоит на полотне.</div>
<div class="txt"><p>Как вертолёт оказался внутри тоннеля между Лос-Сантосом и Сан-Фиерро — не сообщается. Людей в кадре не видно.</p></div></article>
<article class="cap t4"><h3>Офицер лежит на полотне</h3>
<div class="lead">Сотрудник полиции обнаружен без сознания.</div>
<div class="txt"><p>Тёмный кадр тоннеля: патруль с включёнными фарами и офицер на дороге. О состоянии сотрудника не сообщается.</p></div></article>
@@F02@@
<article class="cap n2"><span class="tag">тоннель · задержанный</span><h3>Есть задержанный</h3>
<div class="lead">Тоннель между Лос-Сантосом и Сан-Фиерро: тело мужчины.</div>
<div class="txt"><p>В кадре — фургон, седан, розовая Audi и патруль: женщина и сотрудник полиции у тела.</p></div></article>
</div>
<footer class="pagefoot"><span>полоса 3 · тоннель лос-сантос — сан-фиерро</span><span>san fierro news · 04.10.2026</span></footer></section>"""

S4 = """<section class="sheet th-red" id="s4"><div class="grid">
<div class="bg">$1.800.000.000</div>
<div class="hd"><span class="tag">мэрия Лос-Сантоса · торги</span>
<h2>Миллиард восемьсот миллионов</h2></div>
<div class="tx"><div class="lead">Бизнес Carsharing Guaranteed выставлен на продажу.</div>
<p>Рекордный ценник — на экране зала мэрии; рядом — стенд с презентацией бизнеса. Сумма ставки — миллиард восемьсот миллионов долларов.</p></div>
@@F11@@
<div class="gh">Carsharing Guaranteed</div>
</div>
<footer class="pagefoot"><span>полоса 4 · мэрия лос-сантоса</span><span>san fierro news · 04.10.2026</span></footer></section>"""

S5 = """<section class="sheet" id="s5"><div class="grid">
<div class="th"><span class="tag">коротко</span><span class="line">четыре кадра подряд — как они есть</span></div>
@@F05@@
@@F08@@
<article class="cap c5"><h3>Кровавая расправа: двое</h3>
<div class="lead">Трасса Лас-Вентурас — Сан-Фиерро, двое погибших.</div>
<div class="txt"><p>Пустынный участок шоссе: патруль и два тела на песке у полотна.</p></div></article>
<article class="cap c8"><h3>Пирс перекрыт</h3>
<div class="lead">Полиция и скорая на пляже Санта-Мария.</div>
<div class="txt"><p>Баррикады у входа, патрульные машины, скорая и лёгкий самолёт в небе.</p></div></article>
<div class="tt">Один день. Двенадцать кадров.</div>
@@F06@@
@@F07@@
<article class="cap c6"><h3>Двойная трагедия</h3>
<div class="lead">Два тела на месте дорожного происшествия в Лос-Сантосе.</div>
<div class="txt"><p>Жёлтый пикап и патруль у обочины: съёмка с места происшествия.</p></div></article>
<article class="cap c7"><h3>Фура поперёк перекрёстка</h3>
<div class="lead">В Сан-Фиерро перевернулась фура: движение парализовано.</div>
<div class="txt"><p>Красный тягач с прицепом лёг на бок поперёк полос; перекрёсток пуст.</p></div></article>
</div>
<footer class="pagefoot"><span>полоса 5 · сводка дня</span><span>san fierro news · 04.10.2026</span></footer></section>"""

S6 = """<section class="sheet th-ink" id="s6"><div class="grid">
@@F09@@
@@F10@@
<article class="cap c9"><h3>Берег молчит</h3>
<div class="lead">Тело женщины обнаружено у пляжа Санта-Мария в Лос-Сантосе.</div>
<div class="txt"><p>Патруль у стены с надписью HOMIES SHARP, сотрудник полиции и тело на песке.</p></div></article>
<article class="cap c10"><h3>Участок в окружении патрулей</h3>
<div class="lead">Массовое скопление полиции у участка в Лос-Сантосе.</div>
<div class="txt"><p>Колонна патрулей у входа и машина редакции LSN с бортом LS 2. Что произошло — не сообщается.</p></div></article>
<div class="ff">День закрыт<span class="dot">.</span><br>До завтра<span class="dot">.</span></div>
<div class="sb">San Fierro News собирает день в двенадцати кадрах.</div>
<div class="cc"><span>San Fierro News · ежедневный выпуск · 04.10.2026</span><span>кадры: Anna Malboro</span>
<span>дизайн и вёрстка — редакция San Fierro News · <span class="end">конец выпуска</span></span></div>
</div>
<footer class="pagefoot"><span>полоса 6 · финал</span><span>san fierro news · 04.10.2026</span></footer></section>"""

FIGS = {
 '@@F01@@': fig('m01', '', 'Перекрёсток трассы Лас-Вентураса с высоты: патруль, тела у обочины, фургон с вывеской-хотдогом'),
 '@@F02@@': fig('m02', 'f2', 'Тоннель: чёрный фургон, бордовый седан, розовая Audi, патруль и тело мужчины'),
 '@@F03@@': fig('m03', 'f3', 'Белый вертолёт с красными полозьями стоит посреди тоннеля'),
 '@@F04@@': fig('m04', 'f4', 'Тёмный тоннель: патруль с фарами и сотрудник полиции на полотне'),
 '@@F05@@': fig('m05', 'f5', 'Пустынная трасса: патруль и два тела на песке у обочины'),
 '@@F06@@': fig('m06', 'f6', 'Дорога в Лос-Сантосе: жёлтый пикап, патруль и два тела'),
 '@@F07@@': fig('m07', 'f7', 'Перевёрнутая красная фура поперёк перекрёстка в Сан-Фиерро'),
 '@@F08@@': fig('m08', 'f8', 'Перекрытый пирс: баррикады, полиция, скорая и самолёт в небе'),
 '@@F09@@': fig('m09', 'f9', 'Патруль у стены с надписью HOMIES SHARP, офицер и тело женщины на песке'),
 '@@F10@@': fig('m10', 'f10', 'Колонна патрулей у полицейского участка и новостной фургон LS 2'),
 '@@F11@@': fig('m11', '', 'Экран в зале мэрии Лос-Сантоса со ставкой $1.800.000.000'),
 '@@F12@@': fig('m12', '', 'Тёмный фюзеляж самолёта поперёк дороги у отеля с пальмами в Сан-Фиерро'),
}
for k, v in FIGS.items():
    S1, S2, S3, S4, S5, S6 = (x.replace(k, v) for x in (S1, S2, S3, S4, S5, S6))

NAV_HTML = """<nav class="sheetnav" aria-label="Полосы выпуска">
<button id="navPrev" class="navbtn" type="button" aria-label="Предыдущая полоса">&#8592;</button>
<button id="navNext" class="navbtn" type="button" aria-label="Следующая полоса">&#8594;</button>
</nav>
<div id="pageIndicator" class="page-indicator" aria-live="polite" aria-atomic="true"></div>"""

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
%s
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>San Fierro News — ежедневный выпуск от 04.10.2026</title>
<meta name="description" content="Ежедневный выпуск San Fierro News от 04.10.2026 в визуальном языке bold red/pink editorial: массовое убийство на трассе Лас-Вентураса, упавший самолёт в Сан-Фиерро, хроника тоннеля Лос-Сантос—Сан-Фиерро, торги Carsharing Guaranteed за $1.800.000.000 и ещё восемь кадров дня.">
<style>
%s
</style>
</head>
<body>
<div id="newspaper" class="pages-stage">
%s
%s
%s
%s
%s
%s
</div>
%s
%s
</body>
</html>
""" % (COPY, CSS, S1, S2, S3, S4, S5, S6, NAV_HTML, NAV_JS)

# ---- самопроверки сборщика (до записи) ----
assert HTML.count('data:image/') == 12, HTML.count('data:image/')
for k, (fn, mime) in PH.items():
    assert HTML.count(DATA[k]) == 1, k
assert 'style="' not in HTML
assert HTML.count(':root{') == 1
_ids = re.findall(r'#s(\d) \.grid\{grid-template-areas', CSS)
assert sorted(set(_ids)) == ['1', '2', '3', '4', '5', '6'] and len(_ids) == 12, _ids
assert 'object-fit' not in HTML and 'clip-path' not in HTML
assert 'grid-template-areas' in CSS
vis = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', HTML, flags=re.S)
vis = re.sub(r'base64,[A-Za-z0-9+/=]+', '', vis)
vis = re.sub(r'<[^>]+>', ' ', vis)
for bad in ('Evolve Role Play', 'Evolve RP', 'Saint-Louis', '2504'):
    assert bad not in vis, bad
assert re.search(r'\bчат\b', vis) is None
assert re.search(r'[A-Za-zА-Яа-я]_[A-Za-zА-Яа-я]', vis) is None
assert STAMP in HTML and MARKER not in HTML
HTML = HTML.replace('</body>', MARKER + '\n</body>')
assert HTML.index(STAMP) < HTML.index('@import')

open(OUT, 'w', encoding='utf-8').write(HTML)
print('OK', OUT, len(HTML.encode('utf-8')), 'bytes')
