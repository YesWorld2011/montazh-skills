# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
import sys, wave, numpy as np
from faster_whisper import WhisperModel
w = wave.open(sys.argv[1]); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
m = WhisperModel('large-v3', device='cpu', compute_type='int8')
ranges = [(248, 276), (282, 291), (307, 342), (351, 381), (384, 411), (491, 541), (551, 618), (621, 633)]
out = open(sys.argv[2], 'w', encoding='utf-8')
for s0, s1 in ranges:
    t = s0
    while t < s1:
        e = min(t + 12, s1)
        seg = a[int(t * 16000):int(e * 16000)]
        if np.sqrt(np.mean(seg ** 2)) > 0.004:
            for lang in ('ru', 'kk'):
                segs, _ = m.transcribe(seg, language=lang, word_timestamps=True, beam_size=5, condition_on_previous_text=False)
                for s in segs:
                    ws = ' '.join(f'{x.word.strip()}@{t + x.start:.2f}-{t + x.end:.2f}' for x in s.words)
                    out.write(f'{lang} [{t + s.start:.2f}-{t + s.end:.2f}] {s.text} || {ws}\n'); out.flush()
        t = e
