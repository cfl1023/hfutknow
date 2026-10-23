# 注册本机定时任务：每 30 分钟更新一次数据
# 用法：powershell -ExecutionPolicy Bypass -File tools\install-task.ps1
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$bat = Join-Path $root "update.bat"
if (-not (Test-Path $bat)) { throw "找不到 update.bat：$bat" }

$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$bat`"" -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) `
    -RepetitionInterval (New-TimeSpan -Minutes 30)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "HFUTKnowUpdate" -Action $action -Trigger $trigger `
    -Settings $settings -Description "工大知道：每 30 分钟抓取校园信息源" -Force | Out-Null

Write-Host "已注册任务 HFUTKnowUpdate，每 30 分钟运行一次。"
Write-Host "立即试跑：Start-ScheduledTask -TaskName HFUTKnowUpdate"
Write-Host "删除任务：Unregister-ScheduledTask -TaskName HFUTKnowUpdate -Confirm:`$false"
