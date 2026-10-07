#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN · сборщик ежедневного выпуска 04.10.2026 (anna-malboro/daily-04-10-2026.html).

Концепция по брифу главреда от 04.10.2026: «хроника дня» — современный редакционный
дайджест, визуально НЕ похожий на выпуск 03.10.2026: новая типографика (Bricolage
Grotesque + Source Serif 4 + Space Mono), новая композиционная система (четыре разных
типа подачи: главное событие / хроника со ступенчатым ритмом / мозаика коротких
заметок / финальный кадр), бумажная основа, один красный акцент, редакционные линии,
номера и технические подписи. Навигация и моушен — байт-в-байт из утверждённого
канона day-pageindicator (извлечение из опубликованного 03.10.2026).

Запуск:  python3 build_daily_0410_v1.py
Фото читаются из /home/user/uploads (12 файлов, байт-в-байт, base64 без перекодирования).
"""
import base64, os, re, sys

ROOT = os.getcwd()  # запускать из корня workspace
UP = os.path.join(ROOT, 'uploads')
CANON = os.path.join(ROOT, 'sf-repo', 'anna-malboro', 'daily-03-10-2026.html')
OUT = os.path.join(ROOT, 'sf-repo', 'anna-malboro', 'daily-04-10-2026.html')
assert os.path.isdir(UP) and os.path.isfile(CANON), (UP, CANON)

STAMP = '/* SFN-DESIGN-030: chronicle-digest · 04.10.2026 */'
MARKER = '<!-- SFN · 2026 · 030 · chronicle-digest -->'

# ---- 12 фотографий: имя файла -> (mime, материал) ----
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

# ---- навигация/моушен: байт-в-байт из канона ----
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
assert 'showPageIndicator' in NAV_JS and 'busy' in NAV_JS
COPY = '<!-- © 2026 San Fierro News. Дизайн и вёрстка защищены: CC BY-NC-ND 4.0. Копирование и переработка запрещены. -->'
assert COPY in canon

CSS = STAMP + """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,200..800&family=Source+Serif+4:ital,opsz,wght@0,8..60,300..700;1,8..60,300..700&family=Space+Mono:wght@400;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
img{display:block;width:100%;height:auto}
/* ==== ЕДИНСТВЕННАЯ система переменных ==== */
:root{--paper:#f4f1e9;--ink:#121110;--ox:#c8271e;--mut:#6b6659;--hair:#d6d0c0;
--tint:#ece7da;--gut:22px;--pad:46px}
/* ==== оболочка ==== */
body{background:var(--paper);color:var(--ink);font-family:"Source Serif 4",Georgia,serif;
-webkit-font-size-adjust:100%;padding:0 0 64px}
.sheet{max-width:1120px;margin:0 auto 30px;background:var(--paper);padding:34px var(--pad) 40px;
box-shadow:0 16px 40px rgba(20,24,28,.22);position:relative}
.sheet+.sheet{margin-top:34px}
/* ==== страница: 12 колонок; сценарий полосы = grid-template-areas ==== */
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:18px var(--gut)}
/* ==== типографика ==== */
.mono{font-family:"Space Mono",monospace}
.kick{font-family:"Space Mono",monospace;font-weight:700;font-size:10px;letter-spacing:.26em;
text-transform:uppercase;color:var(--ox);display:flex;align-items:center;gap:10px}
.kick::before{content:"";width:26px;height:3px;background:var(--ox);flex:0 0 26px}
h1,h2,h3{font-family:"Bricolage Grotesque","Arial Black",sans-serif;font-weight:800;
color:var(--ink);line-height:1.02;letter-spacing:-.015em}
.stand{font-style:italic;font-weight:400;color:var(--mut);line-height:1.55}
.txt p{line-height:1.62}
.cap{font-family:"Space Mono",monospace;font-size:9px;letter-spacing:.16em;text-transform:uppercase;
color:var(--mut);margin-top:7px;display:flex;gap:8px;align-items:baseline}
.cap b{color:var(--ox);font-weight:700}
.num{font-family:"Bricolage Grotesque","Arial Black",sans-serif;font-weight:800;line-height:.8;
letter-spacing:-.03em;color:var(--ink)}
/* ==== фото: рамки и акценты ==== */
.ph{position:relative}
.ph .frm{display:block;position:relative;isolation:isolate}
.ph img{border:1px solid var(--ink)}
.ph.fr-red .frm::after{content:"";position:absolute;left:10px;top:10px;right:-10px;bottom:-10px;
border:2px solid var(--ox);z-index:-1}
.ph.fr-ink{padding:6px;border:1px solid var(--ink);background:var(--tint)}
.ph.fr-ink img{border:none}
.ph.fr-thick img{border:3px solid var(--ink)}
/* ==== полоса 1: шапка выпуска ==== */
.mtop{display:flex;justify-content:space-between;gap:14px;font-family:"Space Mono",monospace;
font-size:9.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--mut);
border-bottom:1px solid var(--hair);padding-bottom:8px}
.brand{display:flex;align-items:baseline;gap:14px;margin:16px 0 10px}
.brand .b1{font-family:"Bricolage Grotesque","Arial Black",sans-serif;font-weight:800;
font-size:clamp(44px,6.6vw,84px);line-height:.9;letter-spacing:-.035em;text-transform:uppercase}
.brand .b2{font-family:"Space Mono",monospace;font-weight:700;font-size:11px;letter-spacing:.3em;
text-transform:uppercase;color:var(--ox);border:2px solid var(--ox);padding:6px 9px 5px}
.mrule{border-top:3px solid var(--ink);border-bottom:1px solid var(--ink);height:6px;margin:0 0 12px}
.mmeta{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;font-family:"Space Mono",monospace;
font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);margin-bottom:26px}
.mmeta span{border-left:1px solid var(--hair);padding-left:10px}
.mmeta span:first-child{border-left:none;padding-left:0}
.mmeta b{color:var(--ink);font-weight:700}
#p1 .grid{grid-template-areas:"mt mt mt mt mt mt mt mt mt mt mt mt"
 "br br br br br br br br br br br br"
 "mr mr mr mr mr mr mr mr mr mr mr mr"
 "mm mm mm mm mm mm mm mm mm mm mm mm"
 "mn mn mn mn mn mn mn sd sd sd sd sd"
 "ct ct ct ct ct ct ct ct ct ct ct ct"}
#p1 .mtop{grid-area:mt}#p1 .brand{grid-area:br}#p1 .mrule{grid-area:mr}#p1 .mmeta{grid-area:mm}
#p1 .hh01{display:flex;align-items:baseline;gap:16px}
#p1 .hh01 .num{font-size:78px;color:var(--ox)}
#p1 .main{grid-area:mn;display:grid;gap:12px;align-content:start;
border-right:1px solid var(--hair);padding-right:var(--gut)}
#p1 .side{grid-area:sd;align-self:start;display:grid;gap:14px}
.stats{border-top:1px solid var(--hair);padding-top:10px;display:grid;gap:6px;
font-family:"Space Mono",monospace;font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--mut)}
.stats b{color:var(--ox);font-size:15px;letter-spacing:0;margin-right:9px}
#p1 h1{font-size:clamp(38px,4.6vw,62px);margin:2px 0 6px}
#p1 .stand{font-size:18px}
#p1 .txt p{font-size:15px}
.ledger{border-left:3px solid var(--ox);background:var(--tint);padding:12px 14px;
font-size:14px;line-height:1.55;font-style:italic}
.ledger b{font-style:normal;font-family:"Space Mono",monospace;font-size:9px;letter-spacing:.22em;
text-transform:uppercase;color:var(--ox);display:block;margin-bottom:5px;font-weight:700}
.contents{grid-area:ct;border-top:3px solid var(--ink);margin-top:26px;padding-top:12px;
display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.contents .ci{font-family:"Space Mono",monospace;font-size:11px;letter-spacing:.12em;
text-transform:uppercase;color:var(--mut);line-height:1.7}
.contents .ci b{color:var(--ox);font-size:15px;letter-spacing:0;margin-right:8px;font-weight:700}
.contents .ci i{display:block;font-style:normal;color:var(--ink)}
/* ==== полоса 2: хроника ==== */
.sect{display:flex;align-items:baseline;gap:16px;border-bottom:3px solid var(--ink);
padding-bottom:10px;margin-bottom:22px}
.sect h2{font-size:clamp(24px,2.7vw,34px);text-transform:uppercase}
.sect .st{margin-left:auto;font-family:"Space Mono",monospace;font-size:9.5px;letter-spacing:.2em;
text-transform:uppercase;color:var(--mut)}
#p2 .grid{grid-template-areas:"sc sc sc sc sc sc sc sc sc sc sc sc"
 "f2 f2 f2 f2 f2 f2 f2 f2 t3 t3 t3 t3"
 "f2 f2 f2 f2 f2 f2 f2 f2 f3 f3 f3 f3"
 "t2 t2 t2 t2 t2 t2 t2 t2 t4 t4 t4 t4"
 "lx lx lx lx lx lx lx lx f4 f4 f4 f4"
 "f5 f5 f5 f5 f5 f5 t5 t5 t5 t5 t5 t5"}
#p2 .grid>*{align-self:start}
#a02f{grid-area:f2}#a03t{grid-area:t3}#a03f{grid-area:f3}#a02t{grid-area:t2}
#a04f{grid-area:f4;width:86%}#a04t{grid-area:t4}#a05f{grid-area:f5}#a05t{grid-area:t5}
#p2 .sect{grid-area:sc}
#p2 .lx{grid-area:lx;border-top:1px solid var(--hair);padding-top:10px;
font-family:"Space Mono",monospace;font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;
color:var(--mut);line-height:2}
#p2 .lx b{color:var(--ink)}
.chr{display:grid;gap:9px}
.chr .hh{display:flex;align-items:baseline;gap:12px;border-bottom:1px solid var(--hair);padding-bottom:7px}
.chr .hh .num{font-size:40px}
.chr .hh .k{font-family:"Space Mono",monospace;font-weight:700;font-size:9px;letter-spacing:.22em;
text-transform:uppercase;color:var(--ox)}
.chr h3{font-size:clamp(17px,1.7vw,22px)}
.chr .stand{font-size:12.5px}
.chr .txt p{font-size:13px}
/* ==== полоса 3: коротко ==== */
#p3 .grid{grid-template-areas:"sc sc sc sc sc sc sc sc sc sc sc sc"
 "n6 n6 n6 n6 n6 n7 n7 n7 n7 n7 n7 n7"
 "n8 n8 n8 n8 n9 n9 n9 n9 n10 n10 n10 n10"
 "n11 n11 n11 n11 n11 n11 n11 n11 pk pk pk pk"}
#p3 .grid>*{align-self:start}
#a06{grid-area:n6}#a07{grid-area:n7}#a08{grid-area:n8}#a09{grid-area:n9}#a10{grid-area:n10}
#a11{grid-area:n11}#p3 .sect{grid-area:sc}
#p3pk{grid-area:pk}
.note{display:grid;gap:8px;align-content:start}
.note .hh{display:flex;align-items:baseline;gap:10px}
.note .hh .num{font-size:46px}
.note .hh .k{font-family:"Space Mono",monospace;font-weight:700;font-size:8.5px;letter-spacing:.2em;
text-transform:uppercase;color:var(--ox)}
.note h3{font-size:clamp(15px,1.5vw,19px);line-height:1.12}
.note .stand{font-size:12px}
.note .txt p{font-size:12.5px}
#a06{border-top:3px solid var(--ink);padding-top:12px}
#a07{border-top:1px solid var(--hair);padding-top:12px;
grid-template-columns:1fr 300px;grid-template-areas:"hh hh" "hd hd" "sd pf" "tx pf";column-gap:18px}
#a07 .hh{grid-area:hh}#a07 h3{grid-area:hd}
#a07 .stand{grid-area:sd}#a07 .txt{grid-area:tx}#a07 .ph{grid-area:pf;align-self:center}
#a08{border-left:1px solid var(--hair);padding-left:var(--gut)}
#a08 .ph{width:92%}
#a10 .ph{width:88%}
#a09{border-left:1px solid var(--hair);padding-left:var(--gut)}
#a09 .ph{width:100%}
#a10{border-top:1px solid var(--hair);padding-top:12px}
#a11{border-top:3px solid var(--ink);padding-top:14px;
grid-template-columns:1fr 340px;grid-template-areas:"hh pf" "sd pf" "tx pf";column-gap:20px}
#a11 .hh{grid-area:hh}#a11 .stand{grid-area:sd}#a11 .txt{grid-area:tx}#a11 .ph{grid-area:pf}
#a11 .num{font-size:64px;color:var(--ox)}
#p3pk{border:1px solid var(--ink);background:var(--tint);padding:14px;
font-family:"Space Mono",monospace;font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;
color:var(--mut);line-height:2}
#p3 #p3pk{align-self:stretch;display:flex;flex-direction:column;justify-content:center}
#p3pk b{color:var(--ox);font-weight:700}
/* ==== полоса 4: финальный кадр ==== */
#p4 .grid{grid-template-areas:"fn fn fn fn f12 f12 f12 f12 f12 f12 f12 f12"
 "cl cl cl cl cl cl cl cl cl cl cl cl"}
#p4 .fin{grid-area:fn;display:grid;gap:12px;align-content:start;
border-right:1px solid var(--hair);padding-right:var(--gut)}
#p4 .fin .num{font-size:150px;color:var(--ink)}
#p4 .fin .numline{border-bottom:3px solid var(--ox);padding-bottom:10px}
#p4 h3{font-size:clamp(26px,2.9vw,38px)}
#p4 .stand{font-size:14px}
#p4 .txt p{font-size:15px}
.idx{border-top:1px solid var(--hair);padding-top:10px;display:grid;gap:4px;
font-family:"Space Mono",monospace;font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut)}
.idx span{display:flex;gap:10px}
.idx b{color:var(--ox);font-weight:700}
#p4 .f12{grid-area:f12;align-self:start;display:grid;gap:16px}
.colo{grid-area:cl;border-top:3px solid var(--ink);margin-top:30px;padding-top:12px;
display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;
font-family:"Space Mono",monospace;font-size:9px;letter-spacing:.18em;text-transform:uppercase;
color:var(--mut)}
.colo b{color:var(--ink)}
.colo .end{color:var(--ox);font-weight:700}
/* ==== подвал полосы ==== */
.pagefoot{margin:24px 0 0;border-top:1px solid var(--hair);padding-top:9px;
display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;
font-family:"Space Mono",monospace;font-weight:700;font-size:8.5px;letter-spacing:.2em;
text-transform:uppercase;color:var(--mut)}
""" + NAV_CSS + """
"""

# =================РАЗМЕТКА=================
def fig(mid, cls, alt, cap):
    return ('<figure class="ph %s"><span class="frm"><img src="%s" alt="%s"></span>'
            '<figcaption class="cap"><b>%s</b>%s</figcaption></figure>') % (cls, DATA[mid], alt, mid[1:], cap)

P1 = """<section class="sheet" id="p1"><div class="grid">
<div class="mtop"><span>Независимая редакция · штат San Andreas</span><span>воскресенье, 4 октября 2026</span></div>
<div class="brand"><span class="b1">San Fierro News</span><span class="b2">хроника дня</span></div>
<div class="mrule" aria-hidden="true"></div>
<div class="mmeta"><span><b>№ 31</b> · ежедневный дайджест</span><span>12 событий · 12 кадров · 4 полосы</span><span>Лос-Сантос — Сан-Фиерро — Лас-Вентурас</span><span>Кадры: <b>Anna Malboro</b></span></div>
<article class="main"><div class="hh01"><span class="num">01</span><span class="kick">Главное событие дня · Лас-Вентурас</span></div>
<h1>Четверо погибших на трассе Лас-Вентураса — среди них офицер полиции</h1>
<div class="stand">Патруль, тела у обочины и несколько тёмных машин: перекрёсток трассы с высоты — самый тяжёлый кадр дня.</div>
<div class="txt"><p>Массовое убийство на трассе Лас-Вентураса: четверо погибших, включая офицера полиции. В кадре — перекрёсток шоссе: патрульная машина у обочины, тела рядом с торговым фургоном под вывеской-хотдогом и две тёмные легковушки на полотне.</p>
<p>Как развернулась расправа и кто её участники, не сообщается. Выпуск 04.10.2026 редакция собирает как хронику дня: двенадцать событий, двенадцать кадров.</p></div>
</article>
<div class="side">@@F01@@
<div class="ledger"><b>Подводка редакции</b>День в штате начался с этого кадра: четыре имени на одной трассе. Дальше хроника идёт по тоннелям и шоссе — и завершается ночным Сан-Фиерро.</div>
<div class="stats"><span><b>4</b>имени на одной трассе</span><span><b>3</b>кадра в тоннеле ЛС—СФ</span><span><b>6</b>коротких событий на полосе 3</span><span><b>1</b>ночной кадр Сан-Фиерро</span></div></div>
<div class="contents"><div class="ci"><b>02–05</b><i>Хроника дня</i>тоннели ЛС—СФ и трассы · полоса 2</div>
<div class="ci"><b>06–11</b><i>Коротко</i>шесть событий дня · полоса 3</div>
<div class="ci"><b>12</b><i>Финальный кадр</i>Сан-Фиерро · полоса 4</div></div>
</div>
<footer class="pagefoot"><span>полоса 1 · выпуск № 31 · главное событие</span><span>San Fierro News · 04.10.2026</span></footer></section>"""

P2 = """<section class="sheet" id="p2"><div class="grid">
<div class="sect"><span class="kick">Хроника дня</span><h2>Тоннели и шоссе: четыре кадра</h2><span class="st">материалы 02–05 · 04.10.2026</span></div>
<div id="a02f">@@F02@@</div>
<article class="chr" id="a03t"><div class="hh"><span class="num">03</span><span class="k">Хроника · тоннель ЛС—СФ</span></div>
<h3>Вертолёт обнаружен посреди тоннеля</h3>
<div class="stand">Белая машина с красными полозьями стоит там, где должна идти дорога.</div>
<div class="txt"><p>В тоннеле между Лос-Сантосом и Сан-Фиерро обнаружен вертолёт: белая машина с красными полозьями стоит прямо на полотне. Людей в кадре не видно; как вертолёт оказался внутри, не сообщается.</p></div></article>
<div id="a03f">@@F03@@</div>
<article class="chr" id="a02t"><div class="hh"><span class="num">02</span><span class="k">Хроника · тоннель ЛС—СФ</span></div>
<h3>В тоннеле найдено тело мужчины — есть задержанный</h3>
<div class="stand">Фургон, седан и розовая Audi с шильдиком PRO-Sport выстроились у патруля.</div>
<div class="txt"><p>В тоннеле между Лос-Сантосом и Сан-Фиерро обнаружено тело мужчины: есть задержанный. В кадре — чёрный фургон, бордовый седан, розовая Audi с шильдиком PRO-Sport, патруль и женщина с сотрудником полиции у тела.</p></div></article>
<div id="a04f">@@F04@@</div>
<div class="lx"><b>Сводка полосы</b><br>02 · тело мужчины, задержанный<br>03 · вертолёт на полотне<br>04 · сотрудник без сознания<br>05 · расправа на трассе</div>
<article class="chr" id="a04t"><div class="hh"><span class="num">04</span><span class="k">Хроника · тоннель ЛС—СФ</span></div>
<h3>Сотрудник полиции найден без сознания</h3>
<div class="stand">Патруль с включёнными фарами — и офицер, лежащий на полотне.</div>
<div class="txt"><p>В тоннеле между Лос-Сантосом и Сан-Фиерро обнаружен сотрудник полиции без сознания. Кадр тёмный: патрульная машина с фарами и лежащий на дороге офицер. О состоянии сотрудника не сообщается.</p></div></article>
<div id="a05f">@@F05@@</div>
<article class="chr" id="a05t"><div class="hh"><span class="num">05</span><span class="k">Хроника · трасса ЛВ—СФ</span></div>
<h3>Кровавая расправа на трассе: двое погибших</h3>
<div class="stand">Пустынный участок шоссе, патруль и два тела на песке у полотна.</div>
<div class="txt"><p>На трассе между Лас-Вентурасом и Сан-Фиерро — кровавая расправа: двое погибших. В кадре — пустынный участок шоссе, патрульная машина и два тела на песке у дороги.</p></div></article>
</div>
<footer class="pagefoot"><span>полоса 2 · выпуск № 31 · хроника дня</span><span>San Fierro News · 04.10.2026</span></footer></section>"""

P3 = """<section class="sheet" id="p3"><div class="grid">
<div class="sect"><span class="kick">Коротко</span><h2>Ещё шесть событий дня</h2><span class="st">материалы 06–11 · 04.10.2026</span></div>
<article class="note" id="a06"><div class="hh"><span class="num">06</span><span class="k">Трассы · Лос-Сантос</span></div>
@@F06@@
<h3>Двойная трагедия на дороге в Лос-Сантосе</h3>
<div class="stand">Жёлтый пикап и патруль — у двух тел на месте происшествия.</div>
<div class="txt"><p>На дороге в Лос-Сантосе — два тела на месте происшествия: в кадре жёлтый пикап, патрульная машина и погибшие у обочины.</p></div></article>
<article class="note" id="a07"><div class="hh"><span class="num">07</span><span class="k">Город · Сан-Фиерро</span></div>
<h3>Фура перевернулась на перекрёстке: движение парализовано</h3>
<div class="stand">Красный тягач лёг на бок прямо на перекрёстке.</div>
<div class="txt"><p>В Сан-Фиерро перевернулась фура: движение на перекрёстке парализовано. Тягач с прицепом лежит поперёк полос; перекрёсток пустует.</p></div>
@@F07@@</article>
<article class="note" id="a08"><div class="hh"><span class="num">08</span><span class="k">Пляж · Санта-Мария</span></div>
@@F08@@
<h3>Пирс на пляже Санта-Мария перекрыт</h3>
<div class="stand">Баррикады с табличками WARNING CLOSED TO TRAFFIC, полиция и скорая у входа.</div>
<div class="txt"><p>Пирс на пляже Санта-Мария перекрыт: полиция и скорая на месте. В кадре — баррикады, патрульные машины, скорая и лёгкий самолёт в небе.</p></div></article>
<article class="note" id="a09"><div class="hh"><span class="num">09</span><span class="k">Лос-Сантос</span></div>
<div class="stand">Патруль у стены с надписью HOMIES SHARP; офицер рядом с телом.</div>
<div class="txt"><p>У пляжа Санта-Мария в Лос-Сантосе обнаружено тело женщины: в кадре патруль у стены с надписью HOMIES SHARP, сотрудник полиции и тело на песке.</p></div>
@@F09@@</article>
<article class="note" id="a10"><div class="hh"><span class="num">10</span><span class="k">Лос-Сантос</span></div>
<h3>У участка — колонна патрулей и машина редакции LSN</h3>
<div class="stand">Скопление полиции у входа и новостной фургон с бортом LS 2.</div>
<div class="txt"><p>У полицейского участка в Лос-Сантосе замечено массовое скопление полиции: колонна патрулей у входа и машина редакции LSN с бортом LS 2. Что произошло у участка, не сообщается.</p></div>
@@F10@@</article>
<article class="note" id="a11"><div class="hh"><span class="num">11</span><span class="k">Экономика · мэрия Лос-Сантоса</span></div>
<div class="stand">Экран в зале мэрии: предыдущая ставка — $1.800.000.000.</div>
<div class="txt"><p>В мэрии Лос-Сантоса выставлен на продажу бизнес Carsharing Guaranteed: рекордные $1.800.000.000 — миллиард восемьсот миллионов долларов. В кадре — экран зала с предыдущей ставкой и стенд с презентацией поместья рядом.</p></div>
@@F11@@</article>
<div id="p3pk"><b>SFN · дайджест</b><br>04.10.2026 · полоса 3<br>шесть событий без длинных<br>подводок — как они есть</div>
</div>
<footer class="pagefoot"><span>полоса 3 · выпуск № 31 · коротко</span><span>San Fierro News · 04.10.2026</span></footer></section>"""

P4 = """<section class="sheet" id="p4"><div class="grid">
<article class="fin"><div class="numline"><span class="num">12</span></div>
<span class="kick">Финальный кадр · Сан-Фиерро</span>
<h3>В Сан-Фиерро упал самолёт — экстренные службы на месте</h3>
<div class="stand">Тёмный фюзеляж поперёк дороги у отеля с пальмами: ночной кадр, которым день закрылся.</div>
<div class="txt"><p>В Сан-Фиерро упал самолёт: на месте работают экстренные службы. В кадре — тёмный фюзеляж поперёк дороги у отеля, вдоль которого выстроены пальмы; съёмка в ночном свете.</p>
<p>Этим кадром выпуск 04.10.2026 завершается: хроника дня прошла от трассы Лас-Вентураса до ночного Сан-Фиерро.</p></div>
</article>
<div class="f12">@@F12@@
<div class="idx"><span><b>01</b>трасса ЛВ · массовое убийство</span><span><b>02</b>тоннель ЛС—СФ · тело, задержанный</span><span><b>03</b>тоннель ЛС—СФ · вертолёт</span><span><b>04</b>тоннель ЛС—СФ · офицер без сознания</span><span><b>05</b>трасса ЛВ—СФ · расправа</span><span><b>06</b>Лос-Сантос · двойная трагедия</span><span><b>07</b>Сан-Фиерро · фура на перекрёстке</span><span><b>08</b>Санта-Мария · пирс перекрыт</span><span><b>09</b>Лос-Сантос · тело у пляжа</span><span><b>10</b>Лос-Сантос · участок, колонна патрулей</span><span><b>11</b>мэрия ЛС · торги Carsharing</span><span><b>12</b>Сан-Фиерро · упавший самолёт</span></div></div>
<div class="colo"><span><b>San Fierro News</b> · ежедневный дайджест · выпуск от 04.10.2026</span>
<span>12 событий · 12 кадров · 4 полосы · кадры: Anna Malboro</span>
<span>дизайн и вёрстка — редакция San Fierro News · <span class="end">■ конец выпуска</span></span></div>
</div>
<footer class="pagefoot"><span>полоса 4 · выпуск № 31 · финальный кадр</span><span>San Fierro News · 04.10.2026</span></footer></section>"""

FIGS = {
 '@@F01@@': fig('m01', 'fr-red', 'Перекрёсток трассы Лас-Вентураса с высоты: патруль, тела у обочины, фургон с вывеской-хотдогом', ' · трасса Лас-Вентураса · съёмка с высоты'),
 '@@F02@@': fig('m02', 'fr-thick', 'Тоннель: чёрный фургон, бордовый седан, розовая Audi, патруль и тело мужчины', ' · тоннель ЛС—СФ · кадр с задержанным'),
 '@@F03@@': fig('m03', '', 'Белый вертолёт с красными полозьями стоит посреди тоннеля', ' · тоннель ЛС—СФ · вертолёт на полотне'),
 '@@F04@@': fig('m04', '', 'Тёмный тоннель: патруль с фарами и сотрудник полиции на полотне', ' · тоннель ЛС—СФ · ночной кадр'),
 '@@F05@@': fig('m05', 'fr-ink', 'Пустынная трасса: патруль и два тела на песке у обочины', ' · трасса ЛВ—СФ · обочина'),
 '@@F06@@': fig('m06', '', 'Дорога в Лос-Сантосе: жёлтый пикап, патруль и два тела', ' · Лос-Сантос · место происшествия'),
 '@@F07@@': fig('m07', 'fr-thick', 'Перевёрнутая красная фура поперёк перекрёстка в Сан-Фиерро', ' · Сан-Фиерро · перекрёсток'),
 '@@F08@@': fig('m08', '', 'Перекрытый пирс: баррикады, полиция, скорая и самолёт в небе', ' · пляж Санта-Мария · пирс'),
 '@@F09@@': fig('m09', '', 'Патруль у стены с надписью HOMIES SHARP, офицер и тело женщины на песке', ' · Лос-Сантос · пляж Санта-Мария'),
 '@@F10@@': fig('m10', '', 'Колонна патрулей у полицейского участка и новостной фургон LS 2', ' · Лос-Сантос · участок'),
 '@@F11@@': fig('m11', 'fr-ink', 'Экран в зале мэрии Лос-Сантоса со ставкой $1.800.000.000', ' · мэрия Лос-Сантоса · экран зала'),
 '@@F12@@': fig('m12', 'fr-thick', 'Тёмный фюзеляж самолёта поперёк дороги у отеля с пальмами в Сан-Фиерро', ' · Сан-Фиерро · ночной кадр'),
}
for k, v in FIGS.items():
    P1, P2, P3, P4 = P1.replace(k, v), P2.replace(k, v), P3.replace(k, v), P4.replace(k, v)

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
<title>San Fierro News — ежедневный дайджест от 04.10.2026</title>
<meta name="description" content="Ежедневный дайджест по штату San Andreas от 04.10.2026: массовое убийство на трассе Лас-Вентураса, хроника тоннелей Лос-Сантос—Сан-Фиерро, шесть коротких событий и ночной кадр упавшего самолёта — 12 кадров дня.">
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
</div>
%s
%s
</body>
</html>
""" % (COPY, CSS, P1, P2, P3, P4, NAV_HTML, NAV_JS)

# ---- самопроверки сборщика (до записи) ----
assert HTML.count('data:image/') == 12, HTML.count('data:image/')
for k, (fn, mime) in PH.items():
    assert DATA[k] in HTML, k
assert 'style="' not in HTML
# inline-styles запрещены полностью: убираем служебные grid-column из разметки
assert HTML.count(':root{') == 1
assert 'grid-template-areas' in CSS
for bad in ('Evolve Role Play', 'Evolve RP', 'Saint-Louis', '2504', '_'):
    vis = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', HTML, flags=re.S)
    vis = re.sub(r'base64,[A-Za-z0-9+/=]+', '', vis)
    vis = re.sub(r'<[^>]+>', ' ', vis)
    if bad == '_':
        assert not re.search(r'[A-Za-zА-Яа-я]_[A-Za-zА-Яа-я]', vis), bad
    else:
        assert bad not in vis, bad
    assert re.search(r'\bчат\b', vis) is None
assert STAMP in HTML and MARKER not in HTML  # маркер добавляется ниже
HTML = HTML.replace('</body>', MARKER + '\n</body>')

open(OUT, 'w', encoding='utf-8').write(HTML)
print('OK', OUT, len(HTML.encode('utf-8')), 'bytes')
