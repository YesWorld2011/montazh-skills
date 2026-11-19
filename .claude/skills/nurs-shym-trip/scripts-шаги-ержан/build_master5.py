# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
# Мастер v5: убираем паузу 0.2 c перед «бұл wipe transition» (кадры 77–82, 2.567–2.767) из кадров, масок и голоса.
import os, shutil, subprocess, numpy as np
FPS = 30; A, B = 77, 83
for d in ('frames5', 'mask5'): os.makedirs(f'media/{d}', exist_ok=True)
fr = sorted(os.listdir('media/frames')); mk = sorted(os.listdir('media/mask'))
keep = [i for i in range(len(fr)) if not (A <= i < B)]
for k, i in enumerate(keep):
    shutil.copyfile(f'media/frames/{fr[i]}', f'media/frames5/{k + 1:05d}.jpg')
    shutil.copyfile(f'media/mask/{mk[i]}', f'media/mask5/{k + 1:05d}.png')
N = len(keep); print('frames', N, N / FPS)
SR = 48000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'media/voice4.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
v = np.frombuffer(raw, np.float32).copy()
out = np.concatenate([v[:int(A / FPS * SR)], v[int(B / FPS * SR):]])[:int(N / FPS * SR)]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', 'media/voice5.wav'], input=out.astype(np.float32).tobytes(), check=True)
print('voice', len(out) / SR)
