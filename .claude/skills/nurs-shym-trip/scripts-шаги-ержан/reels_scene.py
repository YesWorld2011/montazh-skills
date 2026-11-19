# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
# Сцена «охват»: 5 превью рилсов (2 сверху, 3 снизу) по референсу «реф ерж»: тёмный фон с размытой копией,
# карточки со скруглёнными углами въезжают по одной снизу с наклоном и выпрямляются, потом проявляются тонкие градиентные обводки.
f = 'video-perehod.html'; s = open(f, encoding='utf-8').read()
a = s.index('  <!-- 6.'); b = s.index('  <!-- 7.')
W = 'data-wdur="0.6" data-wdy="48" data-wblur="16"'
def card(i, x, y, w, h, tin, rot):
    return (f'    <div class="rcard abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px" data-in="{tin}" data-fx="pop" data-from="bottom" data-dist="180" data-rot="{rot}" data-dur="0.55" data-float="4">'
            f'<img src="media/reels/{i}.jpg"></div>\n'
            f'    <div class="rline abs" style="left:{x - 6}px;top:{y - 6}px;width:{w + 12}px;height:{h + 12}px" data-in="1.55" data-fx="blur" data-dur="0.5"></div>\n')
cards = ''
# верх: 2 карточки, низ: 3 карточки (ширина 360 / 300, пропорция 9:16)
cards += card(1, 150, 150, 360, 640, 0.05, -8)
cards += card(2, 570, 150, 360, 640, 0.25, 7)
cards += card(3, 40, 1150, 300, 533, 0.45, -7)
cards += card(4, 390, 1150, 300, 533, 0.62, 6)
cards += card(5, 740, 1150, 300, 533, 0.78, -6)
new = f'''  <!-- 6. И соответственно рилсыма көбірек охват жинаймын — 5 рилсов с просмотрами (как в референсе «реф ерж»): 2 сверху, 3 снизу, обводки-линии -->
  <section class="scene full" data-s="12.36" data-e="14.86" data-push="0.03" data-tr="none" data-sfx="none" style="--bg:#070707">
    <img class="abs" src="media/reels/2.jpg" style="left:-200px;top:-100px;width:1480px;height:2120px;object-fit:cover;filter:blur(60px) brightness(.32) saturate(1.1)">
    <div class="abs" style="inset:0;background:radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 0%, rgba(0,0,0,.55) 75%)"></div>
{cards}    <div class="hw cx" style="top:812px;font-size:64px" data-in="0.05" data-fx="words" {W} data-w="0.05 0.72 1.02">и соответственно рилсыма</div>
    <div class="yb cx" style="top:888px;font-size:210px" data-in="1.24" data-fx="words" {W} data-w="1.24 1.78">көбірек охват</div>
  </section>

'''
s = s[:a] + new + s[b:]
# стили карточек и линий
css = '''  .rcard { border-radius: 34px; overflow: hidden; background: #111; box-shadow: 0 30px 70px rgba(0,0,0,.55); }
  .rcard img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .rline { border-radius: 40px; padding: 4px; background: linear-gradient(140deg, #ff6fae 0%, #FFE81A 45%, #9a7bff 100%);
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor; mask-composite: exclude;
    filter: drop-shadow(0 0 10px rgba(255,200,120,.45)); }
</style>'''
s = s.replace('</style>', css, 1)
# убрать скрипт графика (графика больше нет)
i0 = s.find('/* график «охват»'); i1 = s.find('})();', i0)
if i0 > 0: s = s[:i0] + s[i1 + 5:]
open(f, 'w', encoding='utf-8').write(s); print('ok')
