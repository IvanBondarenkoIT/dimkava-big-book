# Copy deployment bundle from git clone to C:\dimkava\compose

param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$TargetDir = "C:\dimkava\compose"
)

$ErrorActionPreference = "Stop"

$files = @(
    "docker-compose.prod.yml",
    "deploy\Caddyfile",
    "deploy\Caddyfile.https.example"
)

New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $TargetDir "deploy") -Force | Out-Null
New-Item -ItemType Directory -Path "C:\dimkava\scripts" -Force | Out-Null
New-Item -ItemType Directory -Path "C:\dimkava\backups" -Force | Out-Null

foreach ($rel in $files) {
    $src = Join-Path $RepoRoot $rel
    $dest = Join-Path $TargetDir $rel
    $destParent = Split-Path $dest -Parent
    if (-not (Test-Path $destParent)) {
        New-Item -ItemType Directory -Path $destParent -Force | Out-Null
    }
    Copy-Item $src $dest -Force
    Write-Host "Copied $rel"
}

Copy-Item (Join-Path $RepoRoot "deploy\scripts\*.ps1") "C:\dimkava\scripts\" -Force
Write-Host "Next: C:\dimkava\scripts\new-env-prod.ps1"
