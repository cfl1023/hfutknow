# 注册本机定时任务：每 5 分钟抓一次（只在开机登录时跑）
# 用法：powershell -ExecutionPolicy Bypass -File tools\install-task.ps1
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$script = Join-Path $root 'tools\local_update.ps1'
if (-not (Test-Path $script)) { throw "找不到 $script" }

$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`"" `
    -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

Register-ScheduledTask -TaskName 'HFUTKnowLocal' -Action $action -Trigger $trigger `
    -Settings $settings -Description '工大知道：每 5 分钟抓取校园信息并推送' -Force | Out-Null

Write-Host '已注册 HFUTKnowLocal：每 5 分钟一次（电脑开机登录时才跑）'
Write-Host '立即试跑：Start-ScheduledTask -TaskName HFUTKnowLocal'
Write-Host '删除任务：Unregister-ScheduledTask -TaskName HFUTKnowLocal -Confirm:$false'
