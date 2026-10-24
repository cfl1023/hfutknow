# -*- coding: utf-8 -*-
"""前端：B 站条目的作者/播放量展示。"""
from pathlib import Path

p = Path("site/app.js")
t = p.read_text(encoding="utf-8")

old = """        <span class="srcname">${esc(item.sourceName)}</span>
        <span class="dot"></span>
        <span>${catName(item.category)}</span>
        <span class="time">${relTime(item.publishedAt)}</span>"""
new = """        <span class="srcname">${esc(item.sourceName)}</span>
        <span class="dot"></span>
        <span>${catName(item.category)}</span>
        ${item.bili ? `<span class="dot"></span><span>${esc(item.bili.author)} · ▶${fmtPlay(item.bili.play)}</span>` : ''}
        <span class="time">${relTime(item.publishedAt)}</span>"""
assert old in t
t = t.replace(old, new)

# 工具函数
old2 = "  function cardHTML(item) {"
new2 = """  function fmtPlay(n) {
    n = Number(n) || 0;
    if (n >= 10000) return (n / 10000).toFixed(1).replace('.0', '') + '万';
    return String(n);
  }

  function cardHTML(item) {"""
assert old2 in t
t = t.replace(old2, new2, 1)

# 详情页来源行也带上作者
old3 = """          <span class="drawer-hint">${esc(item.sourceName)}</span>"""
new3 = """          <span class="drawer-hint">${esc(item.sourceName)}${item.bili ? ' · ' + esc(item.bili.author) + ' · ▶' + fmtPlay(item.bili.play) : ''}</span>"""
assert old3 in t
t = t.replace(old3, new3)

p.write_text(t, encoding="utf-8")
print("bili ui patched")
