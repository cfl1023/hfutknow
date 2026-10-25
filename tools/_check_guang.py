# -*- coding: utf-8 -*-
"""数逛逛页的帖子链接与分组头。"""
import os
import re

q = open(os.path.join(os.environ["TEMP"], "v_guang.html"), encoding="utf-8", errors="ignore").read()
print("gg links", q.count("#/i/gg-"))
print("card variants", q.count('class="card'), q.count('class="card read"'))
print("groups", re.findall(r"<h2>(.*?)<span>(\d+) 条", q))
