# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
# Мастер v4: после хука (1.2 c) вставляем окно 41 кадр (1.367 c) под демонстрацию wipe-переходов — там нет голоса спикера.
# Кадры/маски в окне — копия кадра хука (их закрывает B-roll), голос — тишина. Остальное сдвигается на +1.367 c.
import os, shutil, subprocess, numpy as np
FPS = 30; AT = 36; GAP = 41
for d in ('frames4', 'mask4'): os.makedirs(f'media/{d}', exist_ok=True)
fr = sorted(os.listdir('media/frames')); mk = sorted(os.listdir('media/mask'))
order = list(range(AT)) + [AT] * GAP + list(range(AT, len(fr)))
for k, i in enumerate(order):
    shutil.copyfile(f'media/frames/{fr[i]}', f'media/frames4/{k + 1:05d}.jpg')
    shutil.copyfile(f'media/mask/{mk[i]}', f'media/mask4/{k + 1:05d}.png')
N = len(order); print('frames', N, N / FPS)
SR = 48000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'media/voice3.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
v = np.frombuffer(raw, np.float32).copy(); c = int(AT / FPS * SR); f = int(0.01 * SR)
a, b = v[:c].copy(), v[c:].copy(); a[-f:] *= np.linspace(1, 0, f); b[:f] *= np.linspace(0, 1, f)
out = np.concatenate([a, np.zeros(int(GAP / FPS * SR), np.float32), b])[:int(N / FPS * SR)]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', 'media/voice4.wav'], input=out.astype(np.float32).tobytes(), check=True)
print('voice', len(out) / SR)
# B-roll демонстрации: их 1.25–2.617 (до голоса), 41 кадр, в реальной скорости; звук — тот же кусок
d = 'media/ex_wipe'
for x in os.listdir(d): os.remove(os.path.join(d, x))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.25', '-t', f'{GAP / FPS:.4f}', '-i', 'media/src_ex.mp4', '-an', '-vf', 'scale=1080:1920,fps=30,format=yuvj420p', '-q:v', '2', f'{d}/%05d.jpg'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.25', '-t', f'{GAP / FPS + 0.05:.4f}', '-i', 'media/src_ex.mp4', '-vn', '-ac', '2', '-ar', str(SR),
                '-af', 'afade=t=in:d=0.01,afade=t=out:st=1.33:d=0.08', 'a/sfx_pro/wipeset.wav'], check=True)
print('ex_wipe', len(os.listdir(d)))
