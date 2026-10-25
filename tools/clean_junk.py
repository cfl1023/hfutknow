# -*- coding: utf-8 -*-
"""清理 items.json 里的垃圾条目，重算 sources.json。

也负责把「发布日期晚于今天」的坏数据清掉（云端已从源头拒绝，
这里兜底清理历史遗留）。
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "site" / "data"

JUNK_TITLES = {"相关链接", "学院新闻", "公告新闻", "通知公告", "新闻动态", "工作动态",
               "学院动态", "更多新闻", "全部新闻", "通知中心", "栏目名称"}
BAD_PATTERNS = ["副教授（", "教授（", "讲师（", "研究员（", "高级实验师", "师资队伍",
                "教师名录", "员工名录"]


def is_junk(it: dict, max_day) -> bool:
    title = it.get("title", "").strip()
    if not title:
        return True
    if title in JUNK_TITLES:
        return True
    if any(b in title for b in BAD_PATTERNS):
        return True
    # 发布日期晚于明天 = 日期解析错误的坏数据，直接清掉
    published = it.get("publishedAt", "")
    try:
        if published:
            pub_day = datetime.fromisoformat(published).date()
            if pub_day > max_day:
                return True
    except ValueError:
        pass
    # 正文等于标题且很短的，基本是空页面
    content = "".join(it.get("content", []))
    text_len = len(content.replace("<p>", "").replace("</p>", ""))
    if text_len < 30 and len(title) < 20:
        return True
    return False


def main() -> None:
    items = json.loads((DATA / "items.json").read_text(encoding="utf-8"))["items"]
    max_day = datetime.now().date() + timedelta(days=1)

    before = len(items)
    kept = [i for i in items if not is_junk(i, max_day)]
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
        removed_urls = [i.get("url", "") for i in items if i not in kept and i.get("url")]
    bl = DATA / "junk_urls.txt"
    old = set(bl.read_text(encoding="utf-8").split()) if bl.exists() else set()
    bl.write_text("\n".join(sorted(old | set(removed_urls))), encoding="utf-8")

    (DATA / "sources.json").write_text(json.dumps({"sources": sources}, ensure_ascii=False, indent=1),
                                       encoding="utf-8")

    print(f"cleaned {removed}, kept {len(kept)}")


if __name__ == "__main__":
    main()
