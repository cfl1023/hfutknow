# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------- app.js: 学院列表 + 首页日历入口 ----------
p = ROOT / "site" / "app.js"
s = p.read_text(encoding="utf-8")

old = """      S.people = (S.peopleData && S.peopleData.people) || [];"""
new = """      S.people = (S.peopleData && S.peopleData.people) || [];
      S.peopleColleges = (S.peopleData && S.peopleData.colleges) || [];"""
assert old in s
s = s.replace(old, new)

old = """        ${profileLine}
        <div class="stats">"""
new = """        ${profileLine}
        <p class="quick-links"><a href="#/calendar">📅 ${L.calendar}</a><a href="#/competitions">🏆 学科竞赛</a><a href="#/people">👤 ${L.nav.people}</a></p>
        <div class="stats">"""
assert old in s
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("app.js boot/hero patched")

# ---------- config.json: profile 学院名 ----------
p = ROOT / "config.json"
cfg = json.loads(p.read_text(encoding="utf-8"))
cfg.setdefault("profile", {})["college"] = "微电子学院"
p.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
print("config profile.college = 微电子学院")
