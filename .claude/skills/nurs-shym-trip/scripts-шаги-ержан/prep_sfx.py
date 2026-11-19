# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
# Готовит профессиональные звуки из папки пользователя МОНТАЖ\ЗВУКИ: обрезка тишины, длина, затухание, пик -1 dBFS.
# Пишет a/sfx_pro/<имя>.wav и a/sfx_pro/peaks.json (где внутри файла пик — чтобы ставить пик ровно на событие).
import subprocess, json, os, numpy as np
B = r'C:\Users\<имя>\Desktop\МОНТАЖ\ЗВУКИ'
SP = os.path.join(B, 'Саунд Пак')
MAP = {  # имя в скилле: (файл, макс. длина, пик-выравнивание)
    'thud':  (os.path.join(SP, 'Transitions', 'TRANSITION 6.wav'), 0.9, False),
    'pop':   (os.path.join(SP, 'Digital_Analog', 'DIGITAL ANALOG 14.wav'), 0.45, False),
    'click': (os.path.join(SP, 'Digital_Analog', 'DIGITAL ANALOG 11.wav'), 0.4, False),
    'tick':  (os.path.join(SP, 'Digital_Analog', 'DIGITAL ANALOG 13.wav'), 0.5, False),
    'glitch':(os.path.join(SP, 'Digital_Analog', 'DIGITAL ANALOG 2.wav'), 0.7, False),
    'whoosh':(os.path.join(SP, 'Whooshes', 'WHOOSH 12.wav'), 1.4, True),
    'wipe':  (os.path.join(SP, 'Transitions', 'TRANSITION 2.wav'), 1.3, True),
    'boom':  (os.path.join(SP, 'Hits', 'HIT 7.wav'), 2.2, False),
}
SR = 48000
def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
os.makedirs('a/sfx_pro', exist_ok=True); peaks = {}
for name, (f, mx, align) in MAP.items():
    x = load(f); env = np.abs(x).max(1)
    on = np.argmax(env > env.max() * 0.03)          # начало звука
    x = x[max(0, on - int(0.005 * SR)):]
    x = x[:int(mx * SR)]
    n = len(x); fade = min(int(0.25 * SR), n // 3)
    x[n - fade:] *= np.linspace(1, 0, fade)[:, None]
    x /= np.abs(x).max() / 0.89                     # пик -1 dBFS
    pk = float(np.argmax(np.abs(x).max(1)) / SR) if align else 0.0
    peaks[name] = round(pk, 3)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', f'a/sfx_pro/{name}.wav'], input=x.astype(np.float32).tobytes())
    print(name, os.path.basename(f), f'{n / SR:.2f}s', 'peak@', peaks[name])
# переходы между сценами — те же кинематографичные вжухи cin1..3 (уже из Саунд Пак), пик в начале не выравниваем
for c in ('cin1', 'cin2', 'cin3'):
    x = load(f'a/sfx/{c}.wav'); x /= np.abs(x).max() / 0.89
    peaks[c] = round(float(np.argmax(np.abs(x).max(1)) / SR), 3)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', f'a/sfx_pro/{c}.wav'], input=x.astype(np.float32).tobytes())
json.dump(peaks, open('a/sfx_pro/peaks.json', 'w'))
print(peaks)
