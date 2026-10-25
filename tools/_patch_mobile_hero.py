# -*- coding: utf-8 -*-
"""手机端隐藏 hero（大标题/简介/统计/快捷链接），打开直接是消息流；sw 升 v5。"""
from pathlib import Path

c = Path("site/style.css")
css = c.read_text(encoding="utf-8")
if "/* 手机端隐藏 hero */" not in css:
    css += """
/* 手机端隐藏 hero */
@media (max-width: 780px) {
  .hero { padding: 8px 0 0; }
  .hero h1, .hero > p, .profile-line, .quick-links, .stats { display: none !important; }
  .hero:has(> .comp-strip) { padding-top: 12px; }
  .comp-strip { margin: 0 0 6px; }
  .toolbar { margin-top: 4px; }
}
"""
    c.write_text(css, encoding="utf-8")
    print("css ok")

s = Path("site/sw.js")
t = s.read_text(encoding="utf-8")
t = t.replace("hfutknow-v4", "hfutknow-v5")
s.write_text(t, encoding="utf-8")
print("sw v5")
