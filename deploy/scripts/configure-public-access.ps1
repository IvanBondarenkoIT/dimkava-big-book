# Configure .env.prod and firewall for public HTTP access (e.g. http://ge.domkofe.biz:777/)
# Run on the server after copy-to-server.ps1 and new-env-prod.ps1 (secrets filled).
#
# Examples:
#   .\configure-public-access.ps1 -PublicHost ge.domkofe.biz -PublicPort 777 -NatVariant B
#   .\configure-public-access.ps1 -PublicHost ge.domkofe.biz -PublicIp 178.63.72.227 -NatVariant B

param(
    [string]$PublicHost = "ge.domkofe.biz",
    [string]$PublicIp = "",
    [int]$PublicPort = 777,
    [ValidateSet("A", "B")]
    [string]$NatVariant = "B",
    [string]$ComposeDir = "C:\dimkava\compose",
    [switch]$SkipFirewall,
    [switch]$SkipComposeUp
)

$ErrorActionPreference = "Stop"
$envFile = Join-Path $ComposeDir ".env.prod"
$composeFile = Join-Path $ComposeDir "docker-compose.prod.yml"

if (-not (Test-Path $envFile)) {
    throw ".env.prod not found at $envFile. Run new-env-prod.ps1 first."
}
if (-not (Test-Path $composeFile)) {
    throw "docker-compose.prod.yml not found at $composeFile. Run copy-to-server.ps1 first."
}

$hostPort = if ($NatVariant -eq "B") { $PublicPort } else { 80 }
$csrfOrigin = "http://${PublicHost}:${PublicPort}"
$allowedHosts = @($PublicHost)
if ($PublicIp) { $allowedHosts += $PublicIp }
$allowedHosts += @("localhost", "127.0.0.1")
$allowedHosts = ($allowedHosts -join ",")
$csrfOrigins = "$csrfOrigin,http://localhost,http://127.0.0.1"
$publicUrl = "http://${PublicHost}:${PublicPort}/"

function Set-EnvLine {
    param([string]$Name, [string]$Value, [ref]$Text)
    if ($Text.Value -match "(?m)^$Name=") {
        $Text.Value = $Text.Value -replace "(?m)^$Name=.*$", "$Name=$Value"
    } else {
        $Text.Value = $Text.Value.TrimEnd() + "`n$Name=$Value`n"
    }
}

$content = Get-Content $envFile -Raw
Set-EnvLine "ALLOWED_HOSTS" $allowedHosts ([ref]$content)
Set-EnvLine "CSRF_TRUSTED_ORIGINS" $csrfOrigins ([ref]$content)
Set-EnvLine "SECURE_SSL_REDIRECT" "false" ([ref]$content)
Set-EnvLine "SESSION_COOKIE_SECURE" "false" ([ref]$content)
Set-EnvLine "CSRF_COOKIE_SECURE" "false" ([ref]$content)
Set-EnvLine "PUBLIC_HTTP_PORT" "$hostPort" ([ref]$content)

Set-Content -Path $envFile -Value $content.TrimEnd() -Encoding utf8
Add-Content -Path $envFile -Value ""

Write-Host "Updated $envFile" -ForegroundColor Green
Write-Host "  NAT variant: $NatVariant (host listens on TCP $hostPort, users open :$PublicPort)"
Write-Host "  ALLOWED_HOSTS=$allowedHosts"
Write-Host "  CSRF_TRUSTED_ORIGINS=$csrfOrigins"
Write-Host "  PUBLIC_HTTP_PORT=$hostPort"
Write-Host ""
Write-Host "Tell server admin:" -ForegroundColor Cyan
if ($NatVariant -eq "A") {
    Write-Host "  WAN :$PublicPort -> this server LAN IP, port 80"
} else {
    Write-Host "  WAN :$PublicPort -> this server LAN IP, port $PublicPort"
}
Write-Host "  Public URL: $publicUrl"
Write-Host "  See: deploy/docs/PUBLIC_ACCESS_NAT.md"
Write-Host ""

if (-not $SkipFirewall) {
    $ruleName = "DimKava HTTP $hostPort"
    $existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "Firewall rule already exists: $ruleName" -ForegroundColor Yellow
    } else {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort $hostPort -Protocol TCP -Action Allow | Out-Null
        Write-Host "Created firewall rule: $ruleName (TCP $hostPort)" -ForegroundColor Green
    }
}

if (-not $SkipComposeUp) {
    Set-Location $ComposeDir
    docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --force-recreate web
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose up -d failed"
    }
    Write-Host "Web container recreated (ALLOWED_HOSTS applied)." -ForegroundColor Green
}

Write-Host ""
Write-Host "Next: .\verify-public-access.ps1 -PublicHost $PublicHost -PublicPort $PublicPort -HostPort $hostPort"
