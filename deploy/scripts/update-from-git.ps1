# Dim Kava self-hosted: git pull + local image build + recreate web
# Usage (from anywhere):
#   powershell -ExecutionPolicy Bypass -File C:\Projects\dimkava-big-book\deploy\scripts\update-from-git.ps1
# Or double-click: update-from-git.bat (same folder)
#
# Do NOT "Run as administrator" if the repo was cloned by a normal user —
# that causes: cannot open '.git/FETCH_HEAD': Permission denied

param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$ComposeDir = "C:\dimkava\compose",
    [string]$ImageTag = "dimkava-local:latest",
    [switch]$SkipPull
)

$ErrorActionPreference = "Stop"

function Test-IsAdmin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Write-GitPermissionHelp {
    Write-Host ""
    Write-Host "Git permission denied on .git (FETCH_HEAD)." -ForegroundColor Red
    Write-Host "Usual cause: script runs as Administrator, repo owned by a normal user." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Fix:" -ForegroundColor Cyan
    Write-Host "  1. Close this window."
    Write-Host "  2. Open PowerShell as the SAME user who owns C:\Projects\dimkava-big-book"
    Write-Host "     (do NOT right-click Run as administrator)."
    Write-Host "  3. Run:"
    Write-Host "       cd C:\Projects\dimkava-big-book"
    Write-Host "       git pull"
    Write-Host "       .\deploy\scripts\update-from-git.ps1"
    Write-Host ""
    Write-Host "  Or double-click update-from-git.bat without elevation."
    Write-Host "  If still failing: close Cursor/Git GUI locking the folder, then retry."
}

Write-Host "=== Dim Kava update (git + local image) ===" -ForegroundColor Cyan
Write-Host "Repo:    $RepoRoot"
Write-Host "Compose: $ComposeDir"
Write-Host "User:    $env:USERNAME  (admin=$(Test-IsAdmin))"
Write-Host ""

if (-not (Test-Path $RepoRoot)) {
    throw "Repo not found: $RepoRoot"
}
if (-not (Test-Path (Join-Path $ComposeDir ".env.prod"))) {
    throw "Missing .env.prod in $ComposeDir"
}

if ((Test-IsAdmin)) {
    Write-Host "WARNING: Running elevated (Administrator)." -ForegroundColor Yellow
    Write-Host "If git pull fails with FETCH_HEAD Permission denied, re-run WITHOUT elevation." -ForegroundColor Yellow
    Write-Host ""
}

Set-Location $RepoRoot

# Quick writable check on .git
$fetchHead = Join-Path $RepoRoot ".git\FETCH_HEAD"
$gitDir = Join-Path $RepoRoot ".git"
try {
    $probe = Join-Path $gitDir ("_write_probe_{0}.tmp" -f [guid]::NewGuid().ToString("N"))
    [IO.File]::WriteAllText($probe, "ok")
    Remove-Item -Force $probe
} catch {
    Write-GitPermissionHelp
    throw "Cannot write to .git (Permission denied). $($_.Exception.Message)"
}

if (-not $SkipPull) {
    Write-Host ">>> git pull" -ForegroundColor Yellow
    git pull 2>&1 | ForEach-Object { $_ }
    if ($LASTEXITCODE -ne 0) {
        if (Test-Path $fetchHead) {
            # still may be ACL issue on update
        }
        Write-GitPermissionHelp
        throw "git pull failed (exit $LASTEXITCODE)"
    }
} else {
    Write-Host ">>> skip git pull" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host ">>> build local image ($ImageTag)" -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "build-local-image.ps1") -RepoRoot $RepoRoot -ImageTag $ImageTag
if ($LASTEXITCODE -ne 0) { throw "build-local-image failed (exit $LASTEXITCODE)" }

Write-Host ""
Write-Host ">>> recreate web" -ForegroundColor Yellow
Set-Location $ComposeDir
$dc = "docker compose --env-file .env.prod -f docker-compose.prod.yml"
Invoke-Expression "$dc up -d --force-recreate web"
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed (exit $LASTEXITCODE)" }

Write-Host ""
Invoke-Expression "$dc ps"
Write-Host ""
Write-Host "Update complete. Hard-refresh the site (Ctrl+F5)." -ForegroundColor Green
