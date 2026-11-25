#!/usr/bin/env python3
"""Видео -> segments.json: [{"id","start","end","text"}]. Бесплатно, на процессоре."""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

video, out = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else None
raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"])
audio = np.frombuffer(raw, dtype=np.float32)
model = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = model.transcribe(audio, language=lang, vad_filter=True)
res = []
for s in segs:
    t = s.text.strip()
    if t:
        res.append({"id": len(res), "start": round(s.start, 2), "end": round(s.end, 2), "text": t})
json.dump({"language": info.language, "segments": res}, open(out, "w"), ensure_ascii=False, indent=1)
print(f"язык: {info.language}, фраз: {len(res)}")
for r in res:
    print(f'{r["id"]:>3} {r["start"]:>6.1f}-{r["end"]:<6.1f} {r["text"]}')
