#!/usr/bin/env python3
"""Своя библиотека архивных фото (только общественное достояние / CC0), чтобы не ждать Wikimedia.

  python3 tools/photolib.py import work/<ролик> "тег1,тег2"   забрать фото из готового проекта (по CREDITS.txt)
  python3 tools/photolib.py find лес                           найти фото по тегу/слову -> путь для story.json
  python3 tools/photolib.py sheet [тег] out.png                лист-превью (весь каталог или по тегу)
  python3 tools/photolib.py harvest terms.txt                  медленно (раз в 45 с) докачать в library/inbox по 2 фото на запрос
  python3 tools/photolib.py approve <имя> "теги"               перенести фото из inbox в библиотеку
  python3 tools/photolib.py reject <имя>                       удалить из inbox

В story.json:  "имя": {"file": "../../library/photos/<имя>.jpg", "cut": false, "dots": false}
"""
import json, os, re, shutil, sys, time
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "library")
CAT = os.path.join(LIB, "catalog.json")
ENGINE = os.path.join(ROOT, ".claude/skills/paper-history/engine")


def load():
    return json.load(open(CAT, encoding="utf-8")) if os.path.exists(CAT) else {}


def save(c):
    json.dump(c, open(CAT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)


def shrink(src, dst, side=1400):
    im = Image.open(src).convert("RGB")
    im.thumbnail((side, side))
    im.save(dst, "JPEG", quality=85)


def parse_credits(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"([^:]+): (File:.+?) \| (.*?) \| (.*?) \| (\S+)", line.strip())
        if m:
            out[m.group(1)] = dict(commons=m.group(2), author=m.group(3), license=m.group(4), url=m.group(5))
    return out


def do_import(proj, tags):
    c = load()
    slug = os.path.basename(os.path.normpath(proj))
    for fn, meta in parse_credits(os.path.join(proj, "CREDITS.txt")).items():
        src = os.path.join(proj, "sources", fn)
        if not os.path.exists(src):
            continue
        name = f"{slug}-{os.path.splitext(fn)[0]}"
        shrink(src, os.path.join(LIB, "photos", name + ".jpg"))
        c[name] = dict(meta, tags=[t.strip() for t in tags.split(",") if t.strip()], from_video=slug)
        print("+", name)
    save(c)


def find(q):
    q = q.lower()
    for k, v in load().items():
        hay = " ".join([k, v.get("commons", ""), " ".join(v.get("tags", []))]).lower()
        if q in hay:
            print(f"{k:28} ../../library/photos/{k}.jpg   [{', '.join(v.get('tags', []))}]")


def sheet(tag, out, folder="photos", cat=None):
    items = []
    if folder == "photos":
        for k, v in load().items():
            if not tag or tag.lower() in " ".join([k] + v.get("tags", [])).lower():
                items.append((k, os.path.join(LIB, "photos", k + ".jpg")))
    else:
        for f in sorted(os.listdir(os.path.join(LIB, folder))):
            if f.endswith(".jpg"):
                items.append((f[:-4], os.path.join(LIB, folder, f)))
    if not items:
        print("пусто"); return
    W, H, cols = 300, 260, 4
    rows = (len(items) + cols - 1) // cols
    sh = Image.new("RGB", (W * cols, H * rows), (30, 30, 30))
    d = ImageDraw.Draw(sh)
    for i, (k, p) in enumerate(items):
        im = Image.open(p); im.thumbnail((W - 10, H - 40))
        x, y = (i % cols) * W, (i // cols) * H
        sh.paste(im, (x + 5, y + 5)); d.text((x + 5, y + H - 30), k[:40], fill=(230, 230, 230))
    sh.save(out); print(out)


def harvest(terms_file):
    sys.path.insert(0, ENGINE)
    import fetch
    inbox = os.path.join(LIB, "inbox")
    meta_p = os.path.join(inbox, "inbox.json")
    meta = json.load(open(meta_p, encoding="utf-8")) if os.path.exists(meta_p) else {}
    for line in open(terms_file, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        term, _, tags = line.partition("|")
        try:
            cands = fetch.search(term.strip(), limit=12)
        except Exception as e:
            print("search fail", term, e); time.sleep(120); continue
        got = 0
        for cnd in cands:
            if got >= 2:
                break
            title = cnd.get("title") if isinstance(cnd, dict) else None
            if not title or title in [m.get("commons") for m in meta.values()]:
                continue
            name = re.sub(r"[^a-z0-9]+", "-", (term.strip() + f" {got + 1}").lower()).strip("-")
            tmp = os.path.join(inbox, name + ".orig")
            try:
                fetch.get(title, tmp, credits=os.path.join(inbox, "CREDITS.txt"))
                shrink(tmp, os.path.join(inbox, name + ".jpg")); os.remove(tmp)
                meta[name] = dict(commons=title, tags=[t.strip() for t in tags.split(",") if t.strip()], term=term.strip())
                json.dump(meta, open(meta_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                print("+", name, title); got += 1
            except BaseException as e:
                print("skip", title, str(e)[:80])
                if os.path.exists(tmp): os.remove(tmp)
            time.sleep(45)
        time.sleep(45)


def approve(name, tags):
    inbox = os.path.join(LIB, "inbox"); meta = json.load(open(os.path.join(inbox, "inbox.json"), encoding="utf-8"))
    c = load(); m = meta.pop(name)
    cred = {v["commons"]: v for v in parse_credits(os.path.join(inbox, "CREDITS.txt")).values()}.get(m["commons"], {})
    shutil.move(os.path.join(inbox, name + ".jpg"), os.path.join(LIB, "photos", name + ".jpg"))
    c[name] = dict(cred or {"commons": m["commons"]}, tags=[t.strip() for t in tags.split(",")] if tags else m["tags"])
    save(c); json.dump(meta, open(os.path.join(inbox, "inbox.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ok", name)


def reject(name):
    inbox = os.path.join(LIB, "inbox"); p = os.path.join(inbox, "inbox.json")
    meta = json.load(open(p, encoding="utf-8")); meta.pop(name, None)
    json.dump(meta, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if os.path.exists(os.path.join(inbox, name + ".jpg")): os.remove(os.path.join(inbox, name + ".jpg"))
    print("removed", name)


if __name__ == "__main__":
    a = sys.argv[1:]
    {"import": lambda: do_import(a[1], a[2] if len(a) > 2 else ""),
     "find": lambda: find(a[1]),
     "sheet": lambda: sheet(a[1] if len(a) > 2 else "", a[-1]),
     "inbox": lambda: sheet("", a[1], folder="inbox"),
     "harvest": lambda: harvest(a[1]),
     "approve": lambda: approve(a[1], a[2] if len(a) > 2 else ""),
     "reject": lambda: reject(a[1])}[a[0]]()
