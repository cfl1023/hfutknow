# -*- coding: utf-8 -*-
"""修正 UTC 时间被当本地时间解析（generatedAt/crawl.at 无时区后缀）。"""
import pathlib
import re

p = pathlib.Path("site/app.js")
s = p.read_text(encoding="utf-8")

helper = """  // UTC 字符串（无时区）按 UTC 解析，避免显示成「8 小时前」
  function asDate(iso) {
    if (!iso) return null;
    const hasZone = /[zZ]$|[+-]\\d{2}:?\\d{2}$/.test(iso);
    return new Date(hasZone ? iso : iso + 'Z');
  }
  function fmtLocal(iso) {
    const d = asDate(iso);
    if (!d || isNaN(d)) return '';
    const p2 = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p2(d.getMonth() + 1)}-${p2(d.getDate())} ${p2(d.getHours())}:${p2(d.getMinutes())}`;
  }

"""
if "function asDate(" not in s:
    anchor = "  function relAgeText("
    assert anchor in s
    s = s.replace(anchor, helper + anchor, 1)
    print("helpers added")

# relAgeText 用 asDate
s2 = re.sub(
    r"(function relAgeText\(iso\) \{\n)(.*?)(\n  \})",
    lambda m: m.group(1) + "    const d = asDate(iso);\n    if (!d || isNaN(d)) return '';\n" + m.group(2).replace("new Date(iso)", "d") + m.group(3),
    s,
    count=1,
    flags=re.S,
)
if s2 != s:
    print("relAgeText patched")
s = s2

# newIn 用 asDate
s = s.replace("const cut = Date.now() - hours * 36e5;", "const cut = Date.now() - hours * 36e5;")
s = re.sub(r"new Date\(i\.publishedAt\)\.getTime\(\)", "asDate(i.publishedAt).getTime()", s)
s = re.sub(r"new Date\(S\.generatedAt\)\.getTime\(\)", "asDate(S.generatedAt).getTime()", s)

# 页脚时间改为本地格式
s = s.replace("${(S.generatedAt || '').replace('T', ' ').slice(0, 16)}", "${fmtLocal(S.generatedAt)}")
s = s.replace("(S.generatedAt || '').replace('T', ' ').slice(5, 16)", "fmtLocal(S.generatedAt).slice(5)")

p.write_text(s, encoding="utf-8")
print("done; asDate uses:", s.count("asDate("))
