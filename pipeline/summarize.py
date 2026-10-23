# -*- coding: utf-8 -*-
"""摘要：默认用规则压缩原文；配置了 LLM 就调用 OpenAI 兼容接口生成。"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from typing import Any

from .common import UA

SENT_SPLIT = re.compile(r"(?<=[。！？!?；;])\s*")


def sentences(text: str) -> list[str]:
    parts = [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]
    return parts


JUNK = ("您的位置", "当前位置", "关闭此页", "提示信息", "版权所有", "技术支持", "ICP备",
        "扫一扫", "上一篇", "下一篇", "点击查看", "相关附件", "浏览次数")
KEY_HINTS = ("时间", "地点", "报名", "截止", "举行", "举办", "召开", "开展", "名额", "要求")


def heuristic_summary(title: str, text: str, event: dict[str, Any] | None) -> str:
    """从正文里挑信息量最高的一两句，拼上时间地点。"""
    body = re.sub(r"\s+", " ", text or "").strip()
    picked: list[str] = []
    if body:
        cands = [s.strip() for s in sentences(body) if len(s.strip()) >= 10 and not any(j in s for j in JUNK)]
        for s in cands:
            if any(k in s for k in KEY_HINTS):
                picked.append(s)
            if len("".join(picked)) >= 60:
                break
        if not picked:
            picked = cands[:2]
    summary = "".join(picked)[:120].strip()
    # 清掉中文之间的多余空格
    summary = re.sub(r"(?<=[\u4e00-\u9fa5，。；：！？、（）《》])\s+|\s+(?=[\u4e00-\u9fa5，。；：！？、（）《》])", "", summary)
    if event:
        bits = []
        if event.get("start"):
            d = event["start"][5:10].split("-")
            bits.append(f"{int(d[0])}月{int(d[1])}日")
        if event.get("location"):
            bits.append(event["location"])
        prefix = "，".join(bits)
        if prefix and prefix not in summary and not re.match(r"^\d{1,2}月\d{1,2}日", summary):
            summary = f"{prefix}。{summary}" if summary else prefix
    return summary[:150]


PROMPT = """你是校园信息编辑。根据下面这篇通知/活动，写一句 60 字以内的中文摘要。
要求：保留时间、地点、截止日期、谁需要参加这类关键信息；不要评价，不要编造原文没有的内容。

标题：{title}
正文：{text}

只输出摘要本身。"""


def llm_summary(title: str, text: str, cfg: dict[str, Any]) -> str | None:
    llm = cfg.get("llm") or {}
    base = llm.get("base_url")
    model = llm.get("model")
    key = os.environ.get(llm.get("api_key_env", "OPENAI_API_KEY"), "")
    if not (base and model and key):
        return None
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT.format(title=title, text=text[:1800])}],
        "temperature": 0.2,
        "max_tokens": 200,
    }
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}", "User-Agent": UA},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"].strip()
        return content[:150] or None
    except Exception:
        return None


def make_summary(title: str, text: str, event: dict[str, Any] | None, cfg: dict[str, Any]) -> str:
    return llm_summary(title, text, cfg) or heuristic_summary(title, text, event)
