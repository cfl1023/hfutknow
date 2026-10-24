# -*- coding: utf-8 -*-
"""给 classify 加竞赛检测：命中《2026 竞赛列表》名称的消息打上竞赛标记。"""
import json
import re
from pathlib import Path

# 读竞赛列表（87 项）
comp_path = Path(__file__).resolve().parents[1] / "site" / "data" / "competitions.json"
COMPETITIONS: list[str] = []
try:
    data = json.loads(comp_path.read_text(encoding="utf-8"))
    COMPETITIONS = [c["name"] for c in data.get("items", [])]
except Exception:
    pass

# 竞赛名拆成可匹配的短词（去掉前缀「全国大学生」等，提高命中率）
def _short_forms() -> list[tuple[str, str]]:
    out = []
    for name in COMPETITIONS:
        short = name
        for prefix in ("全国大学生", "中国大学生", "安徽省大学生", "安徽省", "全国高校",
                       "中国高校", "国际大学生", "美国大学生", "大学生"):
            if short.startswith(prefix):
                short = short[len(prefix):]
        # 去掉引号和空格
        short = re.sub(r"[“”\"\s]", "", short)
        if len(short) >= 4:
            out.append((name, short))
    return out

SHORT_FORMS = _short_forms()

# 高相关（集成电路/电子方向）关键词，命中即视为强相关
IC_KEYS = ("集成电路", "嵌入式", "电子设计", "芯片", "半导体", "蓝桥杯",
           "信息安全", "机器人", "人工智能", "智能汽车", "程序设计", "EDA")


# 常用简称（标题里更常见）→ 竞赛全名
ALIASES: dict[str, str] = {
    "挑战杯": "挑战杯全国大学生课外学术科技作品竞赛",
    "互联网+": "中国国际大学生创新大赛",
    "互联网＋": "中国国际大学生创新大赛",
    "蓝桥杯": "蓝桥杯全国大学生软件和信息技术专业人才大赛",
    "数模": "全国大学生数学建模竞赛",
    "数学建模": "全国大学生数学建模竞赛",
    "电赛": "全国大学生电子设计竞赛",
    "电子设计竞赛": "全国大学生电子设计竞赛",
    "大创": "全国大学生创新创业训练计划",
    "集成电路大赛": "全国大学生集成电路创新创业大赛",
    "集创赛": "全国大学生集成电路创新创业大赛",
    "嵌入式竞赛": "全国大学生嵌入式芯片与系统设计竞赛",
    "工训赛": "中国大学生工程实践与创新能力大赛",
    "智能车": "全国大学生智能汽车竞赛",
    "程序设计竞赛": "中国大学生程序设计竞赛",
    "数学竞赛": "全国大学生数学竞赛",
}


def detect_competition(title: str, text: str = "") -> dict | None:
    """返回 {'name': 竞赛全名, 'ic': bool} 或 None。"""
    haystack = f"{title} {text[:200]}"
    hits: list[tuple[int, str]] = []
    # 先查别名（最长优先）
    for alias in sorted(ALIASES, key=len, reverse=True):
        if alias in haystack:
            hits.append((len(alias), ALIASES[alias]))
    for full, short in SHORT_FORMS:
        # 简称命中（>=4 字，避免「大赛」这种泛词误伤）
        if short in haystack and len(short) >= 4:
            hits.append((len(short), full))
        elif full in haystack:
            hits.append((len(full), full))
    if not hits:
        return _generic_competition(title)
    hits.sort(reverse=True)
    name = hits[0][1]
    ic = any(k in name for k in IC_KEYS)
    return {"name": name, "ic": ic}

# 列表之外的竞赛消息：从标题里抓「第X届…大赛 / …竞赛」这类名字（best effort）
GENERIC_RE = re.compile(r"([\u4e00-\u9fa5A-Za-z0-9（）()·\-—\s]{2,26}?(?:大赛|竞赛|选拔赛))")
SKIP_GENERIC = ("成果", "获奖名单", "评审结果", "评审公示", "获奖情况", "党支部", "教研室", "知识竞赛")
CLEAN_LEAD = re.compile(
    r"^(?:关于|举办|开展|参加|推荐|组织|我校|我院|学子|学院|实验室|代表队|"
    r"[\u4e00-\u9fa5]{2,8}(?:学院|大学|系|支部)(?:学子|代表队|实验室)?(?:在|于)?)")


def _generic_competition(title: str) -> dict | None:
    if any(k in title for k in SKIP_GENERIC):
        return None
    m = GENERIC_RE.search(title)
    if not m:
        return None
    name = m.group(1).strip(" 《》“”")
    # 「…文化节暨…大赛」只留暨字后面那段
    if "暨" in name:
        name = name.split("暨")[-1]
    # 去掉「学子在/学院实验室在」这类前缀
    for _ in range(3):
        new = CLEAN_LEAD.sub("", name).strip()
        if new == name:
            break
        name = new
    # 仍在名字中间的「在/于」当作分界
    if "在" in name and len(name.split("在")[-1]) >= 5:
        name = name.split("在")[-1]
    name = name.strip(" 的")
    if len(name) < 5:
        return None
    ic = any(k in name for k in IC_KEYS)
    return {"name": name, "ic": ic, "generic": True}
