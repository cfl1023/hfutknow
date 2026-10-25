# -*- coding: utf-8 -*-
import pathlib

p = pathlib.Path("site/index.html")
s = p.read_text(encoding="utf-8")
old = '    <p class="muted" id="footMeta"></p>'
new = old + '\n    <div id="footCrawl" class="muted"></div>'
if 'id="footCrawl"' in s:
    print("already present")
else:
    assert old in s, "anchor missing"
    p.write_text(s.replace(old, new, 1), encoding="utf-8")
    print("footCrawl added")
