# -*- coding: utf-8 -*-
"""统一时间解析：无时区的 ISO（含 T）按 UTC 处理；dt() 复用 asDate()。"""
import pathlib
import re

p = pathlib.Path("site/app.js")
s = p.read_text(encoding="utf-8")

old_as = """  function asDate(iso) {
    if (!iso) return null;
    const hasZone = /[zZ]$|[+-]\\d{2}:?\\d{2}$/.test(iso);
    return new Date(hasZone ? iso : iso + 'Z');
  }"""
new_as = """  function asDate(iso) {
    if (!iso) return null;
    const hasZone = /[zZ]$|[+-]\\d{2}:?\\d{2}$/.test(iso);
    const needsZ = !hasZone && iso.includes('T');
    return new Date(needsZ ? iso + 'Z' : iso);
  }"""
if old_as in s:
    s = s.replace(old_as, new_as, 1)

old_dt = "  function dt(iso) { return iso ? new Date(iso) : null; }"
new_dt = "  function dt(iso) { return asDate(iso); }"
if old_dt in s:
    s = s.replace(old_dt, new_dt, 1)

# 去掉重复的 asDate 定义（若存在两份，保留一份）
if s.count("function asDate(") > 1:
    first = s.find("function asDate(")
    second = s.find("function asDate(", first + 10)
    end = s.find("\n  }\n", second)
    s = s[:second] + s[end + 4:]
    print("duplicate asDate removed")

p.write_text(s, encoding="utf-8")
print("asDate count:", s.count("function asDate("))
