# 工大知道 · 本机 5 分钟增量更新（计划任务调用）
# 只在电脑开机并登录时运行；无数据变化时不产生提交。

$ErrorActionPreference = 'Continue'
$repo = 'C:\Users\lenovo\Documents\deepseek-harness\default-workspace\campusknow'
$py = 'C:\Users\lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
$logDir = Join-Path $env:LOCALAPPDATA 'HFUTKnow'
$log = Join-Path $logDir 'local_update.log'
$lock = Join-Path $logDir 'local_update.lock'

New-Item -ItemType Directory -Path $logDir -Force | Out-Null

function Log($msg) {
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $msg" | Add-Content -Path $log -Encoding UTF8
}

# 防止重入：上一次还在跑就跳过
if (Test-Path $lock) {
    $age = (Get-Date) - (Get-Item $lock).LastWriteTime
    if ($age.TotalMinutes -lt 8) { exit 0 }
}
Set-Content -Path $lock -Value (Get-Date -Format o) -Encoding UTF8

try {
    Set-Location $repo
    Log '--- start ---'

    & $py -m pipeline.sync --limit 24 --fast *>> $log
    & $py tools/ingest_corpus.py *>> $log
    & $py tools/make_rss.py *>> $log
    & $py tools/clean_junk.py *>> $log
    & $py tools/build_tracking.py *>> $log
    & $py tools/build_standalone.py *>> $log

    if (Test-Path (Join-Path $repo 'dist\工大知道.html')) {
        Copy-Item (Join-Path $repo 'dist\工大知道.html') 'C:\Users\lenovo\Documents\deepseek-harness\default-workspace\工大知道.html' -Force
    }

    git add -A 2>&1 | Out-Null
    $dirty = git status --porcelain
    if (-not $dirty) { Log 'no data change'; return }

    $stamp = Get-Date -Format 'yyyy-MM-ddTHH:mm'
    git -c user.name='hfutknow-local' -c user.email='local@users.noreply.github.com' commit -m "data: local $stamp" 2>&1 | Add-Content -Path $log -Encoding UTF8

    # 先对齐远端，再把工作区变更整体叠到远端 tip 之上，永不产生 rebase 冲突
    git fetch origin main 2>&1 | Add-Content -Path $log -Encoding UTF8
    if (Test-Path (Join-Path $repo '.git\rebase-merge')) { git rebase --abort 2>&1 | Out-Null }
    if (Test-Path (Join-Path $repo '.git\rebase-apply')) { git rebase --abort 2>&1 | Out-Null }
    git reset --soft origin/main 2>&1 | Add-Content -Path $log -Encoding UTF8
    git add -A 2>&1 | Out-Null
    $dirty2 = git status --porcelain
    if (-not $dirty2) { Log 'no data change'; return }
    git -c user.name='hfutknow-local' -c user.email='local@users.noreply.github.com' commit -m "data: local $stamp" 2>&1 | Add-Content -Path $log -Encoding UTF8

    $ok = $false
    for ($i = 1; $i -le 3; $i++) {
        $push = git push origin main 2>&1
        $push | Add-Content -Path $log -Encoding UTF8
        if ($LASTEXITCODE -eq 0) { $ok = $true; break }
        Log "push retry $i"
        Start-Sleep -Seconds 5
        git fetch origin main 2>&1 | Out-Null
        git reset --soft origin/main 2>&1 | Out-Null
        git add -A 2>&1 | Out-Null
        git -c user.name='hfutknow-local' -c user.email='local@users.noreply.github.com' commit -m "data: local $stamp retry$i" 2>&1 | Add-Content -Path $log -Encoding UTF8
    }
    if ($ok) { Log 'push ok' } else { Log 'push failed, next round' }
}
catch {
    Log ("ERROR: " + $_.Exception.Message)
}
finally {
    Remove-Item $lock -Force -ErrorAction SilentlyContinue
    Log '--- done ---'
}
