# Dim Kava - check GitHub deploy prerequisites on this machine (read-only checks)
param(
    [string]$ComposeDir = "C:\dimkava\compose"
)

$ErrorActionPreference = "Continue"
$ok = $true

Write-Host "=== Dim Kava deploy setup check ===" -ForegroundColor Cyan
Write-Host ""

# Docker CLI
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[FAIL] docker not in PATH. Install Docker Desktop and restart PowerShell." -ForegroundColor Red
    $ok = $false
} else {
    Write-Host "[OK] docker CLI found" -ForegroundColor Green
    $info = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Docker Engine not running. Open Docker Desktop, wait for 'Engine running'." -ForegroundColor Red
        $ok = $false
    } else {
        Write-Host "[OK] Docker Engine running" -ForegroundColor Green
    }
}

# Compose files
$required = @(
    (Join-Path $ComposeDir "docker-compose.prod.yml"),
    (Join-Path $ComposeDir "deploy\Caddyfile"),
    (Join-Path $ComposeDir ".env.prod")
)
foreach ($path in $required) {
    if (Test-Path $path) {
        Write-Host "[OK] $path" -ForegroundColor Green
    } else {
        Write-Host "[MISSING] $path" -ForegroundColor Yellow
        if ($path -like "*.env.prod") {
            Write-Host "       Run: C:\dimkava\scripts\new-env-prod.ps1" -ForegroundColor Yellow
        } elseif ($path -like "*docker-compose*") {
            Write-Host "       Run: .\deploy\scripts\copy-to-server.ps1" -ForegroundColor Yellow
        }
        $ok = $false
    }
}

Write-Host ""
Write-Host "GitHub (check manually in browser):" -ForegroundColor Cyan
Write-Host "  Actions: https://github.com/IvanBondarenkoIT/dimkava-big-book/actions"
Write-Host "  Workflow 'Docker publish (GHCR)' must be green before docker pull"
Write-Host "  Image: ghcr.io/ivanbondarenkoit/dimkava-big-book:latest"
Write-Host ""
Write-Host "Docs: docs/GITHUB_AND_DOCKER.md | docs/WINDOWS_SERVER_DEPLOY.md"
Write-Host ""

if ($ok) {
    Write-Host "Local checks passed. Next: docker login ghcr.io && first-deploy.ps1" -ForegroundColor Green
} else {
    Write-Host "Fix items above, then re-run this script." -ForegroundColor Yellow
}

exit $(if ($ok) { 0 } else { 1 })
