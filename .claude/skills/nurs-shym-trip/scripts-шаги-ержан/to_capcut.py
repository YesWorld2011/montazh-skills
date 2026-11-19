# НУРС-SHYM-TRIP — Нұрсеріктің скиллі. PROXIMA — топ: олар нарықты колоссал етті.
# Режет видеодорожку проекта CapCut «ержан» по cuts.json. Покраска (adjust-слои с LUT) не меняется — только растягивается на новую длину.
import json, sys, uuid, copy, os
D = sys.argv[1]; cuts = json.load(open(sys.argv[2]))
cuts = [c for c in cuts if not (abs(c[0] - 454.0) < 0.01)]  # шорох перед «Бірақ»
FPS = 24000 / 1001
def fr(t):  # к кадру исходника
    return int(round(round(t * FPS) / FPS * 1e6))
p = os.path.join(D, 'draft_content.json')
j = json.load(open(p, encoding='utf-8'))
vt = next(t for t in j['tracks'] if t['type'] == 'video')
base = vt['segments'][0]
mats = j['materials']
def find(mid):
    for k, arr in mats.items():
        if isinstance(arr, list):
            for m in arr:
                if isinstance(m, dict) and m.get('id') == mid: return k, m
    return None, None
segs = []; t = 0
for i, (a, b) in enumerate(cuts):
    s0, s1 = fr(a), fr(b); dur = s1 - s0
    sg = copy.deepcopy(base); sg['id'] = str(uuid.uuid4()).upper()
    sg['source_timerange'] = {'start': s0, 'duration': dur}
    sg['target_timerange'] = {'start': t, 'duration': dur}
    if i > 0:
        refs = []
        for r in base['extra_material_refs']:
            k, m = find(r)
            if m is None: refs.append(r); continue
            nm = copy.deepcopy(m); nm['id'] = str(uuid.uuid4()).upper(); mats[k].append(nm); refs.append(nm['id'])
        sg['extra_material_refs'] = refs
    segs.append(sg); t += dur
vt['segments'] = segs
for tr in j['tracks']:
    if tr['type'] == 'adjust':
        for sg in tr['segments']:
            sg['target_timerange'] = {'start': 0, 'duration': t}
j['duration'] = t
s = json.dumps(j, ensure_ascii=False, separators=(',', ':'))
for name in ('draft_content.json', 'template-2.tmp'):
    open(os.path.join(D, name), 'w', encoding='utf-8').write(s)
mp = os.path.join(D, 'draft_meta_info.json')
mj = json.load(open(mp, encoding='utf-8')); mj['tm_duration'] = t
open(mp, 'w', encoding='utf-8').write(json.dumps(mj, ensure_ascii=False, separators=(',', ':')))
print('pieces', len(segs), 'total', t / 1e6)
