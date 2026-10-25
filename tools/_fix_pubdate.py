# -*- coding: utf-8 -*-
"""修 tieba publishedAt：用最近回复日期，不用抓取时间。"""
from pathlib import Path

p = Path("tools/ingest_corpus.py")
s = p.read_text(encoding="utf-8")

old = '''        cat = classify(title)
        replies = r.get("replies")
        out.append({'''
new = '''        cat = classify(title)
        replies = r.get("replies")
        # 发布时间用「最近回复日期」，避免老帖全堆在今天
        pub_iso = datetime.now().isoformat(timespec="minutes")
        if m:
            pub_iso = m.group(0) + "T12:00"
        elif re.match(r"(\\d{1,2})-(\\d{1,2})$", str(lra)):
            mo, dd = map(int, str(lra).split("-"))
            try:
                dt_ = datetime(datetime.now().year, mo, dd, 12, 0)
                if dt_ > datetime.now():
                    dt_ = dt_.replace(year=dt_.year - 1)
                pub_iso = dt_.isoformat(timespec="minutes")
            except ValueError:
                pass
        out.append({'''
assert old in s
s = s.replace(old, new, 1)
s = s.replace('"publishedAt": (r.get("fetchedAt") or datetime.now().isoformat(timespec="minutes"))[:16],',
              '"publishedAt": pub_iso,')
p.write_text(s, encoding="utf-8")
print("patched")
