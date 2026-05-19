# Run after first successful admin login — disables auto user creation

param(
    [string]$ComposeDir = "C:\dimkava\compose"
)

$ErrorActionPreference = "Stop"
$envFile = Join-Path $ComposeDir ".env.prod"

if (-not (Test-Path $envFile)) {
    throw ".env.prod not found at $envFile"
}

$content = Get-Content $envFile -Raw
$content = $content -replace 'AUTO_CREATE_DEFAULT_USERS=1', 'AUTO_CREATE_DEFAULT_USERS=0'
$content = $content -replace 'AUTO_SEED_DEMO_CONTENT=1', 'AUTO_SEED_DEMO_CONTENT=0'
Set-Content -Path $envFile -Value $content.TrimEnd() -NoNewline
Add-Content -Path $envFile -Value ""

Write-Host "Set AUTO_CREATE_DEFAULT_USERS=0 and AUTO_SEED_DEMO_CONTENT=0 in .env.prod"

Set-Location $ComposeDir
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d web

Write-Host "Web container restarted. Verify login still works." -ForegroundColor Green
