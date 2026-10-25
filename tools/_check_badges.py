# -*- coding: utf-8 -*-
"""数卡片上的子标签。"""
import os
import re

s = open(os.path.join(os.environ["TEMP"], "v_g4.html"), encoding="utf-8", errors="ignore").read()
print("badge-tag count", s.count("badge-tag"))
print(re.findall(r'badge-tag">([^<]{1,30})<', s)[:8])
