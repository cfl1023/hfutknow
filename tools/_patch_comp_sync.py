# -*- coding: utf-8 -*-
"""sync.py 接入竞赛检测：命中竞赛的消息打 competition 标记，前端高亮。"""
from pathlib import Path

p = Path("pipeline/sync.py")
t = p.read_text(encoding="utf-8")

# import
old_imp = "from . import classify, common, fetchers, summarize"
new_imp = "from . import classify, common, competitions, fetchers, summarize"
assert old_imp in t
t = t.replace(old_imp, new_imp)

# build_item 里加竞赛标记（在 tags 行附近）
old_tags = '        "tags": classify.keywords(title),'
new_tags = '''        "tags": classify.keywords(title),
        "competition": competitions.detect_competition(title, text),'''
assert old_tags in t
t = t.replace(old_tags, new_tags)

p.write_text(t, encoding="utf-8")
print("patched sync")
