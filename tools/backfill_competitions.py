# -*- coding: utf-8 -*-
"""测试竞赛识别 + 回填历史 items.json 的 competition 字段。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import competitions

# 1) 单测几条
samples = [
    "关于举办2026年全国大学生电子设计竞赛校内选拔赛的通知",
    "我院学子在蓝桥杯全国软件和信息技术专业人才大赛获奖",
    "合肥工业大学集成电路创新创业大赛报名开始",
    "关于举办第十七届大学生数学竞赛的通知",
    "关于举办2026年校园歌手大赛的通知",
    "挑战杯校赛结果公布",
    "第三届全国大学生职业规划大赛",
    "普通奖学金评选通知",
]
print("=== 识别测试 ===")
for s in samples:
    r = competitions.detect_competition(s)
    print(f"{'✓' if r else '✗'} {s[:34]:36} -> {r}")

# 2) 回填
p = Path(__file__).resolve().parents[1] / "site" / "data" / "items.json"
data = json.loads(p.read_text(encoding="utf-8"))
items = data.get("items", [])
hit = 0
for it in items:
    r = competitions.detect_competition(it.get("title", ""), it.get("summary", ""))
    if r:
        it["competition"] = r
        hit += 1
    elif "competition" in it:
        del it["competition"]
p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n回填完成：{len(items)} 条中 {hit} 条命中竞赛")
if hit:
    for it in items:
        if it.get("competition"):
            print("  -", it["competition"]["name"], "|", it["title"][:40])
