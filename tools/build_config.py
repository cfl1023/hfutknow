# -*- coding: utf-8 -*-
"""生成 config.json 的站点、分类与信息源清单。

官方站点（type=official）的域名都经过 DNS/HTTP 核验，verified=true；
公众号（type=wechat）没有公开检索接口，需要人工确认，verified=false，
确认后把 verified 改成 true 即可。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SITE = {
    "name": "工大知道",
    "enName": "HFUT Know",
    "school": "合肥工业大学",
    "schoolEn": "Hefei University of Technology",
    "tagline": "把散落在合工大几百个公众号和官网里的信息，收进同一个页面",
    "description": "合肥工业大学翡翠湖校区的讲座、活动、招新、奖学金与教务通知聚合站，全天自动更新。",
    "url": "https://hfutknow.example",
    "campuses": ["翡翠湖校区"],
    "profile": {
        "name": "我",
        "college": "集成电路",
        "grade": "大一",
        "major": "集成电路设计与集成系统",
        "keywords": ["集成电路", "芯片", "半导体", "微电子", "电子科学", "专业分流", "培养方案",
                     "大一", "新生", "军训", "报到", "入学", "选课", "转专业", "奖学金", "竞赛"],
        "preferSources": ["hfut-ic", "wx-ic-lab", "wx-micro", "hfut-jwc", "hfut-xgb", "hfut-yjsy"]
    },
}

CATEGORIES = [
    {"id": "arts", "intent": "activity", "zh": "文体", "en": "Arts & Sports", "desc": "演出、电影、展览、游园与体育赛事"},
    {"id": "recruitment", "intent": "activity", "zh": "社团", "en": "Clubs", "desc": "社团招新、学生组织、志愿服务与社会实践"},
    {"id": "lectures", "intent": "activity", "zh": "讲座", "en": "Lectures", "desc": "讲座、论坛、公开课与现场交流活动"},
    {"id": "skills", "intent": "activity", "zh": "学习", "en": "Workshops", "desc": "技能培训、阅读分享、学科竞赛与课外实践"},
    {"id": "careers", "intent": "activity", "zh": "就业", "en": "Careers", "desc": "实习招聘、学生助理、选调宣讲与职业发展机会"},
    {"id": "exchange", "intent": "activity", "zh": "留学", "en": "Exchange", "desc": "交换留学、境外暑校、访学与出国项目申请"},
    {"id": "campus", "intent": "information", "zh": "校园", "en": "Campus", "desc": "学校新闻、活动回顾、人物故事与校园综合消息"},
    {"id": "research", "intent": "information", "zh": "科研", "en": "Research", "desc": "科研成果、学术进展、学术会议纪要与研究资讯"},
    {"id": "departments", "intent": "information", "zh": "院系", "en": "Departments", "desc": "院系通知、院系新闻、培养介绍与单位动态"},
    {"id": "life", "intent": "information", "zh": "生活", "en": "Life", "desc": "食宿出行、运动入门、假期安全、消费优惠、场馆开放"},
    {"id": "academics", "intent": "information", "zh": "学业", "en": "Academics", "desc": "选课考试、学籍学位、证书课程与学分办理"},
    {"id": "scholarships", "intent": "information", "zh": "奖学金", "en": "Scholarships", "desc": "奖学金、助学贷款、补助、综测与荣誉评选办理"},
    {"id": "services", "intent": "information", "zh": "服务", "en": "Services", "desc": "住宿餐饮、场馆、网络、维修、健康服务及校园卡办理"},
]

# (id, 名称, 分类亲和, 官网地址)  —— 域名与首页标题均已核验
OFFICIAL = [
    ("hfut-edu", "合肥工业大学官网", ["campus", "research", "departments"], "https://www.hfut.edu.cn/"),
    ("hfut-news", "合肥工业大学新闻网", ["campus", "research"], "https://news.hfut.edu.cn/"),
    ("hfut-jwc", "合肥工业大学教务处", ["academics", "scholarships"], "https://jwc.hfut.edu.cn/"),
    ("hfut-kyy", "合肥工业大学科研院", ["research", "academics"], "https://kyy.hfut.edu.cn/"),
    ("hfut-lib", "合肥工业大学图书馆", ["academics", "services", "life"], "https://lib.hfut.edu.cn/"),
    ("hfut-xgb", "党委学生工作部", ["scholarships", "life", "services"], "https://xgb.hfut.edu.cn/"),
    ("hfut-xcb", "党委宣传部", ["campus", "research"], "https://xcb.hfut.edu.cn/"),
    ("hfut-cwc", "合肥工业大学财务处", ["services", "academics"], "https://cwc.hfut.edu.cn/"),
    ("hfut-rsc", "党委教师工作部、人力资源处", ["departments", "careers"], "https://rsc.hfut.edu.cn/"),
    ("hfut-yjsy", "合肥工业大学研究生院", ["academics", "research"], "https://yjsy.hfut.edu.cn/"),
    ("hfut-ic", "合肥工业大学集成电路创新学院", ["departments", "research"], "https://ic.hfut.edu.cn/"),
    ("hfut-ci", "计算机与信息学院（人工智能学院）", ["departments", "research", "careers"], "https://ci.hfut.edu.cn/"),
    ("hfut-civil", "土木与水利工程学院", ["departments", "research"], "https://civil.hfut.edu.cn/"),
    ("hfut-jxjy", "合肥工业大学继续教育学院", ["academics", "services"], "https://jxjy.hfut.edu.cn/"),
    ("hfut-bkzs", "合肥工业大学本科招生网", ["campus", "academics"], "https://bkzs.hfut.edu.cn/"),
    ("hfut-jjc", "基建与房屋管理处", ["life", "services"], "https://jjc.hfut.edu.cn/"),
    ("hfut-tzb", "党委统战部", ["departments", "campus"], "https://tzb.hfut.edu.cn/"),
    ("hfut-jjh", "合工大教育基金会", ["scholarships", "campus"], "https://jjh.hfut.edu.cn/"),
    ("hfut-me", "市政工程系", ["departments", "research"], "https://me.hfut.edu.cn/"),
    ("hfut-tiyu", "合肥工业大学体育部", ["arts", "life"], "https://tiyu.hfut.edu.cn/"),
    ("hfut-mks", "马克思主义学院", ["departments", "lectures"], "https://mks.hfut.edu.cn/"),
    ("hfut-xyy", "校医院", ["services", "life"], "https://xyy.hfut.edu.cn/"),
]

# 公众号（命名按合工大常见习惯，需人工确认后把 verified 置为 true）
WECHAT = [
    # —— 校级官方 ——
    ("wx-hfut", "合肥工业大学", ["campus", "research"]),
    ("wx-hfut-youth", "合肥工业大学团委", ["campus", "recruitment", "arts"]),
    ("wx-hfut-su", "合肥工业大学学生会", ["arts", "recruitment", "life"]),
    ("wx-hfut-gsu", "合肥工业大学研究生会", ["academics", "careers", "life"]),
    ("wx-hfut-jobs", "合工大就业", ["careers", "academics"]),
    ("wx-hfut-admission", "合肥工业大学本科招生", ["campus", "academics"]),
    ("wx-hfut-grad", "合肥工业大学研究生", ["academics", "research"]),
    ("wx-hfut-alumni", "合肥工业大学校友总会", ["campus", "careers"]),
    ("wx-hfut-lib", "合工大图书馆", ["academics", "services"]),
    ("wx-hfut-jwc", "合工大教务处", ["academics", "scholarships"]),
    ("wx-hfut-hqc", "合工大后勤", ["life", "services"]),
    ("wx-hfut-hospital", "合肥工业大学医院", ["services", "life"]),
    ("wx-hfut-nic", "合工大信息化", ["services", "academics"]),
    ("wx-hfut-cwc", "合工大财务", ["services", "academics"]),
    ("wx-hfut-intl", "合工大国际交流", ["exchange", "academics"]),
    ("wx-hfut-xgb", "合工大学工", ["scholarships", "life"]),
    ("wx-hfut-sports", "合工大体育", ["arts", "life"]),
    ("wx-hfut-security", "平安工大", ["life", "services"]),
    ("wx-hfut-union", "合工大工会", ["life", "campus"]),
    # —— 学院 ——
    ("wx-cme", "合工大机械学院", ["departments", "research"]),
    ("wx-material", "合工大材料学院", ["departments", "research"]),
    ("wx-ee", "合工大电气学院", ["departments", "research", "careers"]),
    ("wx-cs", "合工大计算机学院", ["departments", "research", "careers"]),
    ("wx-chem", "合工大化工学院", ["departments", "research"]),
    ("wx-civil", "合工大土木学院", ["departments", "research"]),
    ("wx-arch", "合工大建艺学院", ["departments", "arts"]),
    ("wx-res", "合工大资环学院", ["departments", "research"]),
    ("wx-micro", "合工大微电子学院", ["departments", "research"]),
    ("wx-phy", "合工大物理学院", ["departments", "research"]),
    ("wx-math", "合工大数学学院", ["departments", "research", "lectures"]),
    ("wx-mgmt", "合工大管理学院", ["departments", "lectures", "careers"]),
    ("wx-econ", "合工大经济学院", ["departments", "lectures", "careers"]),
    ("wx-law", "合工大文法学院", ["departments", "lectures"]),
    ("wx-fl", "合工大外国语学院", ["departments", "exchange", "lectures"]),
    ("wx-marx", "合工大马院", ["departments", "lectures"]),
    ("wx-auto", "合工大汽车学院", ["departments", "research", "careers"]),
    ("wx-food", "合工大食品学院", ["departments", "research"]),
    ("wx-instrument", "合工大仪器学院", ["departments", "research"]),
    ("wx-software", "合工大软件学院", ["departments", "careers"]),
    # —— 学生组织与社团 ——
    ("wx-volunteer", "合工大青年志愿者联合会", ["recruitment", "life"]),
    ("wx-art-troupe", "合工大艺术团", ["arts", "recruitment"]),
    ("wx-clubs", "合工大社团联合会", ["recruitment", "campus"]),
    ("wx-photo", "合工大摄影协会", ["recruitment", "arts"]),
    ("wx-running", "合工大跑步协会", ["arts", "recruitment"]),
    ("wx-scifi", "合工大科幻协会", ["recruitment", "arts"]),
    ("wx-debate", "合工大辩论队", ["recruitment", "skills"]),
    ("wx-drama", "合工大话剧社", ["arts", "recruitment"]),
    ("wx-astro", "合工大天文社", ["recruitment", "skills"]),
    ("wx-mun", "合工大模拟联合国", ["recruitment", "exchange"]),
    ("wx-guitar", "合工大吉他社", ["arts", "recruitment"]),
    ("wx-startup", "合工大创业协会", ["recruitment", "careers"]),
    ("wx-cs-club", "合工大计算机协会", ["skills", "recruitment"]),
    ("wx-robot", "合工大机器人协会", ["skills", "recruitment"]),
    ("wx-electron", "合工大电子协会", ["skills", "recruitment"]),
    ("wx-mcm", "合工大数学建模协会", ["skills", "academics"]),
    ("wx-english", "合工大英语角", ["skills", "exchange"]),
    ("wx-redcross", "合工大红十字会", ["recruitment", "life"]),
    ("wx-mind", "合工大心理健康协会", ["life", "skills"]),
    ("wx-career-club", "合工大职业发展协会", ["careers", "skills"]),
    ("wx-badminton", "合工大羽毛球协会", ["arts", "recruitment"]),
    ("wx-basketball", "合工大篮球协会", ["arts", "recruitment"]),
    ("wx-tabletennis", "合工大乒乓球协会", ["arts", "recruitment"]),
    ("wx-chess", "合工大棋类协会", ["skills", "recruitment"]),
    ("wx-cycling", "合工大骑行协会", ["arts", "recruitment"]),
    # —— 媒体与自媒体 ——
    ("wx-gongdaqingnian", "工大青年", ["campus", "arts"]),
    ("wx-feicuihu", "翡翠湖青年", ["campus", "life"]),
    ("wx-hubing", "斛兵青年", ["campus", "lectures"]),
    # —— 体育与文艺类社团 ——
    ("wx-tennis", "合工大网球协会", ["arts", "recruitment"]),
    ("wx-volleyball", "合工大排球协会", ["arts", "recruitment"]),
    ("wx-football", "合工大足球协会", ["arts", "recruitment"]),
    ("wx-swim", "合工大游泳协会", ["arts", "recruitment"]),
    ("wx-wushu", "合工大武术协会", ["arts", "recruitment"]),
    ("wx-dance", "合工大街舞社", ["arts", "recruitment"]),
    ("wx-anime", "合工大动漫社", ["arts", "recruitment"]),
    ("wx-hanfu", "合工大汉服社", ["arts", "recruitment"]),
    ("wx-calligraphy", "合工大书法协会", ["arts", "recruitment"]),
    ("wx-speech", "合工大演讲与口才协会", ["skills", "recruitment"]),
    ("wx-marketing", "合工大营销协会", ["careers", "skills"]),
    ("wx-finance", "合工大金融投资协会", ["careers", "skills"]),
    ("wx-fsaer", "合工大方程式赛车队", ["skills", "research"]),
    ("wx-acm", "合工大 ACM 集训队", ["skills", "academics"]),
    ("wx-security", "合工大网络安全协会", ["skills", "recruitment"]),
    ("wx-opensource", "合工大开源社区", ["skills", "recruitment"]),
    ("wx-eda", "合工大电子设计协会", ["skills", "recruitment"]),
    ("wx-energy", "合工大节能减排协会", ["skills", "research"]),
    ("wx-model", "合工大数学建模俱乐部", ["skills", "academics"]),
    # —— 科研机构与平台 ——
    ("wx-ai", "合工大人工智能研究院", ["research", "lectures"]),
    ("wx-ic-lab", "合工大集成电路研究院", ["research", "lectures"]),
    ("wx-nev", "合工大新能源汽车研究院", ["research", "careers"]),
    ("wx-mfg", "合工大智能制造研究院", ["research", "departments"]),
    ("wx-iiot", "合工大工业互联网研究院", ["research", "careers"]),
    ("wx-quantum", "合工大量子信息实验室", ["research", "lectures"]),
    ("wx-bme", "合工大生物医学工程学院", ["research", "departments"]),
    ("wx-ee-lab", "合工大电气工程实验中心", ["research", "academics"]),
    ("wx-chem-eng", "合工大化学工程系", ["departments", "research"]),
    ("wx-materials-lab", "合工大材料实验中心", ["research", "academics"]),
    # —— 职能处室与服务机构 ——
    ("wx-audit", "合工大审计处", ["services", "campus"]),
    ("wx-security-office", "合工大保卫处", ["life", "services"]),
    ("wx-procurement", "合工大招标采购", ["services", "campus"]),
    ("wx-archive", "合工大档案馆", ["services", "campus"]),
    ("wx-journal", "合工大学报", ["research", "academics"]),
    ("wx-retire", "合工大离退休工作处", ["life", "campus"]),
    ("wx-intl-edu", "合工大国际教育学院", ["exchange", "academics"]),
    ("wx-excellent", "合工大卓越工程师学院", ["academics", "careers"]),
    ("wx-innovation", "合工大创新创业学院", ["careers", "skills"]),
    ("wx-continuing", "合工大继续教育", ["academics", "services"]),
    ("wx-alumni-fund", "合工大教育基金会", ["scholarships", "campus"]),
    ("wx-dorm", "合工大宿舍管理", ["life", "services"]),
    ("wx-canteen", "合工大食堂", ["life", "services"]),
    ("wx-bus", "合工大班车", ["life", "services"]),
    ("wx-mental", "合工大心理咨询中心", ["life", "services"]),
    ("wx-career-center", "合工大学生就业指导中心", ["careers", "academics"]),
    # —— 招生与校友 ——
    ("wx-grad-admission", "合工大研究生招生", ["academics", "campus"]),
    ("wx-adult-edu", "合工大成人教育", ["academics", "services"]),
    ("wx-alumni-hf", "合工大合肥校友会", ["campus", "careers"]),
    ("wx-alumni-sh", "合工大上海校友会", ["campus", "careers"]),
    ("wx-alumni-sz", "合工大深圳校友会", ["campus", "careers"]),
]


def main() -> None:
    sources = []
    for sid, name, aff, url in OFFICIAL:
        sources.append({
            "id": sid, "name": name, "type": "official", "url": url,
            "verified": True, "checkedAt": "2026-10-23", "aff": aff,
            "feed": {"kind": "html_list", "url": url, "enabled": sid in {
                "hfut-edu", "hfut-news", "hfut-jwc", "hfut-kyy", "hfut-xgb", "hfut-xcb",
                "hfut-cwc", "hfut-rsc", "hfut-yjsy", "hfut-ic", "hfut-ci", "hfut-civil",
                "hfut-jxjy", "hfut-jjc", "hfut-tzb", "hfut-jjh", "hfut-me", "hfut-tiyu",
                "hfut-mks", "hfut-xyy",
            }, "limit": 10},
        })
    for sid, name, aff in WECHAT:
        sources.append({
            "id": sid, "name": name, "type": "wechat", "url": "",
            "verified": False, "checkedAt": "", "aff": aff, "feed": {"kind": "wechat", "enabled": False},
        })
    payload = {"site": SITE, "categories": CATEGORIES, "sources": sources}
    (ROOT / "config.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"sources={len(sources)} (official={len(OFFICIAL)}, wechat={len(WECHAT)})")


if __name__ == "__main__":
    main()
