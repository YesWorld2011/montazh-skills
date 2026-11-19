# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
# Мастер v3: из мастера v2 (media/frames, media/mask, media/voice2.wav) убираем 2 микропаузы:
# перед «бірақ» (кадры 506–507, 16.867–16.933) и между «жіберемін» и «let's go» (кадры 657–660, 21.9–22.033).
import os, shutil, subprocess, numpy as np
FPS = 30; CUTS = [(506, 508), (657, 661)]
for d in ('frames3', 'mask3'): os.makedirs(f'media/{d}', exist_ok=True)
fr = sorted(os.listdir('media/frames')); mk = sorted(os.listdir('media/mask'))
keep = [i for i in range(len(fr)) if not any(a <= i < b for a, b in CUTS)]
for k, i in enumerate(keep):
    shutil.copyfile(f'media/frames/{fr[i]}', f'media/frames3/{k + 1:05d}.jpg')
    shutil.copyfile(f'media/mask/{mk[i]}', f'media/mask3/{k + 1:05d}.png')
N = len(keep); print('frames', N, N / FPS)
SR = 48000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'media/voice2.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
v = np.frombuffer(raw, np.float32).copy()
v = np.concatenate([v, np.zeros(max(0, int(len(fr) / FPS * SR) - len(v)), np.float32)])
segs, prev = [], 0
for a, b in CUTS:
    segs.append(v[int(prev / FPS * SR):int(a / FPS * SR)]); prev = b
segs.append(v[int(prev / FPS * SR):])
fade = int(0.006 * SR); out = segs[0]
for s in segs[1:]:
    x = min(fade, len(out), len(s))
    out = np.concatenate([out[:-x], out[-x:] * np.linspace(1, 0, x) + s[:x] * np.linspace(0, 1, x), s[x:]])
out = out[:int(N / FPS * SR)]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', 'media/voice3.wav'], input=out.astype(np.float32).tobytes(), check=True)
print('voice', len(out) / SR)
# звук wipe-переходов из «рилс ержан» — кусок до голоса (1.25–2.60), только звук
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.25', '-t', '1.38', '-i', 'media/src_ex.mp4', '-vn', '-ac', '2', '-ar', str(SR),
                '-af', 'afade=t=in:d=0.02,afade=t=out:st=1.18:d=0.2', 'a/sfx_pro/wipeset.wav'], check=True)
print('wipe sound ok')
