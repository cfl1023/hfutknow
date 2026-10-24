# -*- coding: utf-8 -*-
"""把 docx 竞赛列表转成站点使用的 competitions.json（结构化）。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = json.loads((ROOT / "site" / "data" / "competitions.json").read_text(encoding="utf-8"))

tier = None
items = []
for r in RAW["rows"]:
    cells = r["cells"]
    text = " ".join(cells).strip()
    if "三大赛" in text:
        tier = "三大赛"
        continue
    if text.startswith("A类"):
        tier = "A类"
        continue
    if text.startswith("B类"):
        tier = "B类"
        continue
    if tier is None:
        continue
    # 格式：序号 / 名称 或 纯名称
    parts = [c for c in cells if c]
    name = parts[-1] if len(parts) > 1 else parts[0]
    name = name.strip()
    if not name or name.startswith(("序号", "编号", "赛事名称")):
        continue
    items.append({"tier": tier, "name": name})

# 关键词：从名称里拆，用于匹配抓取到的消息
KEYWORDS_PRIORITY = ["集成电路", "芯片", "嵌入式", "电子设计", "蓝桥杯", "信息安全",
                     "计算机", "程序设计", "数学建模", "人工智能", "智能汽车", "机器人"]

for it in items:
    kws = [k for k in KEYWORDS_PRIORITY if k in it["name"]]
    it["related"] = bool(kws)
    it["keywords"] = kws

payload = {
    "generatedAt": "2026-10-24",
    "source": "合肥工业大学学科竞赛赛事列表（2026年版）.docx",
    "total": len(items),
    "items": items,
}
(ROOT / "site" / "data" / "competitions.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

print("total:", len(items))
for it in items:
    if it["related"]:
        print("  ★", it["tier"], it["name"], it["keywords"])
