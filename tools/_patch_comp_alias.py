# -*- coding: utf-8 -*-
"""给 competitions.py 加别名表：蓝桥杯、挑战杯、数模、电赛等常用简称。"""
from pathlib import Path

p = Path("pipeline/competitions.py")
t = p.read_text(encoding="utf-8")

old = '''def detect_competition(title: str, text: str = "") -> dict | None:
    """返回 {'name': 竞赛全名, 'ic': bool} 或 None。"""
    haystack = f"{title} {text[:200]}"
    hits: list[tuple[int, str]] = []
    for full, short in SHORT_FORMS:
        # 优先匹配简称；全名太长很少原样出现在标题里
        if short in haystack and len(short) >= 5:
            hits.append((len(short), full))
        elif full in haystack:
            hits.append((len(full), full))'''

new = '''# 常用简称（标题里更常见）→ 竞赛全名
ALIASES: dict[str, str] = {
    "挑战杯": "挑战杯全国大学生课外学术科技作品竞赛",
    "互联网+": "中国国际大学生创新大赛",
    "互联网＋": "中国国际大学生创新大赛",
    "蓝桥杯": "蓝桥杯全国大学生软件和信息技术专业人才大赛",
    "数模": "全国大学生数学建模竞赛",
    "数学建模": "全国大学生数学建模竞赛",
    "电赛": "全国大学生电子设计竞赛",
    "电子设计竞赛": "全国大学生电子设计竞赛",
    "大创": "全国大学生创新创业训练计划",
    "集成电路大赛": "全国大学生集成电路创新创业大赛",
    "集创赛": "全国大学生集成电路创新创业大赛",
    "嵌入式竞赛": "全国大学生嵌入式芯片与系统设计竞赛",
    "工训赛": "中国大学生工程实践与创新能力大赛",
    "智能车": "全国大学生智能汽车竞赛",
    "程序设计竞赛": "中国大学生程序设计竞赛",
    "数学竞赛": "全国大学生数学竞赛",
}


def detect_competition(title: str, text: str = "") -> dict | None:
    """返回 {'name': 竞赛全名, 'ic': bool} 或 None。"""
    haystack = f"{title} {text[:200]}"
    hits: list[tuple[int, str]] = []
    # 先查别名（最长优先）
    for alias in sorted(ALIASES, key=len, reverse=True):
        if alias in haystack:
            hits.append((len(alias), ALIASES[alias]))
    for full, short in SHORT_FORMS:
        # 简称命中（>=4 字，避免「大赛」这种泛词误伤）
        if short in haystack and len(short) >= 4:
            hits.append((len(short), full))
        elif full in haystack:
            hits.append((len(full), full))'''

assert old in t
t = t.replace(old, new)
p.write_text(t, encoding="utf-8")
print("aliases added")
