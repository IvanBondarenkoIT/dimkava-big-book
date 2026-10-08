# Configure production for https://bigbook.dimkava.ge/
# Run on the Windows Server (Admin PowerShell recommended for firewall).
#
# Prerequisites:
#   - DNS A: bigbook.dimkava.ge -> this server public IP
#   - NAT: WAN :80 -> host :80, WAN :443 -> host :443
#   - Docker stack already running under C:\dimkava\compose
#
# Usage:
#   .\configure-bigbook-https.ps1
#   .\configure-bigbook-https.ps1 -HttpOnly   # ALLOWED_HOSTS/CSRF for HTTP first
#   .\configure-bigbook-https.ps1 -KeepLegacyHost  # also allow ge.domkofe.biz:777

param(
    [string]$PublicHost = "bigbook.dimkava.ge",
    [string]$PublicIp = "178.63.72.227",
    [string]$ComposeDir = "C:\dimkava\compose",
    [string]$RepoCaddyfile = "",
    [switch]$HttpOnly,
    [switch]$KeepLegacyHost,
    [switch]$SkipFirewall,
    [switch]$SkipComposeUp
)

$ErrorActionPreference = "Stop"
$envFile = Join-Path $ComposeDir ".env.prod"
$composeFile = Join-Path $ComposeDir "docker-compose.prod.yml"
$caddyDest = Join-Path $ComposeDir "deploy\Caddyfile"

if (-not (Test-Path $envFile)) {
    throw ".env.prod not found at $envFile"
}
if (-not (Test-Path $composeFile)) {
    throw "docker-compose.prod.yml not found at $composeFile"
}

if (-not $RepoCaddyfile) {
    $candidates = @(
        "C:\Projects\dimkava-big-book\deploy\Caddyfile",
        (Join-Path $PSScriptRoot "..\Caddyfile")
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { $RepoCaddyfile = $c; break }
    }
}
if (-not $RepoCaddyfile -or -not (Test-Path $RepoCaddyfile)) {
    throw "Caddyfile source not found. Pass -RepoCaddyfile path."
}

function Set-EnvLine {
    param([string]$Name, [string]$Value, [ref]$Text)
    if ($Text.Value -match "(?m)^$Name=") {
        $Text.Value = $Text.Value -replace "(?m)^$Name=.*$", "$Name=$Value"
    } else {
        $Text.Value = $Text.Value.TrimEnd() + "`n$Name=$Value`n"
    }
}

$allowed = @($PublicHost, "localhost", "127.0.0.1")
if ($PublicIp) { $allowed = @($PublicHost, $PublicIp) + @("localhost", "127.0.0.1") }
if ($KeepLegacyHost) { $allowed = @($PublicHost, "ge.domkofe.biz", $PublicIp, "localhost", "127.0.0.1") | Select-Object -Unique }

if ($HttpOnly) {
    $csrf = @("http://${PublicHost}", "http://localhost", "http://127.0.0.1")
    if ($KeepLegacyHost) { $csrf = @("http://${PublicHost}", "http://ge.domkofe.biz:777") + $csrf | Select-Object -Unique }
    $sslRedirect = "false"
    $cookieSecure = "false"
    $publicUrl = "http://${PublicHost}/"
} else {
    # Both schemes: browsers/proxies sometimes send Origin: http://… even on HTTPS pages.
    $csrf = @(
        "https://${PublicHost}",
        "http://${PublicHost}",
        "http://localhost",
        "http://127.0.0.1"
    )
    if ($KeepLegacyHost) {
        $csrf = @("https://${PublicHost}", "http://${PublicHost}", "http://ge.domkofe.biz:777") + $csrf |
            Select-Object -Unique
    }
    $sslRedirect = "true"
    $cookieSecure = "true"
    $publicUrl = "https://${PublicHost}/"
}

$allowedHosts = ($allowed -join ",")
$csrfOrigins = ($csrf -join ",")

$content = Get-Content $envFile -Raw
Set-EnvLine "ALLOWED_HOSTS" $allowedHosts ([ref]$content)
Set-EnvLine "CSRF_TRUSTED_ORIGINS" $csrfOrigins ([ref]$content)
Set-EnvLine "SECURE_SSL_REDIRECT" $sslRedirect ([ref]$content)
Set-EnvLine "SESSION_COOKIE_SECURE" $cookieSecure ([ref]$content)
Set-EnvLine "CSRF_COOKIE_SECURE" $cookieSecure ([ref]$content)
Set-EnvLine "PUBLIC_HTTP_PORT" "80" ([ref]$content)

Set-Content -Path $envFile -Value $content.TrimEnd() -Encoding utf8
Add-Content -Path $envFile -Value ""

$caddyDir = Split-Path $caddyDest -Parent
if (-not (Test-Path $caddyDir)) {
    New-Item -ItemType Directory -Path $caddyDir -Force | Out-Null
}

if ($HttpOnly) {
    $httpExample = Join-Path (Split-Path $RepoCaddyfile -Parent) "Caddyfile.http.example"
    if (Test-Path $httpExample) {
        Copy-Item $httpExample $caddyDest -Force
    } else {
        Copy-Item $RepoCaddyfile $caddyDest -Force
    }
    Write-Host "Caddyfile: HTTP :80 (HttpOnly)" -ForegroundColor Yellow
} else {
    Copy-Item $RepoCaddyfile $caddyDest -Force
    Write-Host "Caddyfile: HTTPS $PublicHost (from $RepoCaddyfile)" -ForegroundColor Green
}

Write-Host "Updated $envFile" -ForegroundColor Green
Write-Host "  ALLOWED_HOSTS=$allowedHosts"
Write-Host "  CSRF_TRUSTED_ORIGINS=$csrfOrigins"
Write-Host "  SECURE_SSL_REDIRECT=$sslRedirect"
Write-Host "  PUBLIC_HTTP_PORT=80"
Write-Host "  Public URL: $publicUrl"
Write-Host ""
Write-Host "Confirm with network admin:" -ForegroundColor Cyan
Write-Host "  DNS A $PublicHost -> $PublicIp"
Write-Host "  NAT WAN :80 -> host :80, WAN :443 -> host :443"

if (-not $SkipFirewall) {
    foreach ($port in @(80, 443)) {
        $ruleName = "DimKava TCP $port"
        $existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
        if ($existing) {
            Write-Host "Firewall rule already exists: $ruleName" -ForegroundColor Yellow
        } else {
            try {
                New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow | Out-Null
                Write-Host "Created firewall rule: $ruleName" -ForegroundColor Green
            } catch {
                Write-Host "Could not create firewall rule $ruleName (run as Admin): $_" -ForegroundColor Yellow
            }
        }
    }
}

if (-not $SkipComposeUp) {
    Set-Location $ComposeDir
    docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --force-recreate web proxy
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose up failed"
    }
    Write-Host "web + proxy recreated." -ForegroundColor Green
    Write-Host "Proxy logs (ACME / errors):" -ForegroundColor Cyan
    docker compose --env-file .env.prod -f docker-compose.prod.yml logs proxy --tail 40
}

Write-Host ""
Write-Host "Smoke: open $publicUrl" -ForegroundColor Cyan
if (-not $HttpOnly) {
    Write-Host "If certificate fails: check DNS, NAT 80+443, firewall, then recreate proxy again."
}
