# Copy deployment bundle from git clone to C:\dimkava\compose
# Run from repo root: .\deploy\scripts\copy-to-server.ps1

param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$TargetDir = "C:\dimkava\compose",
    [string]$ScriptsDir = "C:\dimkava\scripts"
)

$ErrorActionPreference = "Stop"

$files = @(
    "docker-compose.prod.yml",
    "deploy\Caddyfile",
    "deploy\Caddyfile.https.example"
)

New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $TargetDir "deploy") -Force | Out-Null
New-Item -ItemType Directory -Path $ScriptsDir -Force | Out-Null
New-Item -ItemType Directory -Path "C:\dimkava\backups" -Force | Out-Null

foreach ($rel in $files) {
    $src = Join-Path $RepoRoot $rel
    if (-not (Test-Path $src)) {
        throw "Missing in repo: $src. Run: git checkout deploy/self-hosted -- $rel"
    }
    $dest = Join-Path $TargetDir $rel
    $destParent = Split-Path $dest -Parent
    if (-not (Test-Path $destParent)) {
        New-Item -ItemType Directory -Path $destParent -Force | Out-Null
    }
    Copy-Item $src $dest -Force
    Write-Host "Copied $rel"
}

$scriptSources = Get-ChildItem (Join-Path $RepoRoot "deploy\scripts\*.ps1")
foreach ($s in $scriptSources) {
    Copy-Item $s.FullName (Join-Path $ScriptsDir $s.Name) -Force
    Write-Host "Copied script: $($s.Name)"
}

Write-Host ""
Write-Host "Done. Next commands:" -ForegroundColor Green
Write-Host "  notepad C:\dimkava\compose\.env.prod"
Write-Host "  .\deploy\scripts\configure-public-access.ps1 -PublicHost ge.domkofe.biz -PublicPort 777 -NatVariant B"
Write-Host "  .\deploy\scripts\verify-setup.ps1"
Write-Host "  .\deploy\scripts\verify-public-access.ps1 -PublicHost ge.domkofe.biz -PublicPort 777"
Write-Host "  docker login ghcr.io"
Write-Host "  .\deploy\scripts\first-deploy.ps1"
