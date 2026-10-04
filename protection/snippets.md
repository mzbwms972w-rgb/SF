# SFN · Сниппеты защиты: куда и что вставлять

## 1. Копирайт-комментарий (в `<head>`, первой строкой после `<head>`)
Вставляется ОДИН РАЗ в каждый `template_*.html` и в `template_newsroom.html` —
дальше попадает во все будущие выпуски автоматически через сборщик.

```html
<!-- © 2026 San Fierro News / Jonny Wilde. Дизайн и вёрстка защищены: CC BY-NC-ND 4.0. Копирование и переработка запрещены. -->
```

Массовая вставка (запустить из корня репозитория):
```bash
python3 - <<'PY'
import glob,re
LINE='<head>\n<!-- © 2026 San Fierro News / Jonny Wilde. Дизайн и вёрстка защищены: CC BY-NC-ND 4.0. Копирование и переработка запрещены. -->'
for f in glob.glob('template_*.html'):
    s=open(f,encoding='utf-8').read()
    if 'CC BY-NC-ND' in s: continue
    s=s.replace('<head>',LINE,1)
    open(f,'w',encoding='utf-8').write(s)
    print('stamped',f)
PY
```

## 2. CSS-штамп выпуска (у каждого номера свой)
Ставится в собранный выпуск первой строкой внутри `<style>`, сразу после блока `@font-face`:

```css
/* SFN-DESIGN-028: roulette-noir-lv · 02.10.2026 */
```

В сборщике (`worktmp/build_*.py`) — токен `@@STAMP@@`, значение берём из сид-таблицы ниже.
Формат: `SFN-DESIGN-<NNN>: <slug> · <DD.MM.YYYY>`, NNN — трёхзначный номер из таблицы.

## 3. Невидимый маркер в теле (перед `</body>`)
```html
<!-- SFN · 2026 · 028 · roulette-noir-lv -->
```
Читатель не видит; копировщик, тянущий страницу целиком, уносит с собой.

## 4. Видимая строка в подвал (внутриигровой тон, без юридического жаргона)
Третьей строкой в `<footer>` каждого шаблона:
```html
дизайн и вёрстка — редакция San Fierro News
```
(в `template_lv_daily.html` это строка после `выпуск подшит в архив навсегда · 02.10.2026`).
RP-чистота соблюдена: никаких «лицензия/CC/copyright» в видимом тексте.

## 5. Сид-таблица номеров штампов (hub-порядок = порядок нумерации)
| NNN | файл | slug |
|---|---|---|
| 001 | index.html | chinatown-casino |
| 002 | driving-school.html | driving-school |
| 003 | caligulas-casino.html | caligula-neon |
| 004 | all-saints-hospital.html | all-saints |
| 005 | sf-police-raid.html | sf-raid |
| 006 | sf-army-base.html | sf-army |
| 007 | sfpd-precinct.html | sfpd-precinct |
| 008 | sfpd-patrol-falk.html | patrol-falk |
| 009 | daily-24-09-2026.html | mourning-editor |
| 010 | opg-leader-interview.html | padre-interview |
| 011 | wedding-ozzy-gulnara.html | wedding-malibu |
| 012 | zone51-investigation.html | zone51 |
| 013 | daily-26-09-2026.html | daily26 |
| 014 | daily-27-09-2026.html | daily27 |
| 015 | daily-28-09-2026.html | daily28 |
| 016 | fotoreport-comedy-club.html | comedy-club |
| 017 | fotoreport-tierra-robada.html | tierra-robada |
| 018 | fotoreport-warlocks-mc.html | warlocks-mc |
| 019 | fotoreport-avtobazar-lv.html | avtobazar-lv |
| 020 | fotoreport-city-hall.html | city-hall |
| 021 | fotoreport-four-dragons.html | four-dragons |
| 022 | fotoreport-evolve-hotel.html | five-stars-hotel |
| 023 | fotoreport-abandoned-airport.html | abandoned-airport |
| 024 | daily-30-09-2026.html | daily30-sf |
| 025 | article-lisa-akana.html | lisa-akana |
| 026 | daily-30-09-2026-los-santos.html | ls-postcards |
| 027 | socio-governor-poll.html | governor-poll |
| 028 | daily-02-10-2026-las-venturas.html | roulette-noir-lv |
| 029 | daily-03-10-2026.html | day-grid-tight |
| 030 | (следующий выпуск) | … |

Примечание форензики: номер 029 первоначально собран со слагом `state-broadsheet`;
после редизайна по брифу главреда (03.10.2026, пересборщик `worktmp/build_daily_0310_state_v2.py`)
слаг стал `classic-broadsheet`; после второго редизайна того же дня (пересборщик
`worktmp/build_daily_0310_state_v3.py` — интерактивная газета из 7 полос с перелистыванием)
действующий слаг — `interactive-pages`; после третьего редизайна того же дня (пересборщик
`worktmp/build_daily_0310_state_v4.py` — компактная газета из 4 полос, тексты −70…74% при сохранении
информации и подписей) действующий слаг — `compact-edition`; после четвёртого редизайна того же дня (пересборщик
`worktmp/build_daily_0310_state_v5.py` — вертикальная веб-газета без перелистывания, концепция
«городская документация Сан-Фиерро») действующий слаг — `street-folio`; после пятого редизайна того же дня (пересборщик
`worktmp/build_daily_0310_state_v6.py` — плакатная редакционная эстетика: цветовые поля, крупная
типографика Bebas Neue, номера материалов как графика) действующий слаг — `harbor-poster`; после композиционной правки 04.10.2026 (пересборщик
`worktmp/build_daily_0310_state_v7.py` — графитовый фон сайта, листы с границей и тенью, КПП как
боковой материал с цветной полосой, асимметричные сетки полос) действующий слаг — `graphite-press`; после арт-директорской правки 04.10.2026 (пересборщик
`worktmp/build_daily_0310_state_v8.py` — оболочка возвращена к v6, у каждого материала собственная
композиция, КПП как газетная колонка с колонными линейками) действующий слаг — `artdesk`; после конкурсной композиционной правки 04.10.2026 (пересборщик
`worktmp/build_daily_0310_state_v9.py` — full-bleed фото, якоря-номера у своих материалов, диптих-контраст,
плакатный вынос дословной фразы, ступенчатые лок-апы) действующий слаг — `prize-desk`.
Прежние имена жили до 03.10.2026.

Еженедельники нумеруемся отдельно: `SFN-WEEKLY-001` и т.д. (у них свой характер и свой шаблон).

## 6. Реестр сигнатурных имён (форензика переживает рефакторы)
Считаем отпечатками редакции (если встречаются чужой странице — это копипаста, а не «похожий стиль»):
`.marquee/.bulb`, `.signbase/.sl/.signpole`, `.jackpot/.jplab/.jpdate`, `.pcard/.corner/.crank/.csuit`,
`.standfirst`, `.plateline/.plate/.mapplate`, `.pullq`, `.chips/.tok/.tokw`, `.chron-grid/.chron-item`,
`.logbook/.logrow`, `.hubbtn`, `.tape/.tnum/.t-red/.t-blk/.t-zero`, `.mapframe/.pin/.pinprev/.pvplate`,
`.lvlegend`, `.tomap/.tomapline`, `.wxcard/.hocard/.wxbin/.hobin/.ho-min/.wx-min`, `.hostars/.hoday`,
`.sidestrip`, `.fin ttl/.fintext` (класс `.finttl`), `.factrow/.fact`, `.divider`, `.secno/.rubric/.rule`.
Пополнять реестр при каждом новом фирменном элементе; при рефакторе — не удалять записи,
а помечать датой «имя жило до …».

## 7. Ретро-штамповка опубликованных страниц (ТОЛЬКО по команде «ретро-штампуй»)
Комментарий + маркер не меняют вид, но меняют байты 28 файлов; URLs остаются вечными.
Делается одним коммитом скриптом (добавляет блоки §1 и §3 по номеру из таблицы), после чего
сразу коммит + тег + манифест.
