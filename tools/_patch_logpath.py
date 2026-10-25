# -*- coding: utf-8 -*-
import pathlib

root = pathlib.Path(".")
p = root / "tools" / "local_update.ps1"
s = p.read_text(encoding="utf-8")
old = "$logDir = Join-Path $repo 'logs'"
new = "$logDir = Join-Path $env:LOCALAPPDATA 'HFUTKnow'"
if old in s:
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
    print("log dir moved")
else:
    print("log dir already moved")

gi = root / ".gitignore"
t = gi.read_text(encoding="utf-8") if gi.exists() else ""
for line in ("logs/", ".local_update.lock", "dist/"):
    if line not in t:
        t = t.rstrip() + "\n" + line + "\n"
gi.write_text(t, encoding="utf-8")
print(t)
