# -*- coding: utf-8 -*-
"""来源类型标签支持 bili。"""
from pathlib import Path

p = Path("site/app.js")
t = p.read_text(encoding="utf-8")

t = t.replace(
    "<p>${s ? (s.type === 'wechat' ? L.wechat : L.official) : ''}</p></section>`;",
    "<p>${s ? srcTypeName(s.type) : ''}</p></section>`;")
t = t.replace(
    "${s ? `<span>${s.type === 'wechat' ? L.wechat : L.official}</span>` : ''}",
    "${s ? `<span>${srcTypeName(s.type)}</span>` : ''}")
t = t.replace(
    "${s.verified ? L.verified : L.toVerify} · ${s.type === 'wechat' ? L.wechat : L.official}",
    "${s.verified ? L.verified : L.toVerify} · ${srcTypeName(s.type)}")

old = "  function fmtPlay(n) {"
new = """  function srcTypeName(type) {
    const L = t();
    return type === 'wechat' ? L.wechat : type === 'bili' ? 'B站' : L.official;
  }

  function fmtPlay(n) {"""
assert old in t
t = t.replace(old, new, 1)

p.write_text(t, encoding="utf-8")
print("label patched")
