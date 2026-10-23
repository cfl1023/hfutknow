# 工大知道 · HFUT Know

合肥工业大学（翡翠湖校区）校园信息聚合站。把散落在官网和公众号里的讲座、活动、招新、奖学金、教务通知收进一个页面：分类浏览、搜索、活动日历、摘要、来源目录，按「集成电路大一」的个人偏好排序。

**当前状态**：387 条真实信息，来自 32 个已核验官网（教务处、科研院、学工部、计算机学院、集成电路创新学院等），每条都能点开原文。公众号暂未接入。

## 功能

| 功能 | 说明 |
| --- | --- |
| 聚合首页 | 瀑布流卡片；默认「为你推荐」，按专业/年级相关度排序 |
| 个性化 | 「与我相关」筛选；集成电路、芯片、选课、奖学金、新生等关键词加权 |
| 详情面板 | 右侧滑出，不离开列表，Esc/遮罩/关闭按钮都能退 |
| 搜索 | 标题、摘要、来源、标签全文匹配 |
| 日历 | 按周排布活动，可翻周 |
| 来源目录 | 139 个来源，标注「已核验 / 待核验」和各自条数 |
| 原文 | 每条真实信息直达官网原文；演示数据会标灰并说明 |
| 暗色 / 英文 / 手机 | 本地记忆偏好；手机单列，可加到主屏幕（PWA） |
| RSS / JSON | `/data/feed.xml`、`/data/items.json` |

## 本地运行

```bash
python serve.py            # 本机 http://127.0.0.1:8710
python serve.py 9000       # 换端口
```

`serve.py` 绑定 0.0.0.0，启动时会打印手机可用的局域网地址。

不想装 Python？直接双击 `..\工大知道.html`（单文件版，约 0.6 MB，离线可看）。

## 自动更新

**方案 A（推荐）**：GitHub Actions 每 30 分钟抓取并发布到 Pages，电脑不用开机。
详见 [`deploy/README.md`](deploy/README.md)。

**方案 B**：本机计划任务，电脑开着时每 30 分钟更新：

```powershell
powershell -ExecutionPolicy Bypass -File tools\install-task.ps1
```

**手动一次**：双击 `update.bat`。

## 目录

```
campusknow/
├─ config.json            # 站点、分类、139 个信息源、个人偏好（唯一配置源）
├─ site/                  # 静态站点（可直接部署）
│  ├─ index.html / app.js / style.css / sw.js / manifest.webmanifest
│  └─ data/               # items.json、sources.json、feed.xml
├─ pipeline/
│  ├─ common.py           # HTTP、HTML、JSON 工具
│  ├─ fetchers.py         # RSS / 官网列表页 / 公众号文章 适配器
│  ├─ classify.py         # 分类、时间地点、报名标记
│  ├─ summarize.py        # 规则摘要 + 可选 LLM
│  └─ sync.py             # 抓取 → 入库 → 去重
├─ tools/                 # 生成配置、图标、RSS、单文件、计划任务
├─ deploy/README.md       # GitHub Pages / Cloudflare Pages 部署
├─ update.bat             # 一键更新
└─ serve.py
```

## 抓取

```bash
python -m pipeline.sync --limit 15 --enrich   # 全部启用来源
python -m pipeline.sync --only hfut-jwc        # 只抓教务处
python -m pipeline.sync --dry-run              # 只看抓到了什么
python tools/make_rss.py                       # 重新生成 RSS
```

列表页用通用启发式解析：链接路径像文章（`/info/`、`/content/`、`/20xx/`）+ 邻近位置有日期 → 打分排序；正文按段落密度选容器，剔除导航、面包屑、版权。特殊站点可在 `config.json` 给该源加 `feed.item_xpath` 覆盖。

命中「仅允许校内地址访问」的页面直接跳过。

## 信息源

22 个官网已核验（DNS + 首页标题），117 个公众号待核验。微信没有公开检索接口，三条路：

1. 第三方 RSS 服务把公众号转成 feed（`feed.kind` 改 `rss`）；
2. 公众号运营者授权，提供文章链接（`feed.articles`）；
3. 人工补充，`#/contribute` 页面就是入口。

## 摘要

默认规则摘要：挑含「时间/地点/报名/截止」的句子，拼上抽取到的时间地点。
接大模型：`config.json` 里加

```json
"llm": { "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat", "api_key_env": "OPENAI_API_KEY" }
```

`export OPENAI_API_KEY=...` 后跑 sync，失败自动回退规则摘要。

## 已知限制

- 公众号未接入，来源目录里 117 个标「待核验」，暂时没有内容。
- 分类是关键词规则，边界情况会分错（如「宣讲会」偶尔落到社团）。
- 时间地点只认日期附近出现「举行/报名/截止」等词的句子，宁可漏也不乱填。
- 校内可见的通知抓不到正文，会被跳过。
- GitHub Actions 的定时任务有几到十几分钟延迟，不是秒级实时。
