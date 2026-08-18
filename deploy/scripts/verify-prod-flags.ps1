# Verify production safety flags in C:\dimkava\compose\.env.prod
# Run on the server: C:\dimkava\scripts\verify-prod-flags.ps1

param(
    [string]$ComposeDir = "C:\dimkava\compose"
)

$ErrorActionPreference = "Stop"
$envFile = Join-Path $ComposeDir ".env.prod"

if (-not (Test-Path $envFile)) {
    throw ".env.prod not found at $envFile"
}

Write-Host "Checking $envFile" -ForegroundColor Cyan
$raw = Get-Content $envFile -Raw
$lines = Get-Content $envFile

function Get-EnvValue([string]$key) {
    foreach ($line in $lines) {
        if ($line -match "^\s*$key\s*=\s*(.*)$") {
            return $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
    return $null
}

$ok = $true

$load = Get-EnvValue "AUTO_LOAD_HR_CONTENT"
$users = Get-EnvValue "AUTO_CREATE_DEFAULT_USERS"
$emailBackend = Get-EnvValue "EMAIL_BACKEND"
$pgPass = Get-EnvValue "POSTGRES_PASSWORD"

Write-Host "AUTO_LOAD_HR_CONTENT=$load"
if ($load -eq "1" -or $load -eq "true") {
    Write-Host "FAIL: AUTO_LOAD_HR_CONTENT must be 0 (overwrites HR quiz keys / portal edits)" -ForegroundColor Red
    $ok = $false
} else {
    Write-Host "OK: content auto-load disabled" -ForegroundColor Green
}

Write-Host "AUTO_CREATE_DEFAULT_USERS=$users"
if ($users -eq "1" -or $users -eq "true") {
    Write-Host "FAIL: AUTO_CREATE_DEFAULT_USERS must be 0 after first login (resets passwords)" -ForegroundColor Red
    $ok = $false
} else {
    Write-Host "OK: default user recreate disabled" -ForegroundColor Green
}

Write-Host "EMAIL_BACKEND=$emailBackend"
if (-not $emailBackend -or $emailBackend -match "console") {
    Write-Host "WARN: EMAIL_BACKEND is console — password reset / verify emails stay in container logs" -ForegroundColor Yellow
} else {
    Write-Host "OK: non-console email backend" -ForegroundColor Green
}

if ($pgPass -and $pgPass.Contains('$') -and -not $pgPass.Contains('$$')) {
    Write-Host "WARN: POSTGRES_PASSWORD contains `$ — escape as `$`$ in .env.prod for Compose" -ForegroundColor Yellow
} elseif ($pgPass) {
    Write-Host "OK: POSTGRES_PASSWORD looks Compose-safe (or has no `$)" -ForegroundColor Green
}

if ($ok) {
    Write-Host "Prod flags check passed." -ForegroundColor Green
    exit 0
}
Write-Host "Prod flags check failed." -ForegroundColor Red
exit 1
