# Build app image on this machine (when GHCR pull returns 403)
# Run from repo root: .\deploy\scripts\build-local-image.ps1

param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$ImageTag = "dimkava-local:latest"
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

Write-Host "Building Docker image locally (10-20 min first time)..." -ForegroundColor Cyan
docker build -t $ImageTag .

Write-Host ""
Write-Host "Set in C:\dimkava\compose\.env.prod:" -ForegroundColor Green
Write-Host "  DIMKAVA_IMAGE=$ImageTag"
Write-Host ""
Write-Host "Then: cd C:\dimkava\compose"
Write-Host "  docker compose --env-file .env.prod -f docker-compose.prod.yml up -d"
