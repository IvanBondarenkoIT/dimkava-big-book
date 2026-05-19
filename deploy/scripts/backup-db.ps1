# Dim Kava — PostgreSQL backup to C:\dimkava\backups
# Schedule via Task Scheduler (daily recommended).

param(
    [string]$ComposeDir = "C:\dimkava\compose",
    [string]$BackupDir = "C:\dimkava\backups",
    [int]$KeepDays = 14
)

$ErrorActionPreference = "Stop"
Set-Location $ComposeDir

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outFile = Join-Path $BackupDir "dimkava-$timestamp.sql"

Write-Host "Backing up to $outFile ..."

docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db pg_dump -U dimkava dimkava | Set-Content -Path $outFile -Encoding utf8

if ($LASTEXITCODE -ne 0) {
    throw "pg_dump failed"
}

Write-Host "Backup OK: $outFile"

Get-ChildItem $BackupDir -Filter "dimkava-*.sql" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$KeepDays) } |
    Remove-Item -Force

Write-Host "Removed backups older than $KeepDays days."
