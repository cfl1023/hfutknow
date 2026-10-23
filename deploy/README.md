# 部署与自动更新

目标：**不用开电脑、手机随时能打开、每 30 分钟自动抓一次**。

## 方案 A：GitHub Actions + Pages（推荐）

整条链路在 GitHub 的机器上跑：定时抓取 → 提交数据 → 发布成网页。
你的电脑关机也不影响，手机用流量也能打开。

### 1. 建仓库

在 GitHub 新建一个 **public** 仓库，名字随意，例如 `hfutknow`。
Public 仓库用 Pages 免费，Actions 也不计费。

### 2. 推代码

在 `campusknow` 目录里执行（把 `你的用户名` 换成 GitHub 用户名）：

```bash
git remote add origin https://github.com/你的用户名/hfutknow.git
git branch -M main
git push -u origin main
```

### 3. 打开 Pages

仓库 → **Settings → Pages → Build and deployment → Source** 选 **GitHub Actions**。

### 4. 手动跑一次

仓库 → **Actions → update → Run workflow**。
第一次会安装依赖、抓 20 个官网、提交数据、发布，大约 2–4 分钟。

### 5. 手机上打开

```
https://你的用户名.github.io/hfutknow/
```

用 Safari / Chrome 打开后「添加到主屏幕」，就是一个全屏的 App，断网也能看缓存。

### 6. 改频率

`.github/workflows/update.yml` 里的 `cron: "*/30 * * * *"` 就是每 30 分钟。
想改成每小时：`0 * * * *`。GitHub 的定时任务有几分钟延迟，属正常。

### 如果 GitHub 访问慢

Pages 域名在国内偶尔不稳定。备选：

- **Cloudflare Pages**：新建项目 → 连接同一个仓库 → 框架预设选 None → 输出目录填 `site` → 构建命令留空。以后每次提交自动发布。
- 数据更新仍然由 GitHub Actions 负责，两者可以并存。

## 方案 B：本机定时任务（电脑开着时）

不想折腾 GitHub 的话，用 Windows 计划任务，每 30 分钟跑一次 `update.bat`：

```powershell
powershell -ExecutionPolicy Bypass -File tools\install-task.ps1
```

它会注册一个名为 `HFUTKnowUpdate` 的任务。删除：

```powershell
Unregister-ScheduledTask -TaskName HFUTKnowUpdate -Confirm:$false
```

缺点：电脑必须开机；而且手机要访问还得解决公网访问问题（同 Wi-Fi 或内网穿透）。

## 方案 C：单文件发手机（零配置）

把 `工大知道.html` 用微信「文件传输助手」发到手机，用浏览器打开即可。
内容是一个静态快照，更新需要重新发一次，适合临时看。

## 数据是怎么更新的

```
GitHub Actions (每 30 分钟)
  └─ python -m pipeline.sync --limit 15 --enrich
       ├─ 20 个官网：抓列表 → 打开正文 → 清洗 → 分类 → 摘要
       └─ 写入 site/data/items.json、sources.json
  └─ python tools/make_rss.py
  └─ git commit + push（数据变更）
  └─ 部署 site/ 到 GitHub Pages
```

抓取失败不会中断：单个来源报错就跳过，下次再试；正文里提示「仅允许校内地址访问」的会被丢弃。
