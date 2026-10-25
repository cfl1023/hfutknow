# -*- coding: utf-8 -*-
"""把逛逛活动条目升级：主讲人/地点/报名截止/海报图。"""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "pipeline" / "guang.py"
s = p.read_text(encoding="utf-8")

old_start = '    for a in acts.get("records") or []:'
old_end = '    items.extend(_items_from_topics(tk, op))'
i, j = s.find(old_start), s.find(old_end)
assert i > 0 and j > i, "anchors not found"

new = '''    for a in acts.get("records") or []:
        item = _activity_item(a)
        if item:
            items.append(item)
'''
s = s[:i] + new + s[j:]

helper = '''
def _activity_item(a: dict) -> dict[str, Any] | None:
    name = (a.get("name") or "").strip()
    if not name:
        return None
    cat = MODULE_CAT.get(a.get("moduleName") or "", "campus")
    lec = (a.get("lectureStartTime") or "").replace(" ", "T")[:16]
    begin = lec or (a.get("beginTime") or "").replace(" ", "T")[:16]
    end = (a.get("lectureEndTime") or a.get("endTime") or "").replace(" ", "T")[:16]
    close = (a.get("et") or a.get("mobileEndTime") or "").strip()
    venue = (a.get("theVenue") or "").strip()
    evt = {"start": begin or None, "end": end or None, "location": venue or None}
    bits = [a.get("moduleName") or "", "主办 " + (a.get("sponsor") or "?")]
    if a.get("form"):
        bits.append(str(a["form"]))
    if a.get("keynoteSpeaker"):
        bits.append("主讲 " + str(a["keynoteSpeaker"]))
    if a.get("peopleNum"):
        bits.append(f"限 {a['peopleNum']} 人")
    bits.append(f"已报 {a.get('applyNum') or 0}")
    if close:
        bits.append(f"报名截止 {close}")
    if venue:
        bits.append(venue)
    summary = "｜".join([b for b in bits if b])
    paras = [f"<p>{summary}</p>"]
    photo = (a.get("activePhoto") or "").strip()
    if photo.startswith("http"):
        paras.append(f'<p><img src="{photo}" alt="{name}" loading="lazy"></p>')
    return {
        "id": "gg-" + str(a.get("id")),
        "title": name[:100],
        "sourceId": "gg-activity",
        "sourceName": "逛逛 · 校园活动",
        "sourceType": "gg",
        "url": "https://community.hfut.edu.cn/",
        "publishedAt": begin or datetime.now().isoformat(timespec="minutes"),
        "dateEstimated": not bool(begin),
        "intent": "activity",
        "category": cat,
        "summary": summary,
        "event": evt if begin else None,
        "deadline": close or None,
        "speaker": (a.get("keynoteSpeaker") or "").strip() or None,
        "requiresSignup": True,
        "tags": [t for t in [a.get("moduleName"), a.get("campus_dictText"), a.get("form")] if t],
        "competition": None,
        "feed": True,
        "content": paras,
        "poster": photo or None,
        "demo": False,
    }


'''
anchor = "def fetch_items() -> list[dict[str, Any]]:"
s = s.replace(anchor, helper.lstrip("\n") + anchor, 1)
p.write_text(s, encoding="utf-8")
print("patched guang activity builder")
