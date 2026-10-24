# -*- coding: utf-8 -*-
"""把 B 站渠道接进 sync.py：抓官方源之后补一轮真人视频。"""
from pathlib import Path

p = Path("pipeline/sync.py")
t = p.read_text(encoding="utf-8")

old_imp = "from . import classify, common, competitions, fetchers, summarize"
new_imp = "from . import bili, classify, common, competitions, fetchers, summarize"
assert old_imp in t
t = t.replace(old_imp, new_imp)

old_loop_end = """    items.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)"""
new_loop_end = """    # B 站：真人学生视频（约每 3 小时刷一次，见 pipeline/bili.py）
    bili_items = bili.fetch_items(cfg.get("biliKeywords") or ["合肥工业大学", "合工大"])
    bili_new = 0
    for it in bili_items:
        if it["url"] in existing_urls:
            continue
        existing_urls.add(it["url"])
        items.append(it)
        bili_new += 1
    if bili_new:
        print(f"  + B站: 新增 {bili_new} 条")
    total_new += bili_new

    items.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)"""
assert old_loop_end in t
t = t.replace(old_loop_end, new_loop_end)

# sources_out 里补 B 站伪源，来源页才看得到
old_src = '''    sources_out = [{**s, "count": counts.get(s["id"], 0)} for s in cfg["sources"]]'''
new_src = '''    sources_out = [{**s, "count": counts.get(s["id"], 0)} for s in cfg["sources"]]
    seen = {s["id"] for s in sources_out}
    for b_id, n in counts.items():
        if b_id.startswith("bili-") and b_id not in seen:
            name = next((i["sourceName"] for i in items if i["sourceId"] == b_id), "B站")
            kw = name.replace("B站 · ", "")
            sources_out.append({"id": b_id, "name": name, "type": "bili",
                                "url": f"https://search.bilibili.com/all?keyword={kw}",
                                "category": "life", "count": n,
                                "feed": {"type": "bili", "url": "", "enabled": True}})'''
assert old_src in t
t = t.replace(old_src, new_src)

p.write_text(t, encoding="utf-8")
print("sync patched")
