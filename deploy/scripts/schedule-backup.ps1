# Register a daily Windows Task Scheduler job for backup-db.ps1
# Run once as Administrator: C:\dimkava\scripts\schedule-backup.ps1

param(
    [string]$ScriptsDir = "C:\dimkava\scripts",
    [string]$TaskName = "DimKava-DB-Backup",
    [string]$TimeOfDay = "02:30"
)

$ErrorActionPreference = "Stop"
$backupScript = Join-Path $ScriptsDir "backup-db.ps1"
if (-not (Test-Path $backupScript)) {
    throw "Missing $backupScript — run copy-to-server.ps1 first"
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$backupScript`""
$trigger = New-ScheduledTaskTrigger -Daily -At $TimeOfDay
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $settings -Principal $principal -Force | Out-Null

Write-Host "Scheduled task '$TaskName' daily at $TimeOfDay -> $backupScript" -ForegroundColor Green
Write-Host "Verify: Get-ScheduledTask -TaskName $TaskName"
