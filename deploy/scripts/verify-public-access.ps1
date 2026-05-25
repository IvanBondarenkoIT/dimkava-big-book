# Verify Dim Kava responds locally after public-access configuration.
param(
    [string]$PublicIp = "178.63.72.227",
    [int]$PublicPort = 777,
    [int]$HostPort = 777,
    [string]$ComposeDir = "C:\dimkava\compose"
)

$ErrorActionPreference = "Continue"
$ok = $true

Write-Host "=== Dim Kava public access check ===" -ForegroundColor Cyan
Write-Host "Expected public URL: http://${PublicIp}:${PublicPort}/"
Write-Host "Local probe port (host): $HostPort"
Write-Host ""

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[FAIL] docker not in PATH" -ForegroundColor Red
    exit 1
}

Set-Location $ComposeDir
$psOut = docker compose --env-file .env.prod -f docker-compose.prod.yml ps 2>&1
Write-Host $psOut
if ($psOut -notmatch "proxy") {
    Write-Host "[FAIL] proxy container not running" -ForegroundColor Red
    $ok = $false
}

function Test-HttpCode {
    param([string]$Url)
    try {
        $code = curl.exe -s -o NUL -w "%{http_code}" --connect-timeout 5 $Url 2>$null
        return $code
    } catch {
        return "000"
    }
}

$urls = @(
    @{ Label = "localhost:80"; Url = "http://127.0.0.1/login/" },
    @{ Label = "localhost:HostPort"; Url = "http://127.0.0.1:${HostPort}/login/" }
)
foreach ($u in $urls) {
    $code = Test-HttpCode -Url $u.Url
    if ($code -match "^(200|302)$") {
        Write-Host "[OK] $($u.Label) -> HTTP $code ($($u.Url))" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $($u.Label) -> HTTP $code ($($u.Url))" -ForegroundColor Red
        $ok = $false
    }
}

Write-Host ""
Write-Host "Recent web logs (DisallowedHost / CSRF):" -ForegroundColor Cyan
docker compose --env-file .env.prod -f docker-compose.prod.yml logs web --tail 20 2>&1 | Select-String -Pattern "DisallowedHost|CSRF|Forbidden" -SimpleMatch
if ($LASTEXITCODE -ne 0) {
    Write-Host "(no matching errors in last 20 lines, or log fetch failed)"
}

Write-Host ""
Write-Host "From phone (not office Wi-Fi): http://${PublicIp}:${PublicPort}/" -ForegroundColor Cyan
Write-Host "If local OK but public fails: check NAT (see deploy/docs/PUBLIC_ACCESS_NAT.md) and try -NatVariant A vs B"
Write-Host ""

if ($ok) {
    Write-Host "Local checks passed." -ForegroundColor Green
    exit 0
}
Write-Host "Fix failures above, then re-run." -ForegroundColor Yellow
exit 1
