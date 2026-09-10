# Dim Kava self-hosted: git pull + local image build + recreate web
# Usage (from anywhere):
#   powershell -ExecutionPolicy Bypass -File C:\Projects\dimkava-big-book\deploy\scripts\update-from-git.ps1
# Or double-click: update-from-git.bat (same folder)

param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$ComposeDir = "C:\dimkava\compose",
    [string]$ImageTag = "dimkava-local:latest",
    [switch]$SkipPull
)

$ErrorActionPreference = "Stop"

Write-Host "=== Dim Kava update (git + local image) ===" -ForegroundColor Cyan
Write-Host "Repo:    $RepoRoot"
Write-Host "Compose: $ComposeDir"
Write-Host ""

if (-not (Test-Path $RepoRoot)) {
    throw "Repo not found: $RepoRoot"
}
if (-not (Test-Path (Join-Path $ComposeDir ".env.prod"))) {
    throw "Missing .env.prod in $ComposeDir"
}

Set-Location $RepoRoot

if (-not $SkipPull) {
    Write-Host ">>> git pull" -ForegroundColor Yellow
    git pull
    if ($LASTEXITCODE -ne 0) { throw "git pull failed (exit $LASTEXITCODE)" }
} else {
    Write-Host ">>> skip git pull" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host ">>> build local image ($ImageTag)" -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "build-local-image.ps1") -RepoRoot $RepoRoot -ImageTag $ImageTag
if ($LASTEXITCODE -ne 0) { throw "build-local-image failed (exit $LASTEXITCODE)" }

Write-Host ""
Write-Host ">>> recreate web" -ForegroundColor Yellow
Set-Location $ComposeDir
$dc = "docker compose --env-file .env.prod -f docker-compose.prod.yml"
Invoke-Expression "$dc up -d --force-recreate web"
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed (exit $LASTEXITCODE)" }

Write-Host ""
Invoke-Expression "$dc ps"
Write-Host ""
Write-Host "Update complete. Hard-refresh the site (Ctrl+F5)." -ForegroundColor Green
