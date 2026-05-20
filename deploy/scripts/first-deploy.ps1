# Dim Kava - first production deploy on Windows Server
# Run from repo: .\deploy\scripts\first-deploy.ps1

param(
    [string]$ComposeDir = "C:\dimkava\compose"
)

$ErrorActionPreference = "Stop"
$repoScripts = $PSScriptRoot
$scriptsDir = if (Test-Path "C:\dimkava\scripts\new-env-prod.ps1") { "C:\dimkava\scripts" } else { $repoScripts }

Write-Host "Dim Kava - first deploy" -ForegroundColor Cyan
Write-Host "Working directory: $ComposeDir"

if (-not (Test-Path $ComposeDir)) {
    New-Item -ItemType Directory -Path $ComposeDir -Force | Out-Null
}

Set-Location $ComposeDir

if (-not (Test-Path ".env.prod")) {
    $newEnv = Join-Path $scriptsDir "new-env-prod.ps1"
    if (-not (Test-Path $newEnv)) {
        throw "new-env-prod.ps1 not found. Run copy-to-server.ps1 from repo root first."
    }
    & $newEnv -ComposeDir $ComposeDir
    Write-Host "Edit .env.prod - set POSTGRES_PASSWORD, SECRET_KEY, DEFAULT_ADMIN_PASSWORD." -ForegroundColor Yellow
    notepad .env.prod
    Write-Host "Save .env.prod in Notepad, then press Enter here." -ForegroundColor Yellow
    Read-Host
}

if (-not (Test-Path "docker-compose.prod.yml")) {
    throw "docker-compose.prod.yml missing in $ComposeDir. Run copy-to-server.ps1"
}

Write-Host "Pulling images and starting stack..."
$dc = "docker compose --env-file .env.prod -f docker-compose.prod.yml"
Invoke-Expression "$dc pull"
Invoke-Expression "$dc up -d"

Start-Sleep -Seconds 15
Invoke-Expression "$dc ps"
Invoke-Expression "$dc logs web --tail 80"

Write-Host ""
Write-Host "Open http://localhost/ then run post-first-login.ps1" -ForegroundColor Green
