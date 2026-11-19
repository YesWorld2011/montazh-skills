# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
# Все жёлтые и белые слова — по одному, плавно снизу вверх (words + длиннее всплытие).
import re
f = 'video-perehod.html'; s = open(f, encoding='utf-8').read()
# одиночные белые слова с blur -> words (одно слово, его время = data-in)
def to_words(m):
    tag = m.group(0); din = re.search(r'data-in="([\d.]+)"', tag).group(1)
    return tag.replace('data-fx="blur"', f'data-fx="words" data-w="{din}"')
s = re.sub(r'<div class="hw[^"]*"[^>]*data-fx="blur"[^>]*>', to_words, s)
# плавность для всех words
s = re.sub(r'data-fx="words"(?![^>]*data-wdur)', 'data-fx="words" data-wdur="0.6" data-wdy="48" data-wblur="16"', s)
open(f, 'w', encoding='utf-8').write(s)
print(s.count('data-wdur'))
