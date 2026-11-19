# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
import sys, json, wave, numpy as np
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
w = wave.open(src); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
m = WhisperModel('large-v3', device='cpu', compute_type='int8')
segs, _ = m.transcribe(a, word_timestamps=True, language='kk', beam_size=5, vad_filter=True,
                       vad_parameters=dict(min_silence_duration_ms=400),
                       condition_on_previous_text=False,
                       initial_prompt='Бұл wipe-транзишн, переход. Контент-мейкерлер, travel, fashion, коммерциялық роликтер, рилстар, комментарийге.')
W = []; log = open(out + '.txt', 'w', encoding='utf-8')
for s in segs:
    log.write(f'[{s.start:.2f}-{s.end:.2f}] {s.text}\n'); log.flush()
    W += [[x.word.strip(), round(x.start, 2), round(x.end, 2)] for x in s.words]
open(out, 'w', encoding='utf-8').write(json.dumps(W, ensure_ascii=False))
