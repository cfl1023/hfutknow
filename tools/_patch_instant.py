# -*- coding: utf-8 -*-
"""秒开：boot 先用 localStorage 缓存渲染，网络回来后无缝替换。"""
from pathlib import Path

p = Path("site/app.js")
s = p.read_text(encoding="utf-8")

# 1) 缓存读写工具
anchor = "  function registerSW() {"
helpers = '''  const LS_KEY = 'ck-cache-v1';
  function saveCache(payload, srcPayload) {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify({ g: S.generatedAt, items: payload.items, sources: srcPayload.sources }));
    } catch (e) { /* 超配额就放弃缓存，不影响使用 */ }
  }
  function loadCache() {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) return null;
      const d = JSON.parse(raw);
      return (d && d.items && d.items.length) ? d : null;
    } catch (e) { return null; }
  }

  function registerSW() {'''
assert anchor in s
s = s.replace(anchor, helpers, 1)

# 2) hydrate：boot 开头先渲染缓存
old_boot = """  async function boot() {
    applyTheme();
    try {"""
new_boot = """  function hydrate(d) {
    S.items = d.items || [];
    S.sources = d.sources || [];
    S.srcById = {};
    S.sources.forEach((x) => { S.srcById[x.id] = x; });
    S.generatedAt = d.g || '';
    S.demoCount = S.items.filter((i) => i.demo).length;
    bind();
    applyLang();
    route();
  }

  async function boot() {
    applyTheme();
    const cached = loadCache();
    if (cached) hydrate(cached);   // 秒开：先画缓存，再悄悄换网络数据
    try {"""
assert old_boot in s
s = s.replace(old_boot, new_boot, 1)

# 3) 网络数据到位后写缓存（boot 成功路径 + refreshData）
old_ok = """      bind();
      applyLang();
      route();
      registerSW();"""
new_ok = """      if (!cached) { bind(); applyLang(); route(); }
      saveCache(payload, srcPayload);
      registerSW();"""
assert old_ok in s
s = s.replace(old_ok, new_ok, 1)

old_ref = """      S.demoCount = S.items.filter((i) => i.demo).length;
      applyLang();
      return true;"""
new_ref = """      S.demoCount = S.items.filter((i) => i.demo).length;
      saveCache(payload, srcPayload);
      applyLang();
      return true;"""
if old_ref in s:
    s = s.replace(old_ref, new_ref, 1)

p.write_text(s, encoding="utf-8")
print("instant boot patched")
