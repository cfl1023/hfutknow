# -*- coding: utf-8 -*-
"""修 relAgeText 里 d 重复声明：重命名时间变量并去掉多余 if。"""
import pathlib

p = pathlib.Path("site/app.js")
s = p.read_text(encoding="utf-8")

bad = """    const d = asDate(iso);
    if (!d || isNaN(d)) return '';
    if (!iso) return '';"""
good = """    const dt = asDate(iso);
    if (!dt || isNaN(dt)) return '';"""
if bad in s:
    s = s.replace(bad, good, 1)
s = s.replace("const m = Math.max(0, Math.round((Date.now() - d.getTime()) / 60000));",
              "const m = Math.max(0, Math.round((Date.now() - dt.getTime()) / 60000));")
p.write_text(s, encoding="utf-8")

seg = s[s.find("function relAgeText"):s.find("function relAgeText") + 420]
print(seg)
print("d.getTime left:", s.count("d.getTime()"))
