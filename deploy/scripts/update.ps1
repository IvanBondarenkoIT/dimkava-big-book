# Dim Kava - pull latest image and restart (manual update or after GitHub Actions deploy)

param(
    [string]$ComposeDir = "C:\dimkava\compose"
)

$ErrorActionPreference = "Stop"
Set-Location $ComposeDir

$dc = "docker compose --env-file .env.prod -f docker-compose.prod.yml"

Write-Host "Pulling web image..."
Invoke-Expression "$dc pull web"

Write-Host "Recreating containers..."
Invoke-Expression "$dc up -d"

Invoke-Expression "$dc ps"
Invoke-Expression "$dc logs web --tail 40"

Write-Host "Update complete." -ForegroundColor Green
