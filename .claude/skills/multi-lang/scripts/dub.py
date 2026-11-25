#!/usr/bin/env python3
"""Дубляж: dub.py видео segments.json tr_<lang>.json <lang> out.mp4 [--voice V] [--music f] [--voice-file f] [--no-subs]"""
import argparse, asyncio, json, os, subprocess, sys, tempfile

VOICES = {"en": "en-US-AndrewNeural", "ru": "ru-RU-DmitryNeural", "kk": "kk-KZ-DauletNeural",
          "es": "es-ES-AlvaroNeural", "de": "de-DE-ConradNeural", "fr": "fr-FR-HenriNeural",
          "pt": "pt-BR-AntonioNeural", "tr": "tr-TR-AhmetNeural", "uk": "uk-UA-OstapNeural",
          "ar": "ar-SA-HamedNeural", "hi": "hi-IN-MadhurNeural"}
MAX_SPEED = 1.35

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("segments"); ap.add_argument("tr")
ap.add_argument("lang"); ap.add_argument("out")
ap.add_argument("--voice"); ap.add_argument("--music"); ap.add_argument("--voice-file")
ap.add_argument("--no-subs", action="store_true")
a = ap.parse_args()

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]).decode())

def size(f):
    w, h = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0", f]).decode().strip().split(",")
    return int(w), int(h)

segs = json.load(open(a.segments))["segments"]
tr = {t["id"]: t["text"].strip() for t in json.load(open(a.tr))}
total = dur(a.video)
tmp = tempfile.mkdtemp()
voice = a.voice or VOICES.get(a.lang)
if not voice and not a.voice_file:
    sys.exit(f"Нет голоса по умолчанию для языка {a.lang}: укажи --voice или --voice-file")

async def tts_all(items):
    import edge_tts
    for i, text in items:
        await edge_tts.Communicate(text, voice).save(f"{tmp}/s{i}.mp3")

late = []
inputs, filters, labels = [], [], []
if a.voice_file:
    inputs += ["-i", a.voice_file]; labels.append("[1:a]")
    next_in = 2
else:
    ca = "/root/.ccr/ca-bundle.crt"
    if os.path.exists(ca):
        import certifi; certifi.where = lambda: ca
    items = [(s["id"], tr[s["id"]]) for s in segs if tr.get(s["id"])]
    asyncio.run(tts_all(items))
    next_in = 1
    for k, s in enumerate(segs):
        i = s["id"]
        if not tr.get(i): continue
        f = f"{tmp}/s{i}.mp3"
        d = dur(f)
        slot = (segs[k + 1]["start"] if k + 1 < len(segs) else total) - s["start"]
        speed = 1.0
        if d > slot:
            speed = min(d / slot, MAX_SPEED)
            d /= speed
            if d > slot + 0.05: late.append((i, round(d - slot, 1)))
        inputs += ["-i", f]
        ms = int(s["start"] * 1000)
        filt = f"atempo={speed:.3f}," if speed > 1.001 else ""
        filters.append(f"[{next_in}:a]{filt}adelay={ms}|{ms},apad[v{i}]")
        labels.append(f"[v{i}]"); next_in += 1
    labels = [l for l in labels]

n = len(labels)
fc = ";".join(filters + ([] if a.voice_file else []))
mix_in = "".join(labels)
chain = (fc + ";" if fc else "") + f"{mix_in}amix=inputs={n}:normalize=0,atrim=0:{total:.2f},volume=1.0[vo]"
if a.music:
    inputs += ["-stream_loop", "-1", "-i", a.music]
    chain += f";[{next_in}:a]volume=0.12,atrim=0:{total:.2f}[bg];[vo][bg]amix=inputs=2:normalize=0[aout]"
else:
    chain += ";[vo]anull[aout]"

vf = []
if not a.no_subs:
    w, h = size(a.video)
    ass = f"{tmp}/subs.ass"
    fs = int(min(w, h) * 0.055)
    def t(x):
        hh, rem = divmod(x, 3600); mm, ss = divmod(rem, 60)
        return f"{int(hh)}:{int(mm):02d}:{ss:05.2f}"
    lines = [f"[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\nWrapStyle: 0\n",
             "[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,Bold,Outline,Shadow,Alignment,MarginL,MarginR,MarginV",
             f"Style: D,DejaVu Sans,{fs},&H00FFFFFF,&H00000000,&H80000000,1,{max(2, fs//12)},0,2,{int(w*0.06)},{int(w*0.06)},{int(h*0.12)}\n",
             "[Events]\nFormat: Layer,Start,End,Style,Text"]
    for k, s in enumerate(segs):
        if not tr.get(s["id"]): continue
        end = segs[k + 1]["start"] if k + 1 < len(segs) else total
        end = min(end, s["start"] + 8)
        lines.append(f"Dialogue: 0,{t(s['start'])},{t(end)},D,{tr[s['id']]}")
    open(ass, "w").write("\n".join(lines))
    vf = ["-vf", f"ass={ass}"]
    cmd_v = ["-c:v", "libx264", "-crf", "20", "-preset", "medium"]
else:
    cmd_v = ["-c:v", "copy"]

run(["ffmpeg", "-y", "-i", a.video] + inputs + ["-filter_complex", chain, "-map", "0:v", "-map", "[aout]"]
    + vf + cmd_v + ["-c:a", "aac", "-b:a", "160k", "-shortest", a.out])
mb = os.path.getsize(a.out) / 1e6
print(f"готово: {a.out} ({mb:.1f} МБ)")
if late:
    print("Не влезли по времени (сократи перевод этих фраз): " + ", ".join(f"#{i} (+{d} с)" for i, d in late))
