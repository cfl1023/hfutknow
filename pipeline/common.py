# -*- coding: utf-8 -*-
"""公共工具：路径、HTTP、HTML 处理、JSON 读写。"""
from __future__ import annotations

import gzip
import io
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
DATA_DIR = SITE_DIR / "data"
CONFIG_PATH = ROOT / "config.json"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(cfg: dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def load_items() -> dict[str, Any]:
    path = DATA_DIR / "items.json"
    if not path.exists():
        return {"items": [], "categories": load_config()["categories"]}
    return json.loads(path.read_text(encoding="utf-8"))


def save_items(payload: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "items.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")


def save_sources(sources: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "sources.json").write_text(
        json.dumps({"sources": sources}, ensure_ascii=False, indent=1), encoding="utf-8")


def http_get(url: str, timeout: int = 20, retries: int = 2) -> tuple[str, str]:
    """返回 (解码后的文本, 最终 URL)。失败抛 RuntimeError。"""
    last: Exception | None = None
    for _ in range(retries + 1):
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip",
        })
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
                charset = resp.headers.get_content_charset()
                return decode(raw, charset), resp.geturl()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
    raise RuntimeError(f"GET {url} failed: {last}")


def decode(raw: bytes, charset: str | None = None) -> str:
    candidates = [charset, "utf-8", "gb18030", "gbk"]
    for enc in candidates:
        if not enc:
            continue
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", "ignore")


TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"[ \t\u3000]+")


def strip_tags(html: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    text = TAG_RE.sub("\n", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"&#\d+;", "", text)
    text = SPACE_RE.sub(" ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()
