# -*- coding: utf-8 -*-
"""打印 dump 里 #app 的内层内容。"""
import sys, re
s = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
i = s.find('id="app"')
print(i)
print(s[i:i + 2600])
