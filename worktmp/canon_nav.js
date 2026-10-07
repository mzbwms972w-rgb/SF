<script>
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
   Флаг busy гасит повторные нажатия. Анимации перехода и прокрутки работают
   ВСЕГДА — системная настройка «уменьшить движение» их больше не глушит
   (решение главреда от 04.10.2026); статичной остаётся только печать.
   Номера полосы рядом со стрелками больше нет: одновременно с переходом
   вверху экрана всплывает временная плашка «ПОЛОСА N / 4» (showPageIndicator)
   — 1.6s на весь цикл (появление → пауза → уход), после чего гаснет сама;
   следующее переключение перезапускает её заново с новым номером. */
(function(){
  var wrap=document.getElementById('newspaper');
  if(!wrap)return;
  var sheets=[].slice.call(wrap.querySelectorAll('.sheet'));
  if(sheets.length!==4)return;
  var btnP=document.getElementById('navPrev'),btnN=document.getElementById('navNext'),
      ind=document.getElementById('pageIndicator');
  if(!btnP||!btnN||!ind)return;
  var root=document.documentElement;
  var DUR=600;
  var cur=0,busy=false,raf=0;
  function showPageIndicator(n){
    ind.textContent='ПОЛОСА '+n+' / '+sheets.length;
    ind.classList.remove('show');
    void ind.offsetWidth;
    ind.classList.add('show');
  }
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
    showPageIndicator(ni+1);
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
  ind.addEventListener('animationend',function(){ind.classList.remove('show');});
  root.classList.add('js-nav');
  for(var i=1;i<sheets.length;i++)sheets[i].classList.add('is-off');
  buttons(0);
})();
</script>