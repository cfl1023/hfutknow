# 工大知道 · HFUT Know

合肥工业大学（翡翠湖校区）讲座、活动、招新、奖学金、教务通知的聚合站。
把散落在几十个官网和上百个公众号里的公开信息收进同一个页面：分类浏览、搜索、活动日历、AI 摘要、来源目录。

> 现状：**139 个信息源**（22 个官网已核验 + 117 个公众号待核验），**1425 条信息**，其中 **99 条为真实抓取**（教务处、科研院、学工部、计算机学院等 20 个官网），其余为演示数据。

## 现在已经能用的

| 功能 | 说明 |
| --- | --- |
| 聚合首页 | 瀑布流卡片，按发布时间排序，支持「最新发布 / 即将开始」切换 |
| 分类筛选 | 活动（文体/社团/讲座/学习/就业/留学）+ 通知（校园/科研/院系/生活/学业/奖学金/服务） |
| 搜索 | 标题、摘要、来源名、标签全文匹配，命中高亮 |
| 活动日历 | 按周排布，可前后翻周，点任意一条进详情 |
| 来源目录 | 139 个来源，按公众号/官网分组，显示条数与核验状态 |
| 详情页 | AI 摘要、时间地点、原文正文、来源链接、报名标记 |
| 暗色模式 / 英文界面 / 手机单列 | 右上角切换，偏好存在本地 |
| RSS 与 JSON | `/data/feed.xml`、`/data/items.json` |

## 快速开始

只依赖 Python 3 标准库（抓取管线额外需要 `lxml`）：

```bash
python serve.py            # 默认 http://127.0.0.1:8710
python serve.py 9000       # 换端口
```

不要直接双击 `site/index.html`——页面用 `fetch` 读 JSON，需要 HTTP 服务。

## 目录结构

```
campusknow/
├─ config.json            # 站点信息、分类、全部信息源（唯一的配置源）
├─ site/                  # 可直接部署的静态站点
│  ├─ index.html / app.js / style.css
│  └─ data/               # items.json（内容）、sources.json、feed.xml
├─ pipeline/              # 抓取管线
│  ├─ common.py           # HTTP / HTML / JSON 工具
│  ├─ fetchers.py         # RSS、官网列表页、公众号文章适配器
│  ├─ classify.py         # 活动/通知、13 个分类、时间地点、报名标记
│  ├─ summarize.py        # 规则摘要 + 可选 LLM 摘要
│  └─ sync.py             # 抓取 → 入库 → 去重
├─ tools/
│  ├─ build_config.py     # 生成 config.json（来源清单在这里维护）
│  ├─ make_demo.py        # 生成演示数据
│  ├─ make_rss.py         # 导出 RSS
│  └─ reset_real.py       # 清掉已抓取条目，保留演示数据
└─ serve.py
```

## 抓取真实数据

```bash
python -m pipeline.sync                          # 所有已启用来源，每源 12 条
python -m pipeline.sync --only hfut-jwc,hfut-kyy  # 只抓指定来源
python -m pipeline.sync --limit 5 --enrich        # 逐篇抓正文（摘要更准，慢）
python -m pipeline.sync --dry-run                 # 只看抓到什么，不写文件
python -m pipeline.sync --drop-demo               # 清掉演示数据，只留真实的
python tools/make_rss.py                          # 重新生成 feed.xml
```

抓取逻辑是**通用列表页启发式**：解析页面所有链接，按「链接里有 /info/、/content/ 这类文章路径 + 邻近位置有日期」打分排序，再逐篇抽取正文（按段落密度选容器，剔除导航、版权、面包屑）。所以大多数 Webplus/CMS 站点不用写选择器就能用；特殊站点可在 `config.json` 里给该源加 `feed.item_xpath` 覆盖。

正文抽取后还有一道过滤：命中「仅允许校内地址访问」的页面直接跳过——合工大不少通知是校内可见，抓不到正文。

## 信息源

`config.json` 里每个来源：

```json
{
  "id": "hfut-jwc",
  "name": "合肥工业大学教务处",
  "type": "official",          // official | wechat
  "url": "https://jwc.hfut.edu.cn/",
  "verified": true,            // 域名和首页标题都核验过
  "checkedAt": "2026-10-23",
  "aff": ["academics", "scholarships"],
  "feed": { "kind": "html_list", "url": "https://jwc.hfut.edu.cn/", "enabled": true, "limit": 10 }
}
```

**已核验官网 22 个**：学校官网、新闻网、教务处、科研院、图书馆、学工部、宣传部、财务处、人力资源处、研究生院、集成电路创新学院、计算机与信息学院、土木与水利工程学院、继续教育学院、本科招生网、基建与房屋管理处、统战部、教育基金会、市政工程系、体育部、马克思主义学院、校医院。

**公众号 117 个**：按合工大实际单位结构铺开（校团委、就业、图书馆、后勤、各学院、社团、校友会等），但微信没有公开检索接口，`verified` 一律是 `false`。要变成真的，三条路：

1. **第三方 RSS**（如 WeRSS、feeddd 一类服务）把公众号转成 RSS feed，`feed.kind` 改成 `rss`；
2. **运营者授权**：公众号管理员在后台开白名单 / 提供文章链接，`feed.kind` 用 `wechat`，把文章 URL 填进 `feed.articles`；
3. **人工补充**：编辑看到就贴链接，最土但最稳——`#/contribute` 页面就是给这个用的。

## 摘要

默认是规则摘要：从正文里挑含「时间/地点/报名/截止」的句子，拼上抽取到的时间地点。
想接大模型，在 `config.json` 里加：

```json
"llm": { "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat", "api_key_env": "OPENAI_API_KEY" }
```

然后 `export OPENAI_API_KEY=...` 再跑 sync，摘要就会走 LLM，失败自动回退规则摘要。

## 部署

`site/` 是纯静态目录，扔到 Nginx、Cloudflare Pages、GitHub Pages 都能跑。
定时更新用 cron：

```cron
*/30 * * * * cd /srv/campusknow && python -m pipeline.sync --limit 10 && python tools/make_rss.py
```

## 换学校 / 换校区

- 校名、域名、校区：`config.json` 的 `site`
- 来源清单：改 `tools/build_config.py` 的 `OFFICIAL` / `WECHAT`，重跑 `python tools/build_config.py`
- 场馆与示例内容：`tools/make_demo.py`

## 已知限制

- **演示数据占多数**：1326 条是按模板生成的，`demo: true`，页脚会标「其中 N 条演示数据」。跑 `--drop-demo` 可清空。
- 公众号全部未接入，来源目录里标「待核验」。
- 分类靠关键词规则，边界情况会分错（比如「宣讲会」可能落到社团）。
- 时间地点抽取只认日期附近出现「举行/报名/截止」等词的句子，宁可漏，不乱填。
- 校内可见的通知抓不到正文，会被跳过。
