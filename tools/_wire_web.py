# -*- coding: utf-8 -*-
"""websearch 接入 sync + 排除官网重复域名。"""
from pathlib import Path

p = Path("pipeline/websearch.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    'CAMPUS_RE = re.compile(r"合肥工业|合工大|HFUT|斛兵|翡翠湖")',
    'CAMPUS_RE = re.compile(r"合肥工业|合工大|HFUT|斛兵|翡翠湖")\n'
    '# 官网已有专门抓取，搜索结果里再出现就是重复\n'
    'SKIP_HOSTS = ("hfut.edu.cn", "bing.com", "microsoft.com")')
s = s.replace(
    '        ch = _channel(href)\n        out.append(',
    '        if any(h in href for h in SKIP_HOSTS):\n            continue\n'
    '        ch = _channel(href)\n        out.append(')
p.write_text(s, encoding="utf-8")

p2 = Path("pipeline/sync.py")
s2 = p2.read_text(encoding="utf-8")
s2 = s2.replace("from . import bili, classify, common, competitions, fetchers, summarize",
                "from . import bili, classify, common, competitions, fetchers, summarize, websearch")
old = """    items.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)"""
new = """    # 互联网搜索（Bing，约 2 小时一次；海外 runner 上稳定，本机可能被墙）
    try:
        web_items = websearch.fetch_items()
    except Exception as exc:
        print(f"  × 互联网搜索整体失败: {str(exc)[:80]}")
        web_items = []
    web_new = 0
    for it in web_items:
        if it["url"] in existing_urls or it["id"] in {i["id"] for i in items}:
            continue
        existing_urls.add(it["url"])
        items.append(it)
        web_new += 1
    if web_new:
        print(f"  + 互联网: 新增 {web_new} 条")
    total_new += web_new

    items.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)"""
assert old in s2
s2 = s2.replace(old, new, 1)
p2.write_text(s2, encoding="utf-8")
print("wired")
