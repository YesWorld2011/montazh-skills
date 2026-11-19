# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
import sys, json, wave, numpy as np
from faster_whisper import WhisperModel
sys.stdout.reconfigure(encoding='utf-8')
w = wave.open(sys.argv[1]); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
cuts = json.load(open(sys.argv[2])); SR = 16000
m = WhisperModel('large-v3', device='cpu', compute_type='int8')
# each piece separately with 0.0 padding, plus whole line glued
for p, q in cuts:
    x = a[int(p * SR):int(q * SR)]
    segs, _ = m.transcribe(np.concatenate([np.zeros(8000, np.float32), x, np.zeros(8000, np.float32)]), language='kk', word_timestamps=True, beam_size=5, condition_on_previous_text=False)
    t = ' '.join(f'{wd.word.strip()}({wd.start-0.5:.2f}-{wd.end-0.5:.2f})' for s in segs for wd in s.words)
    print(f'{p:.2f}-{q:.2f} [{q-p:.2f}] {t}', flush=True)
glued = np.concatenate([a[int(p * SR):int(q * SR)] for p, q in cuts])
wave_out = wave.open(sys.argv[3], 'wb'); wave_out.setnchannels(1); wave_out.setsampwidth(2); wave_out.setframerate(SR)
wave_out.writeframes((glued * 32767).astype(np.int16).tobytes()); wave_out.close()
segs, _ = m.transcribe(glued, language='kk', beam_size=5, condition_on_previous_text=False)
print('GLUED:', ' '.join(s.text for s in segs))
