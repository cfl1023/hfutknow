# -*- coding: utf-8 -*-
from pathlib import Path

c = Path("site/style.css")
css = c.read_text(encoding="utf-8")
css += """
.badge-comp {
  display: inline-flex; align-items: center; font-size: 10px; font-weight: 700;
  padding: 2px 6px; border-radius: 4px; letter-spacing: .02em; line-height: 1.6;
  background: color-mix(in srgb, #3f7a5a 14%, transparent); color: #3f7a5a;
  max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.badge-comp.ic { background: var(--accent-soft); color: var(--accent-2); }
html[data-theme="dark"] .badge-comp { color: #8ec5a6; }
html[data-theme="dark"] .badge-comp.ic { color: var(--accent-2); }
"""
c.write_text(css, encoding="utf-8")
print("styles ok")
