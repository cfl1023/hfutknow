# -*- coding: utf-8 -*-
import pathlib

s = pathlib.Path("dist/工大知道.html").read_text(encoding="utf-8")
i = s.find("fresh-line")
print("excerpt:", repr(s[i - 90:i + 140]))
print("has fn:", "function freshLineHTML" in s)
print("data-fresh at:", s.find("data-fresh"))
print("literal count:", s.count("${freshLineHTML()}"))
