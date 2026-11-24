#!/usr/bin/env python3
"""Бесплатная статистика YouTube без ключей и без vidIQ (публичные данные через yt-dlp).

  python3 tools/yt_free.py mine                 просмотры наших Shorts + запись в stats/history.csv (рост за период)
  python3 tools/yt_free.py outliers @a @b ...   ролики конкурентов, которые набрали в N раз больше медианы своего канала
  python3 tools/yt_free.py find "запрос"         поиск Shorts по теме -> каналы -> их аутлайеры
"""
import csv, datetime as dt, json, os, statistics, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MINE = "https://www.youtube.com/@bylo_na_samom_dele/shorts"
HIST = os.path.join(ROOT, "stats", "history.csv")


def flat(url, n=40):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "--playlist-end", str(n), "-J", url],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not r.stdout.strip():
        return {}
    return json.loads(r.stdout)


def chan_url(c):
    c = c.strip()
    if c.startswith("http"):
        return c.rstrip("/") + ("" if c.rstrip("/").endswith("/shorts") else "/shorts")
    if c.startswith("UC"):
        return f"https://www.youtube.com/channel/{c}/shorts"
    return f"https://www.youtube.com/{c if c.startswith('@') else '@' + c}/shorts"


def mine():
    d = flat(MINE)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
    prev = {}
    if os.path.exists(HIST):
        for row in csv.DictReader(open(HIST, encoding="utf-8")):
            prev[row["id"]] = row  # последняя запись по ролику
    new = not os.path.exists(HIST)
    with open(HIST, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time_utc", "id", "views", "title"])
        for e in d.get("entries", []):
            v = e.get("view_count") or 0
            p = prev.get(e["id"])
            grow = ""
            if p:
                hrs = (dt.datetime.strptime(now, "%Y-%m-%d %H:%M") - dt.datetime.strptime(p["time_utc"], "%Y-%m-%d %H:%M")).total_seconds() / 3600
                if hrs > 0:
                    grow = f"  +{v - int(p['views'])} за {hrs:.0f} ч ({(v - int(p['views'])) / hrs:.0f}/ч)"
            print(f"{v:>8}  {e.get('title')}{grow}")
            w.writerow([now, e["id"], v, e.get("title")])


def outliers(chans, n=30, top=15):
    rows = []
    for c in chans:
        d = flat(chan_url(c), n)
        es = [e for e in d.get("entries", []) if e.get("view_count")]
        if len(es) < 5:
            continue
        med = statistics.median(e["view_count"] for e in es)
        for e in es:
            rows.append((e["view_count"] / max(med, 1), e["view_count"], d.get("channel") or d.get("title") or c, e.get("title"), e["id"]))
    rows.sort(reverse=True)
    for s, v, ch, t, i in rows[:top]:
        print(f"{s:5.1f}×  {v:>9}  {ch[:22]:22}  {t}  https://youtube.com/shorts/{i}")


def find(q, n=25):
    d = flat(f"ytsearch{n}:{q} #shorts", n)
    chans = []
    for e in d.get("entries", []):
        c = e.get("channel_id")
        if c and c not in chans:
            chans.append(c)
    print(f"каналов найдено: {len(chans)}")
    outliers(chans[:12])


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "mine":
        mine()
    elif a[0] == "outliers":
        outliers(a[1:])
    elif a[0] == "find":
        find(" ".join(a[1:]))
