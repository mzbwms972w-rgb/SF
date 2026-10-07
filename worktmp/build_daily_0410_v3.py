#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SFN · сборщик ежедневного выпуска 04.10.2026, раунд 3 (anna-malboro/daily-04-10-2026.html).

Концепция по брифу главреда от 04.10.2026 (раунд 3): выбранный красный дизайн — ОСНОВА,
не шаблон. Новая самостоятельная система «КРАСНАЯ ЛИНИЯ» (redline-report):
— сигнатура выпуска: вертикальный красный корешок-спайн у каждой полосы с названием редакции;
— эволюция палитры: сигнальный красный + гарнет + роза + спокойная сталь, фарфоровое поле
  блока «Город», глухая чернильная полоса «Тоннель», малиновые обложка и финал;
— типографика: Fira Sans Condensed 900 (строчные/прописные, контурные слова) + Inter;
  рубричные плашки, красные проводящие линии (rlxDraw);
— шесть полос — шесть разных сценариев (grid-template-areas): обложка с кадром, выведенным
  к краям полосы; «Трассы» — асимметричная двухколонная сводка; «Тоннель» — тёмный разворот;
  «Город» — кадры на красном паспарту; «Берег и бизнес» — деловая малиновая врезка;
  финал — типографский, без фото: «Линия закрыта» + сводная лента из 12 событий;
— навигация и моушен построены С НУЛЯ (система rlx): новые классы (rlx-band/rlx-nav/rlx-flag,
  состояния st-*), новые keyframes (rlxBandIn/rlxBandOut/rlxRise/rlxFlag/rlxDraw),
  стрелки вверх/вниз стопкой вплотную к правому краю полосы, временная плашка «ПОЛОСА N / 6».
  Старые анимации и старая навигация (sfn-rise/sfn-fade/pageEnter*/pageExit/pageIndicator*/
  .sheet/.m/.navbtn/.pages-stage) НЕ используются и отсутствуют в коде.

Запуск:  python3 sf-repo/worktmp/build_daily_0410_v3.py   (из корня workspace)
Фото читаются из uploads/ (12 файлов, байт-в-байт, base64 без перекодирования).
"""
import base64, os, re, sys

ROOT = os.getcwd()  # запускать из корня workspace
UP = os.path.join(ROOT, 'uploads')
OUT = os.path.join(ROOT, 'sf-repo', 'anna-malboro', 'daily-04-10-2026.html')
assert os.path.isdir(UP), UP

STAMP = '/* SFN-DESIGN-032: redline-report · 04.10.2026 */'
MARKER = '<!-- SFN · 2026 · 032 · redline-report -->'
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
/* ==== ЕДИНСТВЕННАЯ система переменных ==== */
:root{--ink:#1c1416;--paper:#ffffff;--porc:#f7f2ee;--red:#c81e32;--deep:#8c1222;
--rose:#ef3f63;--blush:#f9e6e8;--pink:#f4ccd2;--steel:#3a4a58;--mut:#6f5f62;--fog:#c9bcba;
--body:#4a3a3d;--spine:64px;--gut:30px;--pad:46px}
::selection{background:var(--red);color:#fff}
html{-webkit-text-size-adjust:100%}
body{background:#241b1d;color:var(--ink);font-family:"Inter","Helvetica Neue",Arial,sans-serif;padding:0 0 80px}
/* ==== полосы-экраны: корешок + основное поле ==== */
.rlx-deck{display:block}
.rlx-band{max-width:1160px;margin:0 auto 36px;min-height:100vh;background:var(--paper);color:var(--ink);
position:relative;display:grid;grid-template-columns:var(--spine) 1fr;grid-template-areas:"spine main";
box-shadow:0 30px 80px rgba(0,0,0,.45);overflow:hidden}
.rlx-spine{grid-area:spine;background:var(--red);color:#fff;display:flex;flex-direction:column;
align-items:center;justify-content:space-between;padding:20px 0 18px}
.rlx-spine span{writing-mode:vertical-rl;transform:rotate(180deg);font:700 12px/1 "Inter";
letter-spacing:.42em;text-transform:uppercase;white-space:nowrap}
.rlx-spine b{width:38px;height:38px;background:#fff;color:var(--red);display:grid;place-items:center;
font:900 14px/1 "Fira Sans Condensed","Inter",sans-serif;letter-spacing:.02em}
.rlx-crim{background:var(--red);color:#fff}
.rlx-crim .rlx-spine{background:#fff;color:var(--red)}
.rlx-crim .rlx-spine b{background:var(--red);color:#fff}
.rlx-ink{background:var(--ink);color:#f2e9e7}
.rlx-ink .rlx-spine{background:var(--rose)}
.rlx-ink .rlx-spine b{background:#fff;color:var(--rose)}
.rlx-porc{background:var(--porc)}
.rlx-main{grid-area:main;padding:var(--pad) var(--pad) var(--pad) 42px;display:grid;gap:var(--gut);align-content:start}
/* ==== типографика и компоненты системы ==== */
.rlx-kick{display:inline-block;background:var(--steel);color:#fff;font:700 11.5px/1 "Inter";
letter-spacing:.22em;text-transform:uppercase;padding:9px 13px}
.rlx-kick-inv{background:#fff;color:var(--red)}
.rlx-ink .rlx-kick{background:var(--rose);color:#160f11}
.rlx-head{display:flex;flex-direction:column;gap:14px;align-items:flex-start}
.rlx-h2{font-family:"Fira Sans Condensed","Inter",sans-serif;font-weight:900;
font-size:clamp(36px,5.2vw,70px);line-height:.96;letter-spacing:-.005em}
.rlx-crim .rlx-h2,.rlx-ink .rlx-h2{color:#fff}
.rlx-rd{color:var(--red)}
.rlx-rs{color:var(--rose)}
.rlx-sub{font:600 15.5px/1.5 "Inter";color:var(--mut);max-width:720px}
.rlx-ink .rlx-sub{color:var(--fog)}
.rlx-crim .rlx-sub{color:#f6dfe2}
.rlx-rule{height:6px;width:100%;background:var(--red);transform-origin:left center;margin-top:6px}
.rlx-crim .rlx-rule{background:#fff}
.rlx-ink .rlx-rule{background:var(--rose)}
.rlx-item{display:flex;flex-direction:column;gap:14px}
.rlx-stack{display:flex;flex-direction:column;gap:28px}
.rlx-note{display:flex;flex-direction:column;gap:7px}
.rlx-h3{font-family:"Fira Sans Condensed","Inter",sans-serif;font-weight:700;
font-size:clamp(21px,1.9vw,27px);line-height:1.04;text-transform:uppercase;letter-spacing:.012em}
.rlx-ink .rlx-h3{color:#fff}
.rlx-lead{font:700 14.5px/1.4 "Inter";color:var(--red)}
.rlx-ink .rlx-lead{color:var(--pink)}
.rlx-tx{font:400 14.5px/1.62 "Inter";color:var(--body)}
.rlx-ink .rlx-tx{color:var(--fog)}
.rlx-plate{display:inline-block;align-self:flex-start;background:var(--red);color:#fff;
font:700 12px/1 "Inter";letter-spacing:.16em;text-transform:uppercase;padding:11px 15px}
.rlx-ink .rlx-plate{background:var(--rose);color:#160f11}
.rlx-w76{width:76%;margin-left:auto}
.rlx-w72{width:72%}
.rlx-w78{width:78%;margin-left:auto}
.rlx-mount{box-shadow:14px 14px 0 var(--red)}
.rlx-olw{color:transparent;-webkit-text-stroke:2.5px #fff}
@supports not (-webkit-text-stroke:1px red){.rlx-olw{color:#fff}}
/* ==== обложка ==== */
.rlx-brand{display:flex;gap:18px;align-items:center;padding-right:var(--pad)}
.rlx-mark{width:62px;height:62px;border:3px solid #fff;display:grid;place-items:center;
font:900 24px/1 "Fira Sans Condensed","Inter",sans-serif;color:#fff;flex:none}
.rlx-bname{font:900 30px/1 "Fira Sans Condensed","Inter",sans-serif;letter-spacing:.04em;color:#fff}
.rlx-btag{font:700 11px/1.4 "Inter";letter-spacing:.28em;text-transform:uppercase;color:var(--pink);margin-top:7px}
.rlx-ttlblk{padding-right:var(--pad);display:flex;flex-direction:column;gap:20px;align-items:flex-start}
.rlx-ttl{font-family:"Fira Sans Condensed","Inter",sans-serif;font-weight:900;text-transform:uppercase;
font-size:clamp(52px,7.4vw,104px);line-height:.94;letter-spacing:.005em;color:#fff}
.rlx-intro{align-self:center;max-width:430px;min-height:0}
.rlx-lead-w{font:600 18px/1.45 "Inter";color:#fff}
.rlx-tx-w{font:400 14.5px/1.6 "Inter";color:#f6dfe2;margin-top:9px}
.rlx-meta{align-self:end;font:700 11.5px/1.5 "Inter";letter-spacing:.24em;text-transform:uppercase;
color:var(--pink);border-top:2px solid rgba(255,255,255,.4);padding-top:14px;margin:0 var(--pad) 34px 0}
.a-photo{align-self:end;justify-self:end;width:100%}
/* ==== бизнес-врезка ==== */
.rlx-biz{background:var(--red);color:#fff;padding:22px;display:flex;flex-direction:column;gap:12px}
.rlx-biz .rlx-kick-inv{align-self:flex-start}
.rlx-biznum{font-family:"Fira Sans Condensed","Inter",sans-serif;font-weight:900;
font-size:clamp(24px,3.2vw,44px);line-height:1;letter-spacing:-.01em;color:#fff}
.rlx-biztx{font:500 13.5px/1.5 "Inter";color:var(--blush)}
/* ==== финал ==== */
.rlx-sign{display:inline-block;align-self:flex-start;border:2px solid #fff;color:#fff;
font:700 12px/1 "Inter";letter-spacing:.26em;text-transform:uppercase;padding:11px 16px}
.rlx-fin{font-family:"Fira Sans Condensed","Inter",sans-serif;font-weight:900;text-transform:uppercase;
font-size:clamp(46px,6.6vw,92px);line-height:.96;color:#fff}
.rlx-idx{columns:2;column-gap:46px;align-self:center;width:100%}
.rlx-ix{break-inside:avoid;display:flex;gap:14px;align-items:baseline;
border-bottom:1px solid rgba(255,255,255,.25);padding:12px 2px}
.rlx-ixn{font:900 17px/1.2 "Fira Sans Condensed","Inter",sans-serif;color:var(--pink);min-width:24px;flex:none}
.rlx-ixt{font:600 14px/1.4 "Inter";color:#fff}
.rlx-ix:hover{background:rgba(255,255,255,.07)}
.rlx-colo{display:flex;justify-content:space-between;align-items:center;gap:20px;
border-top:2px solid rgba(255,255,255,.4);padding-top:18px;
font:700 11.5px/1.5 "Inter";letter-spacing:.2em;text-transform:uppercase;color:var(--pink)}
.rlx-mark-s{width:40px;height:40px;background:#fff;color:var(--red);display:grid;place-items:center;
font:900 15px/1 "Fira Sans Condensed","Inter",sans-serif;flex:none}
/* ==== сценарии полос (только grid-template-areas) ==== */
.a-brand{grid-area:brand}.a-ttl{grid-area:ttl}.a-intro{grid-area:intro}.a-meta{grid-area:meta}.a-photo{grid-area:photo}
.a-head{grid-area:head}.a-hero{grid-area:hero}.a-side{grid-area:side}
.a-node{grid-area:node}.a-tunnel{grid-area:tunnel}.a-officer{grid-area:officer}
.a-cap{grid-area:cap}.a-twelve{grid-area:twelve}.a-town{grid-area:town}
.a-verd{grid-area:verd}.a-pier{grid-area:pier}.a-lot{grid-area:lot}
.a-seal{grid-area:seal}.a-final{grid-area:final}.a-recap{grid-area:recap}.a-roll{grid-area:roll}.a-foot{grid-area:foot}
#b1 .rlx-main{grid-template-columns:1fr 640px;grid-template-rows:auto auto 1fr auto;gap:26px var(--gut);
padding:40px 0 0 42px;grid-template-areas:"brand brand" "ttl ttl" "intro photo" "meta photo"}
#b2 .rlx-main{grid-template-columns:1.5fr 1fr;grid-template-rows:auto 1fr;
grid-template-areas:"head head" "hero side"}
#b3 .rlx-main{grid-template-columns:1fr 1.3fr;align-content:center;gap:34px 44px;
grid-template-areas:"node tunnel" "officer tunnel"}
#b4 .rlx-main{grid-template-columns:1.6fr 1fr;grid-template-rows:auto 1fr;
grid-template-areas:"cap cap" "twelve town"}
#b5 .rlx-main{grid-template-columns:1.35fr 1fr;grid-template-rows:auto 1fr;gap:28px var(--gut);
grid-template-areas:"verd verd" "pier lot"}
#b6 .rlx-main{grid-template-columns:1fr;grid-template-rows:auto auto auto 1fr auto;gap:24px;
padding:48px 52px 40px 46px;grid-template-areas:"seal" "final" "recap" "roll" "foot"}
/* ==== навигация выпуска (система rlx, собрана с нуля) ==== */
.rlx-nav{position:fixed;top:50%;left:calc(50% + 604px);transform:translateY(-50%);
display:flex;flex-direction:column;gap:10px;z-index:60}
.rlx-btn{width:52px;height:52px;background:var(--red);border:none;padding:0;cursor:pointer;
display:grid;place-items:center;color:#fff;transition:background .18s ease,transform .18s ease}
.rlx-btn svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:2.4;
stroke-linecap:round;stroke-linejoin:round}
.rlx-btn:hover{background:var(--deep)}
#rlxPrev:hover{transform:translateY(-3px)}
#rlxNext:hover{transform:translateY(3px)}
.rlx-btn:active{transform:scale(.93)}
.rlx-btn:focus-visible{outline:3px solid #fff;outline-offset:2px}
.rlx-flag{position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(18px);
background:var(--ink);color:#fff;font:700 12.5px/1 "Inter";letter-spacing:.2em;text-transform:uppercase;
padding:13px 22px;opacity:0;pointer-events:none;z-index:70}
.rlx-flag.on{animation:rlxFlag 1.75s cubic-bezier(.2,.7,.2,1) both}
html:not(.sfn-js) .rlx-nav,html:not(.sfn-js) .rlx-flag{display:none}
/* ==== моушен выпуска: новые keyframes, новая логика (rlx) ==== */
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
@media (max-width:1279px){
#b1 .rlx-main{grid-template-columns:1fr 54%}
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
.rlx-main{padding:26px 20px 30px;gap:22px}
#b1 .rlx-main{grid-template-columns:1fr;grid-template-rows:auto auto auto auto auto;gap:22px;
padding:26px 20px 0;grid-template-areas:"brand" "ttl" "intro" "meta" "photo"}
#b1 .rlx-brand{padding-right:0}
#b1 .rlx-ttlblk{padding-right:0}
#b1 .rlx-intro{max-width:none}
#b1 .rlx-meta{margin:0 0 24px}
.a-photo{width:100%}
#b2 .rlx-main{grid-template-columns:1fr;grid-template-areas:"head" "hero" "side"}
#b3 .rlx-main{grid-template-columns:1fr;align-content:start;grid-template-areas:"node" "tunnel" "officer"}
#b4 .rlx-main{grid-template-columns:1fr;grid-template-areas:"cap" "twelve" "town"}
#b5 .rlx-main{grid-template-columns:1fr;grid-template-areas:"verd" "pier" "lot"}
#b6 .rlx-main{grid-template-columns:1fr;grid-template-rows:auto auto auto auto auto;
padding:30px 20px 26px;grid-template-areas:"seal" "final" "recap" "roll" "foot"}
.rlx-w76,.rlx-w72,.rlx-w78{width:100%;margin-left:0}
.rlx-mount{box-shadow:9px 9px 0 var(--red)}
.rlx-idx{columns:1;column-gap:0}
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
.rlx-band{box-shadow:none;margin:0 auto;page-break-after:always}
}
"""

# ============================== JS ==============================
JS = """<script>
/* SFN · 2026 · redline-report: навигация и моушен выпуска — самостоятельная система rlx,
   собрана с нуля для этого выпуска (старые навигация и анимации не используются). */
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

SPINE = '<div class="rlx-spine" aria-hidden="true"><span>San Fierro News · 04.10.2026</span><b>SFN</b></div>'

def fig(mid, alt, cls='', r=None, plate=None):
    rv = ' rlx-rv' if r else ''
    dr = ' data-r="%d"' % r if r else ''
    cap = '<figcaption class="rlx-plate">%s</figcaption>' % plate if plate else ''
    return '<figure class="rlx-fig%s%s"%s><img src="%s" alt="%s">%s</figure>' % (
        (' ' + cls) if cls else '', rv, dr, '@@%s@@' % mid.upper(), alt, cap)

def note(h3, lead, tx, r=None):
    rv = ' rlx-rv' if r else ''
    dr = ' data-r="%d"' % r if r else ''
    leadh = '<p class="rlx-lead">%s</p>' % lead if lead else ''
    return '<div class="rlx-note%s"%s><h3 class="rlx-h3">%s</h3>%s<p class="rlx-tx">%s</p></div>' % (rv, dr, h3, leadh, tx)

# ============================== ПОЛОСЫ ==============================
B1 = """
<section class="rlx-band rlx-crim" id="b1">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-brand a-brand rlx-rv" data-r="1"><b class="rlx-mark">SFN</b>
<div><p class="rlx-bname">San Fierro News</p><p class="rlx-btag">Ежедневный выпуск · Лос-Сантос / Сан-Фиерро</p></div></div>
<div class="rlx-ttlblk a-ttl rlx-rv" data-r="2"><p class="rlx-kick rlx-kick-inv">Главный кадр дня</p>
<h1 class="rlx-ttl">Вертолёт —<br>посреди <span class="rlx-olw">тоннеля</span></h1></div>
<div class="rlx-intro a-intro rlx-rv" data-r="3">
<p class="rlx-lead-w">Воздушное судно обнаружили прямо внутри тоннеля между Лос-Сантосом и Сан-Фиерро.</p>
<p class="rlx-tx-w">Как вертолёт оказался в тоннеле — неизвестно. Подробности происшествия к моменту публикации не поступали.</p></div>
<p class="rlx-meta a-meta rlx-rv" data-r="4">Выпуск 04.10.2026 · 12 событий · Лос-Сантос · Сан-Фиерро · Лас-Вентурас</p>
""" + fig('m03', 'Вертолёт в тоннеле между Лос-Сантосом и Сан-Фиерро', 'a-photo', 5) + """
</div>
</section>"""

B2 = """
<section class="rlx-band" id="b2">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-head a-head rlx-rv" data-r="1">
<p class="rlx-kick">Блок 01 · Трассы</p>
<h2 class="rlx-h2">Тяжёлая сводка <b class="rlx-rd">трасс</b></h2>
<p class="rlx-sub">Три происшествия на дорогах — от Лас-Вентураса до Лос-Сантоса.</p>
<div class="rlx-rule"></div></div>
<div class="rlx-item a-hero">
""" + fig('m01', 'Массовое убийство на трассе Лас-Вентураса: на месте работают службы', '', 2) + """
""" + note('Четверо погибших на трассе Лас-Вентураса', 'Среди жертв — офицер полиции.',
           'Массовое убийство произошло на трассе Лас-Вентураса: погибли четыре человека, включая сотрудника полиции. О мотивах и подозреваемых редакция не сообщает.', 3) + """
</div>
<div class="rlx-stack a-side">
<div class="rlx-item">
""" + fig('m05', 'Последствия расправы на трассе между Лас-Вентурасом и Сан-Фиерро', '', 4) + """
""" + note('Расправа на перегоне Лас-Вентурас — Сан-Фиерро', 'Двое погибших.',
           'На трассе между Лас-Вентурасом и Сан-Фиерро обнаружены двое погибших. Обстоятельства устанавливаются.', 5) + """
</div>
<div class="rlx-item">
""" + fig('m06', 'Двойная трагедия на дороге в Лос-Сантосе', 'rlx-w76', 6) + """
""" + note('Два тела на дороге в Лос-Сантосе', 'Двойная трагедия.',
           'На месте происшествия найдены двое погибших. Причин смерти официальная информация не приводит.', 6) + """
</div>
</div>
</div>
</section>"""

B3 = """
<section class="rlx-band rlx-ink" id="b3">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-head a-node rlx-rv" data-r="1">
<p class="rlx-kick">Блок 02 · Тоннель</p>
<h2 class="rlx-h2">Узел между <b class="rlx-rs">двумя городами</b></h2>
<p class="rlx-sub">Один тоннель — и два разных происшествия.</p>
<div class="rlx-rule"></div></div>
<div class="rlx-item a-tunnel">
""" + fig('m02', 'Тело мужчины обнаружено в тоннеле между Лос-Сантосом и Сан-Фиерро', '', 2,
          plate='Тело мужчины · есть задержанный') + """
""" + note('Погибший в тоннеле', 'По делу проходит задержанный.',
           'В тоннеле между Лос-Сантосом и Сан-Фиерро обнаружено тело мужчины. Подробности не раскрываются.', 3) + """
</div>
<div class="rlx-item a-officer">
""" + fig('m04', 'Сотрудник полиции без сознания в тоннеле', '', 4) + """
""" + note('Офицер без сознания', 'Сотрудника полиции обнаружили в тоннеле.',
           'О состоянии найденного и обстоятельствах происшествия информации не поступало.', 5) + """
</div>
</div>
</section>"""

B4 = """
<section class="rlx-band rlx-porc" id="b4">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-head a-cap rlx-rv" data-r="1">
<p class="rlx-kick">Блок 03 · Город</p>
<h2 class="rlx-h2">От перевёрнутой фуры — до <b class="rlx-rd">упавшего самолёта</b></h2>
<p class="rlx-sub">Городская сводка: Сан-Фиерро и Лос-Сантос.</p>
<div class="rlx-rule"></div></div>
<div class="rlx-item a-twelve">
""" + fig('m12', 'Самолёт упал в Сан-Фиерро, на месте работают экстренные службы', 'rlx-mount', 2) + """
""" + note('Самолёт рухнул в Сан-Фиерро', 'На месте работают экстренные службы.',
           'В Сан-Фиерро упал самолёт. Данных о пострадавших к моменту публикации не поступало.', 3) + """
</div>
<div class="rlx-stack a-town">
<div class="rlx-item">
""" + fig('m07', 'Перевёрнутая фура на перекрёстке в Сан-Фиерро', 'rlx-mount', 4) + """
""" + note('Фура легла на бок', 'Перекрёсток парализован.',
           'В Сан-Фиерро перевернулась фура: движение на перекрёстке остановлено. Причина аварии неизвестна.', 5) + """
</div>
<div class="rlx-item">
""" + fig('m10', 'Скопление полиции у участка в Лос-Сантосе, рядом машина редакции LSN', 'rlx-mount rlx-w78', 6) + """
""" + note('Скопление у полицейского участка', 'Лос-Сантос.',
           'У участка замечено массовое скопление полиции, рядом — автомобиль редакции LSN. Повод не уточняется.', 6) + """
</div>
</div>
</div>
</section>"""

B5 = """
<section class="rlx-band" id="b5">
""" + SPINE + """
<div class="rlx-main">
<div class="rlx-head a-verd rlx-rv" data-r="1">
<p class="rlx-kick">Блок 04 · Берег и бизнес</p>
<h2 class="rlx-h2">Пляж перекрыт, лот — <b class="rlx-rd">на миллиарды</b></h2>
<div class="rlx-rule"></div></div>
<div class="rlx-item a-pier">
""" + fig('m08', 'Пирс на пляже Санта-Мария перекрыт, на месте полиция и скорая', '', 2,
          plate='Пирс перекрыт · полиция и скорая') + """
""" + note('Санта-Мария: берег закрыт', 'Доступ на пирс перекрыт.',
           'На пляже Санта-Мария работают полиция и скорая помощь. Причины перекрытия не сообщаются.', 3) + """
</div>
<div class="rlx-stack a-lot">
<div class="rlx-item">
""" + fig('m09', 'Тело женщины обнаружено у пляжа Санта-Мария в Лос-Сантосе', 'rlx-w72', 4) + """
""" + note('Тело у пляжа', 'Лос-Сантос.',
           'У пляжа Санта-Мария обнаружено тело женщины. Обстоятельства не раскрываются.', 5) + """
</div>
<aside class="rlx-biz rlx-rv" data-r="6">
<p class="rlx-kick rlx-kick-inv">Деловая строка</p>
""" + fig('m11', 'Продажа бизнеса Carsharing Guaranteed в мэрии Лос-Сантоса') + """
<p class="rlx-biznum">$1.800.000.000</p>
<p class="rlx-biztx">Carsharing Guaranteed выставлен на продажу в мэрии Лос-Сантоса. Заявленная цена — рекордная.</p>
</aside>
</div>
</div>
</section>"""

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
<section class="rlx-band rlx-crim" id="b6">
""" + SPINE + """
<div class="rlx-main">
<p class="rlx-sign a-seal rlx-rv" data-r="1">San Fierro News · сводная лента дня</p>
<h2 class="rlx-fin a-final rlx-rv" data-r="2">Линия <span class="rlx-olw">закрыта</span></h2>
<p class="rlx-sub a-recap rlx-rv" data-r="3">Двенадцать событий выпуска — одним списком: от трасс Лас-Вентураса до мэрии Лос-Сантоса.</p>
<div class="rlx-idx a-roll rlx-rv" data-r="4">""" + IDXH + """</div>
<div class="rlx-colo a-foot rlx-rv" data-r="5"><span>San Fierro News — ежедневная редакция</span>
<span>Выпуск 04.10.2026</span><b class="rlx-mark-s">SFN</b></div>
</div>
</section>"""

NAV = """
<nav class="rlx-nav" id="rlxNav" aria-label="Навигация по полосам выпуска">
<button class="rlx-btn" id="rlxPrev" type="button" aria-label="Предыдущая полоса"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 14l7-7 7 7"/></svg></button>
<button class="rlx-btn" id="rlxNext" type="button" aria-label="Следующая полоса"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 10l7 7 7-7"/></svg></button>
</nav>
<div class="rlx-flag" id="rlxFlag" role="status"></div>"""

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>San Fierro News — ежедневный выпуск от 04.10.2026</title>
<meta name="description" content="Ежедневный выпуск San Fierro News от 04.10.2026: двенадцать событий дня — трассы Лас-Вентураса, тоннель между городами, происшествия Сан-Фиерро и Лос-Сантоса, пляж Санта-Мария и рекордный деловой лот.">
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
          'SFN-DESIGN-031', 'class="sheet', 'class="grid"', 'class="m"', 'class="ph', 'th-red',
          'th-ink', 'th-blush', 'Bricolage', 'Source Serif', 'Space Mono', 'prefers-reduced-motion',
          'object-fit', 'clip-path', 'style="', 'rotateY', 'marquee']
for t in FORBID:
    assert t not in HTML, 'ЗАПРЕЩЁНОЕ НАСЛЕДСТВО: ' + t
NEED = ['SFN-DESIGN-032: redline-report', '@keyframes rlxBandIn', '@keyframes rlxBandOut',
        '@keyframes rlxRise', '@keyframes rlxFlag', '@keyframes rlxDraw', 'rlxPrev', 'rlxNext',
        'rlxFlag', 'sfn-js', 'st-live', 'st-off', 'st-in', 'st-out', 'grid-template-areas',
        'Fira+Sans+Condensed:wght@700;900', 'family=Inter', '<title>', 'name="viewport"',
        'name="description"', COPY, MARKER]
for t in NEED:
    assert t in HTML, 'НЕТ ОБЯЗАТЕЛЬНОГО: ' + t
assert HTML.index(STAMP) < HTML.index('@import'), 'штамп не первой строкой CSS'
assert HTML.count(':root{') == 1, 'несколько :root'
assert HTML.count('class="rlx-band') == 6 and HTML.count('<img ') == 12
assert re.search(r'<html[^>]*lang="ru"', HTML)
for i in range(1, 7):
    assert ('id="b%d"' % i) in HTML, i
assert HTML.count('ПОЛОСА') == 0, 'плашка должна собираться только в JS из escape-последовательности'
assert '\\u041f\\u041e\\u041b\\u041e\\u0421\\u0410' in HTML
# сценарии: 6 десктоп + 6 мобильных, все разные
sc = re.findall(r'#b(\d) \.rlx-main\{[^}]*?grid-template-areas:([^;}]+)', CSS)
assert sorted(x[0] for x in sc[:6]) == ['1', '2', '3', '4', '5', '6'] and len(sc) == 12, sc
assert len({x[1].strip() for x in sc[:6]}) == 6, 'десктоп-сценарии не уникальны'
# RP-чистота видимого текста
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

open(OUT, 'w', encoding='utf-8').write(HTML)
print('OK ->', OUT)
print('размер: %.2f MB · полос: 6 · фото: 12 · штамп: SFN-DESIGN-032: redline-report'
      % (len(HTML.encode('utf-8')) / 1048576))
