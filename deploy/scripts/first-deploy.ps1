# Dim Kava — first production deploy on Windows Server

param(
    [string]$ComposeDir = "C:\dimkava\compose"
)

$ErrorActionPreference = "Stop"
$scriptsDir = if (Test-Path "C:\dimkava\scripts\new-env-prod.ps1") { "C:\dimkava\scripts" } else { $PSScriptRoot }

Write-Host "Dim Kava — first deploy" -ForegroundColor Cyan
Write-Host "Working directory: $ComposeDir"

if (-not (Test-Path $ComposeDir)) {
    New-Item -ItemType Directory -Path $ComposeDir -Force | Out-Null
}

Set-Location $ComposeDir

if (-not (Test-Path ".env.prod")) {
    & (Join-Path $scriptsDir "new-env-prod.ps1") -ComposeDir $ComposeDir
    Write-Host "Edit .env.prod — set POSTGRES_PASSWORD, SECRET_KEY, DEFAULT_ADMIN_PASSWORD." -ForegroundColor Yellow
    notepad .env.prod
    Read-Host "Press Enter after saving .env.prod"
}

Write-Host "Logging in to GHCR..."
docker login ghcr.io

$dc = "docker compose --env-file .env.prod -f docker-compose.prod.yml"
Invoke-Expression "$dc pull"
Invoke-Expression "$dc up -d"

Start-Sleep -Seconds 15
Invoke-Expression "$dc ps"
Invoke-Expression "$dc logs web --tail 80"

Write-Host "Open http://localhost/ then run post-first-login.ps1" -ForegroundColor Green
