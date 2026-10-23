# -*- coding: utf-8 -*-
"""静态分析 APK：找包名、接口域名、登录相关字段。不做任何登录。"""
from __future__ import annotations

import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

APK = Path(sys.argv[1])
z = zipfile.ZipFile(APK)
names = z.namelist()
print(f"entries: {len(names)}")
for n in names[:12]:
    print("  ", n)

url_re = re.compile(rb"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]{4,140}")
urls: Counter[str] = Counter()
logins: set[str] = set()
for n in names:
    if not (n.endswith(".dex") or n.endswith(".xml") or n.endswith(".json") or n.endswith(".js")):
        continue
    try:
        data = z.read(n)
    except Exception:
        continue
    for m in url_re.finditer(data):
        u = m.group(0).decode("utf-8", "ignore").rstrip("\\x00")
        urls[u] += 1
    for kw in (b"login", b"Login", b"password", b"passwd", b"/api/", b"token"):
        if kw in data:
            logins.add(f"{n}:{kw.decode()}")

print("\n=== top hosts/urls ===")
for u, c in urls.most_common(40):
    print(f"{c:4} {u[:120]}")

hosts = Counter()
for u in urls:
    m = re.match(r"https?://([^/]+)", u)
    if m:
        hosts[m.group(1)] += urls[u]
print("\n=== hosts ===")
for h, c in hosts.most_common(25):
    print(f"{c:4} {h}")

print("\n=== login-ish files ===")
for x in sorted(logins)[:30]:
    print("  ", x)

# 包名 / 应用名
manifest = z.read("AndroidManifest.xml") if "AndroidManifest.xml" in names else b""
text = manifest.decode("utf-16-le", "ignore")
pkgs = re.findall(r"[a-z][a-z0-9_]*(?:\.[a-zA-Z0-9_]+){2,}", text)
print("\n=== likely package ===", pkgs[:6])
