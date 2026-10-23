# -*- coding: utf-8 -*-
"""清理 items.json 里的垃圾条目，重算 sources.json。"""
import json
from pathlib import Path

DATA = Path("site/data")
items = json.loads((DATA / "items.json").read_text(encoding="utf-8"))["items"]

JUNK_TITLES = {"相关链接", "学院新闻", "公告新闻", "通知公告", "新闻动态", "工作动态",
               "学院动态", "更多新闻", "全部新闻", "通知中心", "栏目名称"}
BAD_PATTERNS = ["副教授（", "教授（", "讲师（", "研究员（", "高级实验师", "师资队伍",
                "教师名录", "员工名录"]


def is_junk(it: dict) -> bool:
    title = it.get("title", "").strip()
    if not title:
        return True
    if title in JUNK_TITLES:
        return True
    if any(b in title for b in BAD_PATTERNS):
        return True
    # 正文等于标题且很短的，基本是空页面
    content = "".join(it.get("content", []))
    text_len = len(content.replace("<p>", "").replace("</p>", ""))
    if text_len < 30 and len(title) < 20:
        return True
    return False


before = len(items)
kept = [i for i in items if not is_junk(i)]
removed = before - len(kept)

payload = json.loads((DATA / "items.json").read_text(encoding="utf-8"))
payload["items"] = kept
(DATA / "items.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

counts: dict[str, int] = {}
for it in kept:
    counts[it["sourceId"]] = counts.get(it["sourceId"], 0) + 1
sources = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))["sources"]
for s in sources:
    s["count"] = counts.get(s["id"], 0)
(DATA / "sources.json").write_text(json.dumps({"sources": sources}, ensure_ascii=False, indent=1),
                                   encoding="utf-8")

print(f"removed {removed}, kept {len(kept)}")
for it in kept[:3]:
    print("  keep:", it["title"][:40])
