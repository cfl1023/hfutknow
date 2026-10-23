# -*- coding: utf-8 -*-
"""规则分类：判断「活动 / 通知」与 13 个分类，抽取时间地点与报名标记。"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

ACTIVITY_CATEGORIES = {"arts", "recruitment", "lectures", "skills", "careers", "exchange"}

# 顺序即优先级：先命中先归类
RULES: list[tuple[str, list[str]]] = [
    ("lectures", ["讲座", "学术报告", "报告会", "论坛", "沙龙", "公开课", "讲堂", "研讨会", "学术会议", "名家讲坛"]),
    ("arts", ["演出", "音乐会", "话剧", "放映", "电影", "展览", "画展", "摄影展", "歌唱", "舞蹈", "相声",
              "京剧", "专场", "艺术", "运动会", "马拉松", "球赛", "联赛", "锦标赛", "文艺"]),
    ("recruitment", ["招新", "纳新", "招募", "社团", "志愿者", "义工", "支教", "社会实践", "加入我们"]),
    ("careers", ["招聘", "实习", "校招", "宣讲会", "岗位", "简历", "就业", "双选会", "选调", "职业发展"]),
    ("exchange", ["交换", "访学", "留学", "境外", "暑校", "国际交流", "海外学习", "联合培养"]),
    ("scholarships", ["奖学金", "助学金", "评优", "综测", "综合素质测评", "补助", "助学贷款", "荣誉称号"]),
    ("academics", ["选课", "考试", "成绩", "学籍", "学分", "毕业设计", "论文答辩", "教务", "转专业",
                   "辅修", "推免", "缓考", "重修", "培养方案"]),
    ("services", ["校园卡", "一卡通", "报修", "VPN", "补办", "预约", "缴费", "医保", "报销", "服务大厅",
                  "网络", "信息化", "证件"]),
    ("life", ["食堂", "宿舍", "校车", "班车", "热水", "供暖", "快递", "超市", "游泳", "健身", "餐饮",
              "后勤", "维修", "停水", "停电"]),
    ("research", ["科研", "成果", "论文", "发表", "基金", "课题", "实验室", "征稿", "专利", "立项"]),
    ("departments", ["学院", "院系", "教研室", "专业认证", "学科建设", "系主任", "教师"]),
    ("skills", ["培训", "工作坊", "竞赛", "大赛", "挑战赛", "训练营", "技能", "证书"]),
    ("campus", ["举行", "开幕", "落幕", "圆满", "典礼", "座谈会", "开放日", "校庆", "文化节", "新闻"]),
]

SIGNUP_RE = re.compile(r"报名|扫码|名额|限额|限\s*\d+\s*人|先到先得|注册链接|填写问卷")
DATE_RE = re.compile(r"(?:(\d{4})\s*年\s*)?(\d{1,2})\s*月\s*(\d{1,2})\s*日")
TIME_RE = re.compile(r"(上午|下午|晚上)?\s*(\d{1,2})\s*[:：]\s*(\d{2})")
PLACE_RE = re.compile(r"(?:地点|地址|会场|举办地)[:：\s]*([^\s，。；;]{2,30})")
PLACE_IN_RE = re.compile(r"在\s*([^\s，。；;]{2,30}?)\s*(?:举行|举办|召开|开展|开讲|进行|上演)")


def classify(title: str, text: str = "") -> tuple[str, str]:
    """返回 (intent, category)。"""
    haystack = f"{title} {text[:400]}"
    best_cat, best_hits = "campus", 0
    for cat, words in RULES:
        hits = sum(1 for w in words if w in haystack)
        if hits > best_hits:
            best_cat, best_hits = cat, hits
    if best_hits == 0:
        best_cat = "campus"
    intent = "activity" if best_cat in ACTIVITY_CATEGORIES else "information"
    return intent, best_cat


EVENT_CONTEXT = ("活动时间", "时间", "举行", "举办", "召开", "开展", "开始", "截止",
                 "报名", "开幕", "开讲", "讲座", "演出", "比赛", "会议")


def extract_event(text: str, now: datetime | None = None) -> dict[str, Any] | None:
    """尽力抽取活动时间与地点；只在日期附近出现活动类关键词时才认，避免把普通日期当活动。"""
    now = now or datetime.now()
    for m in DATE_RE.finditer(text):
        window = text[max(0, m.start() - 40): m.end() + 60]
        if not any(k in window for k in EVENT_CONTEXT):
            continue
        year = int(m.group(1)) if m.group(1) else now.year
        if not (2000 <= year <= now.year + 1):
            continue
        month, day = int(m.group(2)), int(m.group(3))
        hour, minute = 19, 0
        t = TIME_RE.search(text[m.end(): m.end() + 24])
        if t:
            hour, minute = int(t.group(2)), int(t.group(3))
            if t.group(1) in ("下午", "晚上") and hour < 12:
                hour += 12
        try:
            start = datetime(year, month, day, hour, minute)
        except ValueError:
            continue
        if start > now + timedelta(days=180):
            continue
        pm = PLACE_RE.search(window) or PLACE_IN_RE.search(window)
        location = pm.group(1).strip("，。；:：") if pm else None
        return {"start": start.isoformat(), "location": location}
    return None


def needs_signup(text: str) -> bool:
    return bool(SIGNUP_RE.search(text))


def keywords(title: str, limit: int = 3) -> list[str]:
    out: list[str] = []
    for _, words in RULES:
        for w in words:
            if w in title and w not in out:
                out.append(w)
    return out[:limit]
