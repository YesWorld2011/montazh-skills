# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
# B-roll (блокнот TRAVEL → перелистывание → FASHION) под таймлайн сцены 6.92–9.08 (30 fps, 65 кадров).
# travel на 6.94, страница FASHION ложится на 7.66, дальше FASHION медленно (0.5x) до конца — под надпись COMMERCIAL.
import os, cv2, numpy as np
src = sorted(os.listdir('media/broll_src'))
S = lambda i: os.path.join('media/broll_src', src[min(i, len(src) - 1)])
seq = []
seq += [round(i * 11 / 17) for i in range(18)]      # TRAVEL, 0.6 c, замедленно
seq += [12, 14, 16, 18, 20]                          # перелистывание, реальная скорость
seq += [22 + j for j in range(42)]                   # FASHION, 0.5x
for k, i in enumerate(seq):
    im = cv2.imdecode(np.fromfile(S(i), np.uint8), cv2.IMREAD_COLOR)
    cv2.imencode('.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 92])[1].tofile(f'media/broll/{k + 1:05d}.jpg')
print(len(seq), 'frames')
