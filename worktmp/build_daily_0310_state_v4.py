#!/usr/bin/env python3
"""SFN: сборщик выпуска 03.10.2026 (v4, компактная ежедневная газета, 4 полосы).
Дизайн: SFN-DESIGN-029, слаг compact-edition (бриф главреда от 03.10.2026:
−80% словесного объёма, 4 полосы, ничего не обрезается: ни тексты, ни кадры).
Тексты переписаны компактно (информация сохранена), подписи к кадрам — дословно из v1.
Фото: width:100% + height:auto (без object-fit:cover — кадр виден целиком).
Никакого overflow:hidden / max-height / line-clamp в текстовых блоках.
Выход: anna-malboro/daily-03-10-2026.html (очередь подшивки).
Запуск из корня:  python3 worktmp/build_daily_0310_state_v4.py
"""
import base64
import io
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP = os.path.join(ROOT, 'assets')
OUT = os.path.join(ROOT, 'anna-malboro', 'daily-03-10-2026.html')

FILES = {
    'truck': 'state0310-01-truck.jpg', 'gas': 'state0310-02-gas.jpg',
    'crash': 'state0310-03-crash.jpg', 'square': 'state0310-04-square.jpg',
    'hwy': 'state0310-05-hwy.jpg', 'heli': 'state0310-06-heli.jpg',
    'yacht': 'state0310-07-yacht.jpg', 'dragons': 'state0310-08-dragons.jpg',
    'stop': 'state0310-09-stop.jpg', 'fallen': 'state0310-10-fallen.jpg',
    'caligula': 'state0310-11-caligula.jpg', 'kpp': 'state0310-12-kpp.jpg',
}


def b64(key):
    im = Image.open(os.path.join(UP, FILES[key])).convert('RGB')
    im = im.resize((1600, 900), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=80, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


IMG = {k: b64(k) for k in FILES}

# ---- компактные материалы: информация сохранена, объём −80% ----
A = {
 'fallen': dict(k='Главное сегодня · Лас-Вентурас',
   t='На трассе под Лас-Вентурасом погибли двое полицейских',
   s='Патрульная машина осталась у разделителя, на полотне дороги — двое в тёмной форме.',
   p=['Двое сотрудников полиции погибли на пустом участке шоссе под Лас-Вентурасом: патрульный автомобиль остался у бетонного разделителя в нескольких метрах от тел, следов других машин на полотне нет. Имена и подразделения погибших не назывались; официальных заявлений к выходу номера не поступало.'],
   cap='Патрульный автомобиль и двое погибших на почти пустом шоссе: обстоятельства трагедии предстоит установить.',
   alt='Пустое шоссе под Лас-Вентурасом: патрульная машина у разделителя и двое людей в тёмной форме на полотне'),
 'crash': dict(k='ДТП · Лос-Сантос',
   t='Патрульный и легковушка сошлись бортами на пустом перекрёстке',
   s='Борт 2504 и автомобиль в чёрно-красном узоре столкнулись в центре перекрёстка; других машин рядом не было.',
   p=['Борт 2504 и легковушка в чёрно-красном узоре сошлись бортами на пустом перекрёстке в Лос-Сантосе; пострадавших нет, виновность не установлена.'],
   cap='Борт 2504 и легковушка в чёрно-красном узоре: перекрёсток в момент столкновения был пуст.',
   alt='Патрульный автомобиль и гражданская машина в чёрно-красном узоре соприкоснулись на перекрёстке'),
 'gas': dict(k='Экономика · торги',
   t='За AngelPine Gas на торгах предлагают сто миллионов',
   s='Табло площадки Starkweathers Estate зафиксировало предыдущую ставку — $100 млн.',
   p=['Предыдущая ставка торгов за заправку AngelPine Gas на площадке Starkweathers Estate — $100 млн; победитель станет известен в следующих раундах.'],
   cap='Табло торгов: ставка, после которой разговор о цене заправки перешёл в разряд городских новостей.',
   alt='Табло в зале торгов: AngelPine Gas, предыдущая ставка сто миллионов долларов'),
 'kpp': dict(k='Силовые структуры · Лос-Сантос',
   t='Военные у закрытого шлагбаума: КПП работает без объяснений',
   s='Армейский внедорожник и двое в камуфляже — у опущенного шлагбаума на ограждённом периметре.',
   p=['У опущенного шлагбаума на ограждённом периметре в Лос-Сантосе — армейский внедорожник песочного цвета и двое военнослужащих, один с винтовкой; назначение мероприятий не пояснялось.'],
   cap='У опущенного шлагбаума — машина песочного цвета и двое в камуфляже: назначение мероприятий не пояснялось.',
   alt='Контрольно-пропускной пункт: опущенный шлагбаум, армейский внедорожник и двое военнослужащих'),
 'truck': dict(k='Происшествие · Лос-Сантос',
   t='У оставленного грузовика нашли тело человека',
   s='Оранжевый фургон стоял с заглушенным двигателем, человек лежал в паре метров от кабины.',
   p=['Грузовик с глухим красным кузовом стоял на бетонной площадке у откоса в Лос-Сантосе с закрытыми дверями; в паре метров от кабины лежал человек в светлой одежде. Следов борьбы нет, причина смерти не называлась.'],
   cap='Грузовик остался стоять там, где его оставили; следов борьбы на площадке не видно.',
   alt='Оранжевый грузовик-фургон на бетонной площадке, рядом на земле лежит человек'),
 'square': dict(k='Происшествие · Лос-Сантос',
   t='Тело на пустой площади: фургон стоял в отдалении',
   s='Мощёная площадь у ограды была безлюдна; человек лежал посреди открытого пространства.',
   p=['На безлюдной площади у ограды в Лос-Сантосе лежал человек в светлой рубашке; бирюзовый фургон-дом в десятках метров — единственная техника, его связь с произошедшим не установлена.'],
   cap='Площадь у ограды оставалась пустой; фургон в отдалении — единственная машина в кадре.',
   alt='Пустая мощёная площадь: человек лежит на асфальте, вдали бирюзовый фургон-дом'),
 'stop': dict(k='Хроника · Лос-Сантос',
   t='Борт 2504: будничная остановка у кирпичного здания',
   s='Патрульный автомобиль остановил седан у обочины; беседа у водительской двери выглядела спокойной.',
   p=['Патрульный борт 2504 остановил серо-голубой седан у обочины в Лос-Сантосе; причина остановки не сообщалась.'],
   cap='Остановка у обочины: причина визита патрульного осталась за кадром.',
   alt='Патрульный автомобиль стоит за седаном у обочины, человек у водительской двери'),
 'hwy': dict(k='Криминал · трасса штата',
   t='Открытая дверь и обломок на полотне: остановка на шоссе под Лас-Вентурасом',
   s='Патрульный с распахнутой дверью, чёрный седан с тормозным следом и человек с предметом, похожим на оружие.',
   p=['Патрульный с распахнутой дверью и чёрный седан с длинным тормозным следом встали на шоссе у промзоны под Лас-Вентурасом; на полотне — отделившаяся деталь кузова, у двери седана — человек с предметом, похожим на оружие. О задержании, стрельбе или пострадавших официально не сообщалось.'],
   cap='Тормозной след и отделившаяся деталь кузова: остановка на шоссе прошла не по будничному сценарию.',
   alt='Шоссе у промзоны: патрульная машина с открытой дверью и чёрный седан с тормозным следом'),
 'dragons': dict(k='Городская жизнь · Лас-Вентурас',
   t='У Four Dragons не осталось свободных мест',
   s='Стоянка казино заполнилась до последнего места: от ярких кроссоверов до лимузина у крыла.',
   p=['Все размеченные места у Four Dragons Hotel & Casino заняты, у крыла встали фургон и лимузин; гости шли к золотому кольцу входа, администрация наплыв не комментировала.'],
   cap='Стоянка у входа заполнена до последнего места: редкий час, когда свободных мест нет даже у крыла служебного въезда.',
   alt='Плотный ряд автомобилей на стоянке у входа Four Dragons Hotel & Casino'),
 'caligula': dict(k='Экономика · Лас-Вентурас',
   t='Caligula’s Palace на обслуживании: стоянка молчит',
   s='На утопленной парковке у башни — две красные машины на все пустые ряды.',
   p=['Казино находится на техническом обслуживании, и утопленная стоянка у башни Caligula’s Palace пуста: две красные машины на все ряды. Вероятно, работы и объясняют отсутствие гостей; когда обслуживание завершится, паркинг вернёт привычный вид.'],
   cap='Две машины на всю стоянку: редкий кадр для парковки крупного казино.',
   alt='Пустая утопленная стоянка у башни Caligula’s Palace: две красные машины на весь паркинг'),
 'heli': dict(k='Необычная история · трасса штата',
   t='Вертолёт, которого не было в сводках',
   s='Лёгкий вертолёт стоит посреди проезжей части пустого тоннеля между Лос-Сантосом и Сан-Фиерро.',
   p=['Светло-серый вертолёт стоит на собственных полозьях посреди полосы пустого дорожного тоннеля: роторы неподвижны, людей рядом нет, повреждений обшивки и следов копоти не видно. Как машина оказалась внутри — а наземным путём иных входов у тоннеля нет — никто не объяснил; сводок о пропавших вертолётах город не публиковал.'],
   cap='Вертолёт стоит посреди полосы, будто дожидаясь, пока кто-нибудь объяснит его появление.',
   alt='Светло-серый вертолёт стоит посреди проезжей части пустого дорожного тоннеля'),
 'yacht': dict(k='Необычная история · Лос-Сантос',
   t='Яхта в парковом пруду: вода есть, выхода нет',
   s='Белая моторная яхта стоит в замкнутом пруду городского парка; ближайшая большая вода — в десятках кварталов.',
   p=['Белая яхта с тёмной рубкой неподвижно стоит в замкнутом пруду парка Лос-Сантоса под мостом: это причал, от которого невозможно отплыть; как судно спустили на воду, не сообщалось.'],
   cap='Пруд с яхтой: единственный причал в городе, от которого невозможно отплыть.',
   alt='Белая моторная яхта стоит в замкнутом парковом пруду под мостом'),
}

CSS = """/* SFN-DESIGN-029: compact-edition · 03.10.2026 */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;0,900;1,700&family=PT+Serif:ital,wght@0,400;0,700;1,400&family=PT+Sans:wght@400;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
img{display:block;max-width:100%}
:root{--paper:#f7f4ed;--paper2:#f4f0e6;--ink:#1b1a17;--mut:#6e6a62;--line:#d9d3c6;--red:#9e1b1b}
body{background:#e8e4da;color:var(--ink);font-family:"PT Serif",Georgia,serif;-webkit-font-size-adjust:100%;
min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:14px 12px 8px;
background-image:radial-gradient(#ddd8cb 1px,transparent 1px);background-size:26px 26px}
.stage{flex:1 1 auto;display:flex;align-items:center;justify-content:center;width:100%;min-height:0}
.sheet-wrap{position:relative}
.book{position:absolute;top:0;left:0;width:720px;height:1000px;transform-origin:top left;perspective:2200px}
/* лист: контент не скрывается никакими правилами — всё, что не поместится, остаётся видимым */
.page{position:absolute;inset:0;background:var(--paper);padding:26px 28px;
box-shadow:0 14px 34px rgba(40,36,28,.22),0 2px 6px rgba(40,36,28,.14);border:1px solid #cfc8b8;
opacity:0;visibility:hidden;transform:rotateY(0deg);transform-origin:left center;
transition:transform .56s cubic-bezier(.35,.1,.25,1),opacity .5s,visibility 0s .56s}
.page:nth-child(even){background:var(--paper2)}
.page::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:0;
background:linear-gradient(100deg,rgba(60,50,30,.26),rgba(60,50,30,0) 42%);transition:opacity .56s}
.page.cur{opacity:1;visibility:visible;z-index:2;transform:none;
transition:transform .56s cubic-bezier(.35,.1,.25,1),opacity .45s,visibility 0s}
.page.out-l{visibility:visible;z-index:3;transform:rotateY(-68deg);opacity:.15}
.page.out-l::after{opacity:1}
.page.out-r{visibility:visible;z-index:3;transform-origin:right center;transform:rotateY(68deg);opacity:.15}
.page.out-r::after{opacity:1;background:linear-gradient(-100deg,rgba(60,50,30,.26),rgba(60,50,30,0) 42%)}
.page.in-r{visibility:visible;z-index:2;transform-origin:right center;transform:rotateY(46deg);opacity:.5;transition:none}
.page.in-l{visibility:visible;z-index:2;transform:rotateY(-46deg);opacity:.5;transition:none}
/* типографика */
.kicker{font-family:"PT Sans",sans-serif;font-size:10px;font-weight:700;letter-spacing:.19em;
text-transform:uppercase;color:var(--red);margin-bottom:4px}
h1,h3{font-family:"Playfair Display",Georgia,serif;font-weight:800;line-height:1.14;letter-spacing:-.004em}
h1{font-size:29px;margin-bottom:6px}
h3{font-size:17px;margin-bottom:4px}
.stand{font-style:italic;color:var(--mut);font-size:12.5px;line-height:1.5;margin-bottom:8px}
figure{margin:0 0 8px}
.ph img{width:100%;height:auto;transition:filter .4s}
.ph:hover img{filter:contrast(1.04)}
figcaption{margin-top:4px;font-family:"PT Sans",sans-serif;font-size:10.5px;line-height:1.45;color:var(--mut)}
.txt p{margin:0 0 7px;line-height:1.6;font-size:13.5px}
.txt2{columns:2;column-gap:16px;column-rule:1px solid var(--line)}
.txt2 p{margin:0 0 7px;line-height:1.6;font-size:13.5px}
/* статьи: естественная высота по содержимому, никаких фиксированных размеров */
.page article{height:auto;min-height:0;overflow:visible}
.leadgrid{display:grid;grid-template-columns:48fr 52fr;gap:16px;align-items:start;margin-bottom:12px}
/* шапка */
.masttop{display:flex;justify-content:space-between;font-family:"PT Sans",sans-serif;font-size:9.5px;
letter-spacing:.12em;text-transform:uppercase;color:var(--mut)}
.mastname{font-family:"Playfair Display",Georgia,serif;font-weight:900;text-align:center;font-size:32px;
line-height:1.08;padding:5px 0 4px}
.mastname i{font-style:normal;color:var(--red)}
.mastmeta{display:flex;flex-wrap:wrap;justify-content:center;gap:2px 12px;font-family:"PT Sans",sans-serif;
font-size:10px;letter-spacing:.05em;border-top:1px solid var(--ink);border-bottom:4px double var(--ink);padding:4px 0}
.mastmeta b{color:var(--red)}
.mastcred{margin-top:4px;text-align:center;font-family:"PT Sans",sans-serif;font-size:9.5px;color:var(--mut)}
.sechead{display:flex;align-items:baseline;gap:6px;border-top:1px solid var(--ink);
border-bottom:1px solid var(--line);padding:4px 0 5px;margin:0 0 14px}
.sechead .sq{width:7px;height:7px;background:var(--red);flex:0 0 7px;transform:translateY(-1px)}
.sechead h2{font-family:"PT Sans",sans-serif;font-weight:700;font-size:12px;letter-spacing:.17em;text-transform:uppercase}
.sechead .pg{margin-left:auto;font-family:"PT Sans",sans-serif;font-size:9.5px;color:var(--mut)}
/* композиции */
.briefs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:start;
border-top:1px solid var(--line);padding-top:10px}
.g-side{display:grid;grid-template-columns:45fr 55fr;gap:16px;align-items:start;margin-bottom:16px}
.g-side-rev{display:grid;grid-template-columns:55fr 45fr;gap:16px;align-items:start;margin-bottom:16px}
.colophon{margin-top:16px;border-top:4px double var(--ink);padding-top:8px}
.colophon .credits{font-family:"PT Sans",sans-serif;font-size:10.5px}
.colophon .made{margin-top:3px;font-family:"PT Sans",sans-serif;font-size:9.5px;color:var(--mut)}
.backpill{display:block;width:max-content;margin:10px auto 0;padding:7px 16px;border:1px solid var(--red);
border-radius:999px;color:var(--red);font-family:"PT Sans",sans-serif;font-weight:700;font-size:11px;
text-decoration:none;box-shadow:0 0 12px rgba(158,27,27,.2);transition:.25s}
.backpill:hover{background:var(--red);color:var(--paper)}
/* навигация */
.navbar{display:flex;align-items:center;gap:14px;padding:10px 0 2px;font-family:"PT Sans",sans-serif;
font-size:11px;letter-spacing:.1em;color:var(--mut)}
.navbar button{background:none;border:1px solid var(--line);color:var(--ink);width:34px;height:30px;
border-radius:4px;cursor:pointer;font-size:15px;line-height:1;transition:.2s}
.navbar button:hover{border-color:var(--red);color:var(--red);transform:translateX(1px)}
.navbar button:first-child:hover{transform:translateX(-1px)}
.dots{display:flex;gap:5px}
.dots span{width:7px;height:7px;border-radius:50%;background:#c9c2b2;transition:.25s}
.dots span.on{background:var(--red);transform:scale(1.25)}
.pageno{text-transform:uppercase}
/* мобиль: лист можно прокручивать внутри, обрезки нет */
@media(max-width:820px){
 body{padding:8px 6px}
 .stage{display:block}
 .sheet-wrap{width:100%!important;height:auto!important}
 .book{position:relative;width:100%!important;height:auto!important;transform:none!important;perspective:none}
 .page{position:relative;display:none;opacity:1;visibility:visible;transform:none!important;
 max-height:82vh;overflow-y:auto;box-shadow:0 6px 18px rgba(40,36,28,.18)}
 .page.cur{display:block}
 .page::after{display:none}
 .txt2{columns:1}
 .g-side,.g-side-rev,.briefs,.leadgrid{grid-template-columns:1fr}
}
"""

JS = """
(function(){
var pages=[].slice.call(document.querySelectorAll('.page'));
var dots=[].slice.call(document.querySelectorAll('.dots span'));
var label=document.getElementById('pageno');
var cur=0,busy=false;
function paint(){dots.forEach(function(d,i){d.classList.toggle('on',i===cur)});
label.textContent='Страница '+(cur+1)+' из '+pages.length;}
function go(n,dir){
 if(busy||n===cur||n<0||n>=pages.length)return;busy=true;
 var out=pages[cur],inn=pages[n];
 inn.classList.add(dir>0?'in-r':'in-l');
 void inn.offsetWidth;
 out.classList.add(dir>0?'out-l':'out-r');
 inn.classList.remove('in-r','in-l');inn.classList.add('cur');
 setTimeout(function(){out.classList.remove('cur','out-l','out-r');cur=n;paint();busy=false;},580);
}
window.sfnGo=function(d){go(cur+d,d)};
document.addEventListener('keydown',function(e){
 if(e.key==='ArrowRight'||e.key==='PageDown'){go(cur+1,1);e.preventDefault();}
 if(e.key==='ArrowLeft'||e.key==='PageUp'){go(cur-1,-1);e.preventDefault();}
 if(e.key==='Home'){go(0,-1);} if(e.key==='End'){go(pages.length-1,1);}});
var tx=null;
document.addEventListener('touchstart',function(e){tx=e.touches[0].clientX;},{passive:true});
document.addEventListener('touchend',function(e){if(tx===null)return;
 var dx=e.changedTouches[0].clientX-tx;tx=null;
 if(Math.abs(dx)>56){go(cur+(dx<0?1:-1),dx<0?1:-1);}},{passive:true});
paint();
})();
"""


def fig(key, alt, cap):
    return (f'<figure><div class="ph"><img src="{IMG[key]}" alt="{alt}"></div>'
            f'<figcaption>{cap}</figcaption></figure>')


def art(key, cls='g-side', stand=True, cols='txt'):
    a = A[key]
    st = f'<div class="stand">{a["s"]}</div>' if stand else ''
    txt = (f'<div class="kicker">{a["k"]}</div><h3>{a["t"]}</h3>{st}'
           f'<div class="{cols}">' + ''.join(f'<p>{p}</p>' for p in a['p']) + '</div>')
    ph = fig(key, a['alt'], a['cap'])
    if cls == 'g-side':
        return f'<article class="g-side"><div>{ph}</div><div>{txt}</div></article>'
    if cls == 'g-side-rev':
        return f'<article class="g-side-rev"><div>{txt}</div><div>{ph}</div></article>'
    return f'<article>{ph}{txt}</article>'


P = []
P.append("""<!DOCTYPE html>
<html lang="ru">
<head>
<!-- © 2026 San Fierro News / Jonny Wilde. Дизайн и вёрстка защищены: CC BY-NC-ND 4.0. Копирование и переработка запрещены. -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>San Fierro News — ежедневный выпуск по штату от 03.10.2026</title>
<meta name="description" content="Компактный ежедневный выпуск по штату San Andreas в четырёх полосах: гибель двоих полицейских на трассе под Лас-Вентурасом, торги за AngelPine Gas со ставкой $100 млн, военный КПП, вертолёт в тоннеле и яхта в парковом пруду — 12 кадров дня.">
<style>
""")
P.append(CSS)
P.append('</style>\n</head>\n<body>\n<div class="stage"><div class="sheet-wrap" id="sheet"><div class="book">\n')

# ---- полоса 1 ----
P.append('<section class="page page-1 cur">')
P.append('<div class="masttop"><span>Независимая редакция · штат San Andreas</span><span>суббота, 3 октября 2026</span></div>')
P.append('<div class="mastname">San Fierro <i>News</i></div>')
P.append('<div class="mastmeta"><span><b>№ 30</b></span><span>ежедневный выпуск</span><span>Лос-Сантос — Лас-Вентурас — трассы штата</span><span>12 материалов</span><span>4 полосы</span></div>')
P.append('<div class="mastcred">Кадры: Anna Malboro · Фоторедактор: Sonya Malboro · Текст/Редактор: Jonny Wilde</div>'
         '<div style="height:12px"></div>')
a = A['fallen']
P.append(f'<div class="kicker">{a["k"]}</div>')
P.append('<div class="leadgrid"><div>' + fig("fallen", a["alt"], a["cap"]) + '</div>'
         f'<div><h1>{a["t"]}</h1><div class="stand">{a["s"]}</div>'
         + '<div class="txt">' + ''.join(f'<p>{p}</p>' for p in a['p']) + '</div></div></div>')
P.append('<div class="briefs">')
for key in ('crash', 'gas', 'kpp'):
    b = A[key]
    P.append(f'<article><div class="kicker">{b["k"]}</div><h3>{b["t"]}</h3>'
             f'{fig(key, b["alt"], b["cap"])}'
             f'<div class="txt">' + ''.join(f'<p>{p}</p>' for p in b['p']) + '</div></article>')
P.append('</div></section>\n')

# ---- полоса 2 ----
P.append('<section class="page page-2">')
P.append('<div class="sechead"><span class="sq"></span><h2>Происшествия</h2><span class="pg">полоса 2</span></div>')
P.append(art('truck', 'g-side'))
P.append(art('square', 'g-side-rev'))
P.append(art('stop', 'g-side'))
P.append('</section>\n')

# ---- полоса 3 ----
P.append('<section class="page page-3">')
P.append('<div class="sechead"><span class="sq"></span><h2>Криминал · Экономика</h2><span class="pg">полоса 3</span></div>')
P.append(art('hwy', 'g-side'))
P.append(art('dragons', 'g-side-rev'))
P.append(art('caligula', 'g-side'))
P.append('</section>\n')

# ---- полоса 4 ----
P.append('<section class="page page-4">')
P.append('<div class="sechead"><span class="sq"></span><h2>Необычные истории</h2><span class="pg">полоса 4</span></div>')
P.append(art('heli', 'g-side-rev'))
P.append(art('yacht', 'g-side'))
P.append('<div class="colophon"><div class="credits">Кадры: Anna Malboro · Фоторедактор: Sonya Malboro · Текст/Редактор: Jonny Wilde</div>'
         '<div class="made">выпуск очереди подшивки · 03.10.2026 · дизайн и вёрстка — редакция San Fierro News</div>'
         '<a class="backpill" href="newsroom.html">← Посмотреть все выпуски редакции</a></div>')
P.append('</section>\n')

P.append('</div></div></div>\n')
P.append('<nav class="navbar"><button onclick="sfnGo(-1)" aria-label="Предыдущая страница">‹</button>'
         '<div class="dots">' + '<span></span>' * 4 + '</div>'
         '<span class="pageno" id="pageno">Страница 1 из 4</span>'
         '<button onclick="sfnGo(1)" aria-label="Следующая страница">›</button></nav>\n')
P.append(f'<script>{JS}</script>\n')
P.append('<script>(function(){var s=document.getElementById("sheet"),b=document.querySelector(".book");'
         'function fit(){var ah=window.innerHeight-92,aw=window.innerWidth-24;'
         'var k=Math.min(ah/1000,aw/720,1);k=Math.max(k,.5);'
         'if(window.innerWidth<=820){s.style.width="100%";s.style.height="auto";b.style.transform="none";return;}'
         's.style.width=(720*k)+"px";s.style.height=(1000*k)+"px";b.style.transform="scale("+k+")";}'
         'fit();window.addEventListener("resize",fit);})();</script>\n')
P.append('<!-- SFN · 2026 · 029 · compact-edition -->\n</body>\n</html>\n')

html = ''.join(P)
with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write(html)
words = sum(len((a['s'] + ' ' + ' '.join(a['p'])).split()) for a in A.values())
print(f'собрано v4: {OUT} · {len(html)//1024} КБ · полос: 4 · кадров: {len(IMG)} · слов в материалах: {words}')
