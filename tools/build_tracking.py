# -*- coding: utf-8 -*-
"""竞赛追踪：把 87 项竞赛与校内通知对上，抓通知正文里的报名截止/比赛时间，算状态。

产出写回 site/data/competitions.json 每项的 tracking 字段：
    status: open（报名中）| closed（已截止）| notice（有通知没写截止）| none（校内暂无通知）
    deadline/daysLeft/eventAt/snippet/how{} / notices[]
抓过的页面缓存在 site/data/_notice_cache.json，避免每轮重抓。
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

COMP = ROOT / "site" / "data" / "competitions.json"
ITEMS = ROOT / "site" / "data" / "items.json"
CACHE = ROOT / "site" / "data" / "_notice_cache.json"

YEAR = datetime.now().year

D_DEADLINE_A = re.compile(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日[^\n。；]{0,14}?(?:前|之前|截止|为止)")
D_DEADLINE_B = re.compile(r"报名(?:截止|时间|日期)[^\d\n]{0,16}?(\d{4})?\s*[年\-./]\s*(\d{1,2})\s*[月\-./]\s*(\d{1,2})")
D_DEADLINE_B2 = re.compile(r"报名(?:截止|时间|日期)[^\d\n]{0,16}?(\d{1,2})\s*月\s*(\d{1,2})\s*日")
D_DEADLINE_C = re.compile(r"截止(?:时间|日期|报名)?[^\d\n]{0,12}?(\d{4})?\s*[年\-./]\s*(\d{1,2})\s*[月\-./]\s*(\d{1,2})")
D_DEADLINE_C2 = re.compile(r"截止(?:时间|日期)?[^\d\n]{0,12}?(\d{1,2})\s*月\s*(\d{1,2})\s*日")
D_EVENT = re.compile(r"(?:校赛|初赛|比赛|决赛|评审|网考)(?:时间|定于|将于|拟于|安排在|时间定于|：|:)[^\d\n]{0,10}?"
                     r"(\d{4})?\s*[年\-./]?\s*(\d{1,2})\s*[月\-./]\s*(\d{1,2})")
D_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
D_PHONE = re.compile(r"(?:电话|联系|咨询)[^\d\n]{0,8}(1[3-9]\d{9}|0\d{2,3}-?\d{7,8})")
D_QQ = re.compile(r"(?:QQ|群号|QQ群)[^\d\n]{0,8}(\d{6,12})")
D_PLATFORM = re.compile(r"(https?://[^\s，。；）)\"']+)")


def _mk(month: int, day: int, year: int | None = None) -> str:
    try:
        y = year or YEAR
        if y < 2000:
            y = YEAR
        return date(y, month, day).isoformat()
    except ValueError:
        return ""


def _scan(text: str) -> dict:
    text = re.sub(r"\s+", " ", text or "")
    cands: list[tuple[str, str]] = []
    for m in D_DEADLINE_A.finditer(text):
        ds = _mk(int(m.group(1)), int(m.group(2)))
        if ds:
            cands.append((ds, m.group(0)[:90]))
    for pat in (D_DEADLINE_B, D_DEADLINE_C):
        for m in pat.finditer(text):
            g = m.groups()
            ds = _mk(int(g[1]), int(g[2]), int(g[0]) if g[0] else None)
            if ds:
                cands.append((ds, m.group(0)[:90]))
    for pat in (D_DEADLINE_B2, D_DEADLINE_C2):
        for m in pat.finditer(text):
            ds = _mk(int(m.group(1)), int(m.group(2)))
            if ds:
                cands.append((ds, m.group(0)[:90]))

    today = date.today()
    deadline = snippet = ""
    future = sorted([c for c in cands if c[0] >= today.isoformat()], key=lambda c: c[0])
    if future:
        deadline, snippet = future[0]
    elif cands:
        deadline, snippet = sorted(cands, key=lambda c: c[0])[-1]

    event = ""
    m = D_EVENT.search(text)
    if m:
        g = m.groups()
        event = _mk(int(g[1]), int(g[2]), int(g[0]) if g[0] else None)

    how: dict = {}
    if (mm := D_EMAIL.search(text)):
        how["email"] = mm.group(0)
    if (mm := D_PHONE.search(text)):
        how["phone"] = mm.group(1)
    if (mm := D_QQ.search(text)):
        how["qq"] = mm.group(1)
    if (mm := D_PLATFORM.search(text)):
        how["url"] = mm.group(1).rstrip("）)")
    return {"deadline": deadline, "snippet": snippet, "eventAt": event, "how": how}


def _level(name: str) -> str:
    if name.startswith(("中国", "全国", "国际", "美国")) or "全国" in name[:6] or "国际" in name[:6]:
        return "国家级"
    if "省" in name[:8]:
        return "省级"
    return "校级"


def _load_cache() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _page_text(url: str, cache: dict) -> str:
    if url in cache:
        return cache[url]
    text = ""
    try:
        from pipeline.common import http_get
        from lxml import html as lh

        raw, _ = http_get(url, timeout=20, retries=1)
        doc = lh.fromstring(raw)
        body = doc.xpath("//body")
        if body:
            text = " ".join(body[0].text_content().split())
    except Exception as exc:
        print(f"    抓取失败 {url[:60]}：{exc}")
    cache[url] = text
    return text


def build_tracking(items: list[dict], comps: list[dict], fetch: bool = True) -> None:
    today = date.today()
    cache = _load_cache()
    by_name: dict[str, list[dict]] = {}
    for it in items:
        c = it.get("competition")
        if not c:
            continue
        by_name.setdefault(c["name"], []).append(it)

    for comp in comps:
        comp["level"] = _level(comp["name"])
        related = sorted(by_name.get(comp["name"], []),
                         key=lambda i: i.get("publishedAt") or "", reverse=True)
        tracking = {"status": "none", "deadline": "", "daysLeft": None,
                    "eventAt": "", "snippet": "", "how": {}, "notices": []}
        for it in related[:3]:
            tracking["notices"].append({
                "id": it["id"], "title": it["title"], "url": it.get("url", ""),
                "date": (it.get("publishedAt") or "")[:10],
            })
            if not fetch:
                continue
            body = (it.get("content") or it.get("summary") or "")
            if isinstance(body, list):
                body = " ".join(str(b) for b in body)
            page = _page_text(it.get("url", ""), cache) if it.get("url") else ""
            got = _scan(page or body)
            if got["deadline"] and (not tracking["deadline"] or got["deadline"] < tracking["deadline"]):
                tracking["deadline"] = got["deadline"]
                tracking["snippet"] = got["snippet"]
            if got["eventAt"] and not tracking["eventAt"]:
                tracking["eventAt"] = got["eventAt"]
            for k, v in got["how"].items():
                tracking["how"].setdefault(k, v)

        if tracking["deadline"]:
            d = date.fromisoformat(tracking["deadline"])
            tracking["daysLeft"] = (d - today).days
            tracking["status"] = "open" if d >= today else "closed"
        elif tracking["notices"]:
            tracking["status"] = "notice"

        comp["tracking"] = tracking

    comps.sort(key=lambda c: (
        0 if c["tracking"]["status"] == "open" else 1,
        c["tracking"]["deadline"] or "9999",
        {"三大赛": 0, "A类": 1, "B类": 2}.get(c["tier"], 3),
        c["name"]))
    if len(cache) > 400:
        for k in list(cache)[: len(cache) - 400]:
            cache.pop(k, None)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    comp_data = json.loads(COMP.read_text(encoding="utf-8"))
    items = json.loads(ITEMS.read_text(encoding="utf-8"))["items"]
    comps = comp_data["items"]
    fetch = "--no-fetch" not in sys.argv
    build_tracking(items, comps, fetch=fetch)
    comp_data["trackedAt"] = datetime.now().isoformat(timespec="minutes")
    COMP.write_text(json.dumps(comp_data, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print("状态：", Counter(c["tracking"]["status"] for c in comps))
    for c in comps:
        t = c["tracking"]
        if t["status"] in ("open", "closed", "notice"):
            print(f"  {t['status']:6} {t['deadline'] or '-':10} {str(t['daysLeft']):>4}d {c['name'][:30]} ← {t['snippet'][:46]}")


if __name__ == "__main__":
    main()
