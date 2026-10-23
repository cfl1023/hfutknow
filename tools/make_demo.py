# -*- coding: utf-8 -*-
"""生成一份可演示的「工大知道」数据集（合成内容，非真实抓取）。

站点配置、分类与信息源都在 config.json，这里只负责把示例内容填进去，
让前端在没有接入真实抓取时也能完整跑起来。
真实数据由 pipeline/sync.py 写入同一份 site/data/items.json。
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = SITE / "data"
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
TZ = timezone(timedelta(hours=8))
rng = random.Random(20261023)

VENUES = {
    "翡翠湖校区": [
        "翡翠湖校区图书馆报告厅", "翡翠湖校区综合楼 301", "翡翠湖校区大学生活动中心",
        "翡翠湖校区体育馆", "翡翠湖校区西操场", "翡翠湖校区学生事务大厅",
        "翡翠湖校区教学楼 A 座 101", "翡翠湖校区科创中心", "翡翠湖校区食堂三层",
    ],
    "线上": ["线上（腾讯会议）"],
}

SPEAKERS = ["张启明教授", "李文澜研究员", "王思远博士", "陈默副教授", "赵一鸣教授",
            "周予安研究员", "孙立群博士", "吴桐副教授", "郑海宁教授", "何雨薇博士"]

TOPICS = [
    ("智能网联汽车的技术路线与产业化", "从单车智能到车路云一体，梳理三条技术路线的成本与落地节奏。"),
    ("管理科学与工程：从运筹优化到产业决策", "以供应链与排产为例，看模型如何进入真实的企业决策。"),
    ("集成电路制造的国产化路径", "设备、材料与人才三个环节的现状与突破口。"),
    ("新能源汽车动力电池的技术进展", "从磷酸铁锂到固态电池，能量密度与安全性的权衡。"),
    ("人工智能时代的科学发现", "从 AlphaFold 到自动化实验室，AI 正在改写科研的工作方式。"),
    ("从《诗经》看先秦礼乐生活", "以文本细读还原三千年前的仪式、宴饮与日常。"),
    ("量子信息：从实验室到产业", "梳理超导与离子阱两条技术路线的最新进展。"),
    ("如何读懂一份财报", "三张表之间的勾稽关系，以及常见的美化手法。"),
    ("长三角一体化中的产业分工", "合肥在新能源汽车与新型显示产业链中的位置。"),
    ("古典诗词的声律之美", "平仄、押韵与吟诵传统的现场示范。"),
    ("脑机接口的现在与未来", "从侵入式电极到非侵入式解码的技术图谱。"),
    ("数据要素与数字经济", "数据确权、定价与流通的制度难题。"),
    ("数学之美：从欧拉到现代密码", "一条从数论到公钥密码的思想线索。"),
    ("大国博弈与全球产业链重构", "用结构现实主义解释当下的秩序重组。"),
    ("医学人文：疾病叙事的力量", "当医学遇到文学，如何理解病痛与照护。"),
    ("城市更新中的遗产保护", "老街区改造中的价值判断与利益协调。"),
]
SERIES = ["工大讲堂", "斛兵学者论坛", "翡翠湖讲坛", "青年科学家沙龙", "研究生学术论坛"]

SHOWS = [("《雷雨》学生版话剧", "大学生艺术团年度大戏，全本三小时，连演两场。"),
         ("新年音乐会", "学生交响乐团与合唱团联袂演出。"),
         ("古典舞专场《山河》", "以山水意象贯穿的十支原创群舞。"),
         ("相声专场「说学逗唱」", "校园相声社封箱演出。"),
         ("校园十佳歌手大赛决赛", "十强选手同台竞演。"),
         ("京剧《四郎探母》", "名家进校园，含演后谈。"),
         ("现代舞工作坊展演", "工作坊六周成果公开展示。")]
FILMS = ["《海上钢琴师》", "《星际穿越》", "《一一》", "《饮食男女》", "《长安三万里》", "《布达佩斯大饭店》"]
EXHIBITS = ["「四时」校园摄影展", "「字里行间」书籍设计展", "「山海」插画原作展", "「光的形状」影像装置展"]
SPORTS = ["翡翠湖环湖跑", "校运动会", "院系篮球联赛", "羽毛球公开赛", "冬季长跑活动"]

CLUBS = ["青年志愿者联合会", "摄影协会", "辩论队", "创新创业协会", "科幻协会",
         "跑步协会", "话剧社", "天文社", "模拟联合国协会", "吉他社"]

WORKSHOPS = ["Python 数据分析入门", "文献检索与 Zotero 使用", "学术写作与论文投稿",
             "摄影后期基础", "公众表达与演讲训练", "Excel 高阶技巧", "Figma 界面设计入门"]

COMPANIES = ["奇瑞汽车", "蔚来汽车", "江淮汽车", "京东方", "长鑫存储", "科大讯飞",
             "阳光电源", "国轩高科", "华为", "国家电网"]

SCHOOLS = ["加州大学伯克利分校", "东京大学", "新加坡国立大学", "爱丁堡大学",
           "苏黎世联邦理工学院", "香港大学", "墨尔本大学"]

ACADEMIC_ITEMS = ["春季学期选课", "期中考试安排", "毕业设计开题", "辅修专业申请",
                  "成绩复核申请", "校外学分认定", "转专业申请", "推免资格申请"]
SCHOLARSHIPS = ["国家奖学金", "校长奖学金", "励志奖学金", "学业优秀奖学金",
                "创新奖学金", "助学金", "综合测评优秀奖"]
LIFE_ITEMS = ["翡翠湖校区食堂开放时间调整", "校区班车时刻表调整", "翡翠湖校区游泳馆开放安排",
              "宿舍热水供应时间调整", "校园网提速升级", "快递驿站搬迁", "供暖试水通知",
              "图书馆延长开放"]
SERVICE_ITEMS = ["校园卡挂失补办", "电子成绩单申请", "校园 VPN 使用指南", "馆际互借规则调整",
                 "宿舍报修流程", "医保报销指南", "一卡通充值渠道变更"]
CAMPUS_NEWS = ["校运动会圆满落幕", "新生开学典礼举行", "校园开放日接待三千余人",
               "毕业季影像征集启动", "校园文化节开幕", "翡翠湖校区图书馆改造完工"]
RESEARCH_NEWS = ["团队在《Nature》子刊发表柔性传感新成果", "国家自然科学基金立项数创新高",
                 "重点实验室开放课题开始申报", "国际学术会议征稿通知", "交叉研究平台正式启用"]
DEPT_NEWS = ["学院召开本科教学工作会议", "学院举办师生座谈会", "学科建设研讨会举行",
             "工程教育专业认证推进会", "青年教师教学比赛落幕"]

TIME_SLOTS = ["09:00", "10:00", "14:00", "15:30", "18:30", "19:00", "19:30", "20:00"]


def pick(lst):
    return rng.choice(lst)


def venue(campus: str | None = None) -> str:
    campus = campus or rng.choices(["翡翠湖校区", "线上"], [9, 1])[0]
    return pick(VENUES[campus])


def cn_date(dt: datetime) -> str:
    return f"{dt.month}月{dt.day}日"


def cn_weekday(dt: datetime) -> str:
    return "周" + "一二三四五六日"[dt.weekday()]


def source_for(cat_id: str) -> dict:
    pool = [s for s in CONFIG["sources"] if cat_id in s["aff"]]
    return pick(pool) if pool else pick(CONFIG["sources"])


def published_time(now: datetime) -> datetime:
    days = min(6.0, rng.expovariate(0.55))
    dt = now - timedelta(days=days, minutes=rng.randint(0, 1439))
    return dt.replace(second=0, microsecond=0)


def event_time(now: datetime) -> datetime:
    days = rng.randint(-1, 20)
    hour, minute = map(int, pick(TIME_SLOTS).split(":"))
    return (now + timedelta(days=days)).replace(hour=hour, minute=minute, second=0, microsecond=0)


def body(cat: str, title: str, source: dict, ev: dict | None, signup: bool) -> list[str]:
    when = ""
    if ev:
        start = datetime.fromisoformat(ev["start"])
        when = f"{cn_date(start)}（{cn_weekday(start)}）{start:%H:%M}"
    place = f"，地点在{ev['location']}" if ev and ev.get("location") else ""
    tail = f"以上信息由{source['name']}整理发布，如有调整以原通知为准。"

    if cat == "lectures":
        return [
            f"讲座将于{when}{place}举行。主讲人将结合近年的研究进展，系统梳理该领域的核心问题与方法演进，并在问答环节与现场听众交流。",
            "本次讲座面向全校师生开放，无需提前报名。建议提前十分钟入场，讲座结束后可凭校园卡领取讲座记录单。",
            tail,
        ]
    if cat == "arts":
        note = "需要报名的场次请留意报名入口，名额有限，先到先得。" if signup else "凭校园卡入场，座位先到先得。"
        return [
            f"演出时间为{when}{place}。{note}",
            "请观众提前十五分钟到场，演出开始后请勿随意走动；场内禁止摄影摄像与饮食。",
            tail,
        ]
    if cat == "recruitment":
        return [
            f"招募说明会安排在{when}{place}。负责同学将介绍组织架构、日常活动与本次招募的岗位设置。",
            "报名不限年级与专业，欢迎带着问题来现场交流。面试安排将在报名截止后通过短信通知。",
            tail,
        ]
    if cat == "skills":
        return [
            f"工作坊共两次课，首次课程于{when}{place}开始。请自带笔记本电脑，并提前安装所需软件。",
            "课程以实操为主，完成全部练习后可获得结业证明。名额三十人，报满即止。",
            tail,
        ]
    if cat == "careers":
        return [
            f"宣讲会于{when}{place}举行，现场将介绍岗位方向、培养体系与招聘流程，并安排简历门诊。",
            "请携带纸质简历若干份，着装整洁。部分岗位现场收取简历并安排初面。",
            tail,
        ]
    if cat == "exchange":
        return [
            f"项目说明会于{when}{place}举行，国际处老师将解读申请条件、语言要求、学分转换与资助政策。",
            "申请材料包括成绩单、语言成绩与个人陈述，截止时间以项目页面为准，逾期不再受理。",
            tail,
        ]
    if cat == "academics":
        return [
            f"根据教学安排，{title}的相关事项已发布。请同学登录教务系统查看个人适用条款，并在规定时间内完成操作。",
            "如遇系统异常或对结果有疑问，可在工作日联系所在院系教务老师，或通过教务处服务窗口咨询。",
            tail,
        ]
    if cat == "scholarships":
        return [
            f"{title}的评选工作现已启动。评审依据包括学业成绩、科研表现与综合素质测评结果，具体名额分配见附件。",
            "请符合条件的同学按要求提交材料，逾期视为放弃。评审结果将在公示期后正式公布。",
            tail,
        ]
    if cat == "life":
        return [
            f"为配合校园运行安排，{title}。具体调整自本周起执行，请师生留意现场公告与线上通知。",
            "带来不便敬请谅解。如有疑问，可拨打后勤服务热线或在「合工大微后勤」小程序内提交工单。",
            tail,
        ]
    if cat == "services":
        return [
            f"{title}的办理流程已更新。师生可通过线上服务大厅提交申请，部分业务需携带证件到窗口办理。",
            "办理时间为工作日 8:30—11:30、13:30—17:00，节假日安排另行通知。",
            tail,
        ]
    if cat == "campus":
        return [
            f"{title}。活动现场气氛热烈，参与师生超过八百人次，相关影像与报道已同步发布。",
            "本次活动是校园文化建设的重要组成部分，后续还将推出系列配套活动，欢迎持续关注。",
            tail,
        ]
    if cat == "research":
        return [
            f"{title}。研究成果近日发表于国际期刊，审稿人评价其方法在灵敏度与稳定性上均有明显提升。",
            "该工作得到国家自然科学基金与校级交叉研究项目的支持，相关数据与代码已按开放科学规范公开。",
            tail,
        ]
    return [
        f"{title}。会议围绕人才培养方案修订、课程体系建设与教学质量保障展开讨论。",
        "与会教师就课时分配、实践环节与考核方式提出了具体建议，相关意见将纳入下一阶段工作方案。",
        tail,
    ]


def build_item(cat: dict, now: datetime) -> dict:
    src = source_for(cat["id"])
    pub = published_time(now)
    cat_id = cat["id"]
    ev = None
    signup = False
    tags: list[str] = []

    if cat_id == "lectures":
        topic, lead = pick(TOPICS)
        series = pick(SERIES)
        speaker = pick(SPEAKERS)
        title = f"{series}｜{topic}"
        place = venue()
        et = event_time(now).replace(hour=rng.choice([14, 15, 18, 19]), minute=rng.choice([0, 30]))
        ev = {"start": et.isoformat(), "location": place, "speaker": speaker}
        summary = f"{speaker}主讲，{cn_date(et)}（{cn_weekday(et)}）{et:%H:%M} 在{place}举行。{lead}"
        tags = ["讲座", topic[:6]]
    elif cat_id == "arts":
        kind = rng.choices(["show", "film", "exhibit", "sport"], [4, 3, 2, 2])[0]
        if kind == "show":
            name, lead = pick(SHOWS)
            title = f"开售｜{name}"
            signup = rng.random() < 0.5
        elif kind == "film":
            title = f"放映｜{pick(FILMS)}"
            lead = "大学生活动中心影院本周放映，含映后交流。"
            signup = rng.random() < 0.35
        elif kind == "exhibit":
            title = f"展览｜{pick(EXHIBITS)}"
            lead = "展期两周，免费参观。"
        else:
            title = f"赛事｜{pick(SPORTS)}"
            lead = "报名通道已开启，欢迎组队参加。"
            signup = True
        et = event_time(now)
        place = venue()
        ev = {"start": et.isoformat(), "location": place}
        summary = f"{lead}时间：{cn_date(et)}（{cn_weekday(et)}）{et:%H:%M}；地点：{place}。" + ("需提前报名。" if signup else "凭校园卡入场。")
        tags = ["文体", kind]
    elif cat_id == "recruitment":
        club = pick(CLUBS)
        title = f"招新｜{club}秋季招新"
        et = event_time(now)
        place = venue()
        ev = {"start": et.isoformat(), "location": place}
        signup = True
        summary = f"{club}面向全校招新，说明会 {cn_date(et)}（{cn_weekday(et)}）{et:%H:%M} 在{place}举行。报名后统一安排面试。"
        tags = ["社团", club]
    elif cat_id == "skills":
        ws = pick(WORKSHOPS)
        title = f"工作坊｜{ws}"
        et = event_time(now)
        place = venue()
        ev = {"start": et.isoformat(), "location": place}
        signup = True
        summary = f"两课时实操工作坊，{cn_date(et)}（{cn_weekday(et)}）{et:%H:%M} 在{place}开课，限额 30 人。"
        tags = ["技能", ws]
    elif cat_id == "careers":
        company = pick(COMPANIES)
        title = f"宣讲会｜{company}2027 届校园招聘"
        et = event_time(now).replace(hour=rng.choice([14, 18, 19]), minute=0)
        place = venue()
        ev = {"start": et.isoformat(), "location": place}
        signup = True
        summary = f"{company}校招宣讲，{cn_date(et)}（{cn_weekday(et)}）{et:%H:%M} 在{place}举行，现场收简历。"
        tags = ["就业", company]
    elif cat_id == "exchange":
        school = pick(SCHOOLS)
        title = f"交换项目｜{school} 2027 春季学期访学"
        et = event_time(now)
        place = venue()
        ev = {"start": et.isoformat(), "location": place}
        signup = True
        summary = f"项目说明会 {cn_date(et)}（{cn_weekday(et)}）{et:%H:%M}，{place}。申请截止见项目页面，需提交成绩单与语言成绩。"
        tags = ["留学", school]
    elif cat_id == "academics":
        thing = pick(ACADEMIC_ITEMS)
        title = f"关于{thing}的通知"
        summary = f"{thing}已开放办理，请登录教务系统确认个人安排，注意各环节截止时间。"
        tags = ["学业"]
    elif cat_id == "scholarships":
        sch = pick(SCHOLARSHIPS)
        title = f"关于评选{sch}的通知"
        summary = f"{sch}评选启动，需提交成绩单与证明材料，名额与评审细则见附件，逾期不予受理。"
        tags = ["奖学金", sch]
    elif cat_id == "life":
        title = pick(LIFE_ITEMS)
        summary = f"{title}，具体安排已发布，请师生留意时间变化，合理安排行程。"
        tags = ["生活"]
    elif cat_id == "services":
        thing = pick(SERVICE_ITEMS)
        title = f"{thing}指南"
        summary = f"{thing}支持线上办理，材料清单与办理时限已更新，可在服务大厅查看。"
        tags = ["服务"]
    elif cat_id == "campus":
        title = pick(CAMPUS_NEWS)
        summary = f"{title}。活动吸引众多师生参与，相关报道与影像已发布。"
        tags = ["校园"]
    elif cat_id == "research":
        title = pick(RESEARCH_NEWS)
        summary = f"{title}，成果发表于国际期刊，获国家自然科学基金支持。"
        tags = ["科研"]
    else:
        title = pick(DEPT_NEWS)
        summary = f"{title}，会议就人才培养与课程建设作出部署，相关方案将陆续公布。"
        tags = ["院系"]

    content = body(cat_id, title, src, ev, signup)
    item_id = f"{src['id']}-{int(pub.timestamp())}-{rng.randint(100, 999)}"
    return {
        "id": item_id,
        "title": title,
        "sourceId": src["id"],
        "sourceName": src["name"],
        "sourceType": src["type"],
        "url": f"https://example.edu/{quote(src['id'])}/{item_id}",
        "publishedAt": pub.isoformat(),
        "intent": cat["intent"],
        "category": cat_id,
        "summary": summary,
        "event": ev,
        "requiresSignup": signup,
        "tags": tags,
        "content": [f"<p>{p}</p>" for p in content],
        "demo": True,
    }


def main() -> None:
    now = datetime.now(TZ).replace(minute=0, second=0, microsecond=0)
    per_category = {"arts": 108, "recruitment": 104, "lectures": 128, "skills": 88,
                    "careers": 78, "exchange": 42, "campus": 146, "research": 116,
                    "departments": 148, "life": 96, "academics": 118,
                    "scholarships": 76, "services": 78}
    items = []
    for cat in CONFIG["categories"]:
        for _ in range(per_category[cat["id"]]):
            items.append(build_item(cat, now))
    items.sort(key=lambda x: x["publishedAt"], reverse=True)

    # 保证每个来源至少有一条，来源目录里不会出现 0 条的孤儿
    covered = {it["sourceId"] for it in items}
    cat_by_id = {c["id"]: c for c in CONFIG["categories"]}
    for src in CONFIG["sources"]:
        if src["id"] in covered:
            continue
        cat = cat_by_id[src["aff"][0]]
        item = build_item(cat, now)
        item["sourceId"], item["sourceName"], item["sourceType"] = src["id"], src["name"], src["type"]
        item["url"] = f"https://example.edu/{quote(src['id'])}/{item['id']}"
        items.append(item)

    counts: dict[str, int] = {}
    for it in items:
        counts[it["sourceId"]] = counts.get(it["sourceId"], 0) + 1
    sources = [{**s, "count": counts.get(s["id"], 0)} for s in CONFIG["sources"]]

    payload = {
        "generatedAt": now.isoformat(),
        "demo": True,
        "site": CONFIG["site"],
        "categories": CONFIG["categories"],
        "items": items,
    }
    DATA.mkdir(parents=True, exist_ok=True)
    existing_path = DATA / "items.json"
    if existing_path.exists():
        try:
            old = json.loads(existing_path.read_text(encoding="utf-8"))
            keep = [i for i in old.get("items", []) if not i.get("demo")]
            if keep:
                items.extend(keep)
                items.sort(key=lambda x: x["publishedAt"], reverse=True)
                payload["items"] = items
                payload["demo"] = False
                print(f"保留真实条目 {len(keep)} 条")
        except Exception as exc:
            print("读取旧数据失败，忽略：", exc)
    (DATA / "items.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    (DATA / "sources.json").write_text(
        json.dumps({"sources": sources}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"items={len(items)} sources={len(sources)} -> {DATA}")


if __name__ == "__main__":
    main()
