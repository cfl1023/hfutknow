# -*- coding: utf-8 -*-
"""tieba recent 判定：null 不收，相对时间（N小时前/分钟前）要收。"""
from pathlib import Path

p = Path("tools/ingest_corpus.py")
s = p.read_text(encoding="utf-8")

old = '''        # lastReplyAt 有两种格式："09-19" 或 "2026-10-25" 或 null；判不动就按 30 天内收
        lra = r.get("lastReplyAt") or ""
        recent = True
        m = re.match(r"(\\d{4})-(\\d{2})-(\\d{2})", str(lra))
        if m:
            try:
                recent = datetime.strptime(m.group(0), "%Y-%m-%d") >= cutoff
            except ValueError:
                recent = True
        elif re.match(r"(\\d{1,2})-(\\d{1,2})$", str(lra)):
            mo, dd = map(int, str(lra).split("-"))
            try:
                recent = datetime(datetime.now().year, mo, dd) >= cutoff
            except ValueError:
                recent = True
        if not recent:
            continue'''
new = '''        # lastReplyAt 形态：null（老帖，不收）/ "09-19" / "2026-10-25" / "11小时前" / "38分钟前"
        lra = str(r.get("lastReplyAt") or "").strip()
        if not lra:
            continue
        m = re.match(r"(\\d{4})-(\\d{2})-(\\d{2})", lra)
        recent = False
        if m:
            try:
                recent = datetime.strptime(m.group(0), "%Y-%m-%d") >= cutoff
            except ValueError:
                recent = False
        elif re.search(r"(分钟|小时)前$", lra):
            recent = True
        elif re.match(r"(\\d{1,2})-(\\d{1,2})$", lra):
            mo, dd = map(int, lra.split("-"))
            try:
                recent = datetime(datetime.now().year, mo, dd) >= cutoff
            except ValueError:
                recent = False
        if not recent:
            continue'''
assert old in s, "recent block not found"
s = s.replace(old, new, 1)

# pub_iso 也要处理「N小时前/分钟前」
old2 = '''        pub_iso = datetime.now().isoformat(timespec="minutes")
        if m:
            pub_iso = m.group(0) + "T12:00"
        elif re.match(r"(\\d{1,2})-(\\d{1,2})$", str(lra)):'''
new2 = '''        pub_iso = datetime.now().isoformat(timespec="minutes")
        if m:
            pub_iso = m.group(0) + "T12:00"
        elif re.search(r"(分钟|小时)前$", lra):
            pass  # 保持 now
        elif re.match(r"(\\d{1,2})-(\\d{1,2})$", lra):'''
assert old2 in s
s = s.replace(old2, new2, 1)
p.write_text(s, encoding="utf-8")
print("patched")
