# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
# Новый мастер: из экспорта CapCut убираем 2 паузы и дотягиваем «go» из исходника FX3 (те же LUT пользователя).
# Кадры 30 fps -> media/frames2, голос -> media/voice2.wav
import os, shutil, subprocess, numpy as np, cv2
FPS = 30
CUTS = [(273, 277), (511, 515)]          # индексы кадров (t*30), которые выкидываем: 9.100–9.233 и 17.033–17.167
os.makedirs('media/frames2', exist_ok=True)
src = sorted(os.listdir('media/frames'))  # 00001.jpg = t 0
keep = [i for i in range(len(src)) if not any(a <= i < b for a, b in CUTS)]
for k, i in enumerate(keep):
    shutil.copyfile(f'media/frames/{src[i]}', f'media/frames2/{k + 1:05d}.jpg')
n0 = len(keep)
# хвост: 629.20–629.50 из FX3, LUT SLog3→709 + Kodak 2383, подгонка среднего/контраста к последнему кадру экспорта
TAIL = 9
tmp = 'media/tail'; os.makedirs(tmp, exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '629.20', '-t', f'{TAIL / FPS:.3f}', '-i', r'C:\Users\<имя>\Desktop\ержан\FX3_1574.MP4', '-an',
                '-vf', 'fps=30,scale=1080:1920,format=rgb48le,lut3d=a/lut1.cube,lut3d=a/lut2.cube,format=rgb24', f'{tmp}/%05d.png'], check=True)
ref = cv2.imdecode(np.fromfile(f'media/frames/{src[-1]}', np.uint8), cv2.IMREAD_COLOR).astype(np.float32)
tf = sorted(os.listdir(tmp))
first = cv2.imread(f'{tmp}/{tf[0]}').astype(np.float32)
mr, sr = ref.reshape(-1, 3).mean(0), ref.reshape(-1, 3).std(0)
mf, sf = first.reshape(-1, 3).mean(0), first.reshape(-1, 3).std(0)
for j, name in enumerate(tf[:TAIL]):
    im = cv2.imread(f'{tmp}/{name}').astype(np.float32)
    im = (im - mf) * (sr / sf) + mr
    cv2.imencode('.jpg', np.clip(im, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])[1].tofile(f'media/frames2/{n0 + j + 1:05d}.jpg')
N = n0 + TAIL
print('frames', N, 'dur', N / FPS)
# голос: экспорт без двух пауз (короткие склейки 6 мс) + хвост из FX3, уровень подогнан
SR = 48000
def load(args):
    raw = subprocess.run(['ffmpeg', '-v', 'error', *args, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
v = load(['-i', 'media/source.mp4'])
segs, prev = [], 0
for a, b in CUTS:
    segs.append(v[int(prev / FPS * SR):int(a / FPS * SR)]); prev = b
segs.append(v[int(prev / FPS * SR):int(691 / FPS * SR)])
tail = load(['-ss', '629.20', '-t', f'{TAIL / FPS:.3f}', '-i', r'C:\Users\<имя>\Desktop\ержан\FX3_1574.MP4'])
ref_rms = np.sqrt(np.mean(v[int(22.88 * SR):int(23.02 * SR)] ** 2))
src_rms = np.sqrt(np.mean(load(['-ss', '629.06', '-t', '0.14', '-i', r'C:\Users\<имя>\Desktop\ержан\FX3_1574.MP4']) ** 2))
tail *= ref_rms / max(src_rms, 1e-6)
fade = int(0.006 * SR)
out = segs[0]
for s in segs[1:] + [tail]:
    s = s.copy(); x = min(fade, len(out), len(s))
    out = np.concatenate([out[:-x], out[-x:] * np.linspace(1, 0, x) + s[:x] * np.linspace(0, 1, x), s[x:]])
end = int(N / FPS * SR); out = out[:end]
out[-int(0.08 * SR):] *= np.linspace(1, 0, int(0.08 * SR))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', 'media/voice2.wav'], input=out.astype(np.float32).tobytes(), check=True)
print('voice', len(out) / SR)
