# -*- coding: utf-8 -*-
"""核对首页/逛逛页渲染计数。"""
import os

tmp = os.environ.get("TEMP", ".")
home = open(os.path.join(tmp, "v_home.html"), encoding="utf-8", errors="ignore").read()
gg = open(os.path.join(tmp, "v_guang.html"), encoding="utf-8", errors="ignore").read()
print("home cards", home.count('class="card"'))
print("home 逛逛 mentions", home.count("逛逛"), "| tieba links", home.count("tieba.baidu.com/p/"))
print("guang cards", gg.count('class="card"'), "| groups", gg.count("gg-group"))
print("guang 浏览 in summary", "浏览" in gg)
print("bili mentions home", home.count("bilibili.com/video/"))
