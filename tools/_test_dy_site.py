# -*- coding: utf-8 -*-
"""抖音无登录通道测试：走 Bing 的 site:douyin.com 索引。"""
import re
import sys
sys.path.insert(0, ".")
from pipeline import websearch

for q in ["site:douyin.com 合肥工业大学", "site:douyin.com 合工大", "抖音 合肥工业大学 活动"]:
    try:
        rows = websearch._search(q)
        print(q, "->", len(rows))
        for r in rows[:4]:
            print("   ", r["channel"] or "?", "|", r["title"][:44], "|", r["url"][:60])
    except Exception as e:
        print(q, "ERR", str(e)[:80])
