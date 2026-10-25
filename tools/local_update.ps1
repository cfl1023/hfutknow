# 工大知道 · 本机 5 分钟增量更新（计划任务调用）
# 仅在电脑开机并登录时运行；无新数据时不产生提交。

$ErrorActionPreference = 'Continue'
$repo = 'C:\Users\lenovo\Documents\deepseek-harness\default-workspace\campusknow'
$py = 'C:\Users\lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
$logDir = Join-Path $repo 'logs'
$log = Join-Path $logDir 'local_update.log'
$lock = Join-Path $repo '.local_update.lock'

New-Item -ItemType Directory -Path $logDir -Force | Out-Null

# 防止重入：上一次还在跑就跳过
if (Test-Path $lock) {
    $age = (Get-Date) - (Get-Item $lock).LastWriteTime
    if ($age.TotalMinutes -lt 8) { exit 0 }
}
Set-Content -Path $lock -Value (Get-Date -Format o) -Encoding UTF8

function Log($msg) {
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $msg" | Add-Content -Path $log -Encoding UTF8
}

try {
    Set-Location $repo

    & $py -m pipeline.sync --limit 24 --fast *>> $log
    & $py tools/make_rss.py *>> $log
    & $py tools/clean_junk.py *>> $log
    & $py tools/build_tracking.py *>> $log
    & $py tools/build_standalone.py *>> $log

    if (Test-Path (Join-Path $repo 'dist\工大知道.html')) {
        Copy-Item (Join-Path $repo 'dist\工大知道.html') 'C:\Users\lenovo\Documents\deepseek-harness\default-workspace\工大知道.html' -Force
    }

    git add -A 2>&1 | Out-Null
    $dirty = git status --porcelain
    if (-not $dirty) { Log '无数据变化，跳过提交'; return }

    $stamp = Get-Date -Format 'yyyy-MM-ddTHH:mm'
    git -c user.name='hfutknow-local' -c user.email='local@users.noreply.github.com' commit -m "data: local $stamp" 2>&1 | Add-Content -Path $log -Encoding UTF8

    # 远端可能被 GitHub Actions bot 抢先提交：最多重试 3 轮
    $ok = $false
    for ($i = 1; $i -le 3; $i++) {
        git pull --rebase --autostash origin main 2>&1 | Add-Content -Path $log -Encoding UTF8
        $push = git push origin main 2>&1
        $push | Add-Content -Path $log -Encoding UTF8
        if ($LASTEXITCODE -eq 0) { $ok = $true; break }
        Log "push 第 $i 次失败，5 秒后重试"
        Start-Sleep -Seconds 5
    }
    if ($ok) { Log 'push 成功' } else { Log 'push 连续失败，等下一轮' }
}
catch {
    Log ("ERROR: " + $_.Exception.Message)
}
finally {
    Remove-Item $lock -Force -ErrorAction SilentlyContinue
    Log '--- done ---'
}
