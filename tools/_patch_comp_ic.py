# -*- coding: utf-8 -*-
"""修正 IC 相关判定：用关键词包含判断，避免全名不一致漏判。"""
from pathlib import Path

p = Path("pipeline/competitions.py")
t = p.read_text(encoding="utf-8")

old = '''# 高相关（集成电路方向）竞赛名，命中这些的排序权重更高
IC_COMPETITIONS = {"全国大学生集成电路创新创业大赛", "全国大学生嵌入式芯片与系统设计竞赛",
                   "全国大学生电子设计竞赛", "蓝桥杯全国大学生软件和信息技术大赛",
                   "安徽省集成电路精英赛", "全国大学生信息安全竞赛", "中国机器人及人工智能大赛"}'''
new = '''# 高相关（集成电路/电子方向）关键词，命中即视为强相关
IC_KEYS = ("集成电路", "嵌入式", "电子设计", "芯片", "半导体", "蓝桥杯",
           "信息安全", "机器人", "人工智能", "智能汽车", "程序设计", "EDA")'''
assert old in t
t = t.replace(old, new)

old2 = '''    name = hits[0][1]
    return {"name": name, "ic": name in IC_COMPETITIONS}'''
new2 = '''    name = hits[0][1]
    ic = any(k in name for k in IC_KEYS)
    return {"name": name, "ic": ic}'''
assert old2 in t
t = t.replace(old2, new2)
p.write_text(t, encoding="utf-8")
print("ic keys fixed")
