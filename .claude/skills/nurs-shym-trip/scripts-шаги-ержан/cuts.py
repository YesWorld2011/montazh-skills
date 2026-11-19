# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
import sys, json, wave, numpy as np
w = wave.open(sys.argv[1]); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
SR = 16000; H = 160  # 10 ms
WIN = [(163.85, 165.3), (179.9, 182.2), (244.28, 247.7), (284.88, 287.7), (347.9, 351.3),
       (364.06, 366.9), (446.55, 449.02), (454.0, 457.1), (507.6, 511.6), (628.2, 629.2)]
PRE, POST, MAXGAP, KEEPGAP = 0.07, 0.14, 0.32, 0.18
out = []
for s0, s1 in WIN:
    x = a[int(s0 * SR):int(s1 * SR)]
    n = len(x) // H
    rms = np.sqrt(np.mean(x[:n * H].reshape(n, H) ** 2, axis=1))
    db = 20 * np.log10(rms + 1e-9)
    thr = max(db.max() - 32, np.percentile(db, 10) + 6)
    on = db > thr
    # fill tiny holes (<60ms) / remove blips (<50ms)
    idx = np.where(on)[0]
    st, en = idx[0], idx[-1]
    # find inner silences
    runs = []; i = st
    while i <= en:
        if not on[i]:
            j = i
            while j <= en and not on[j]: j += 1
            runs.append((i, j)); i = j
        else: i += 1
    parts = []; cur = max(0, st * 0.01 - PRE)
    for i, j in runs:
        g = (j - i) * 0.01
        if g > MAXGAP:
            mid_end = i * 0.01 + KEEPGAP / 2
            parts.append((cur, mid_end)); cur = j * 0.01 - KEEPGAP / 2
    parts.append((cur, min((s1 - s0), en * 0.01 + POST)))
    for p, q in parts:
        out.append([round(s0 + p, 3), round(s0 + q, 3)])
    sys.stderr.write(f'{s0}-{s1}: thr {thr:.1f} speech {s0+st*0.01:.2f}-{s0+en*0.01:.2f} parts {[(round(s0+p,2), round(s0+q,2)) for p,q in parts]}\n')
json.dump(out, open(sys.argv[2], 'w'))
print('total', round(sum(q - p for p, q in out), 2), 'pieces', len(out))
