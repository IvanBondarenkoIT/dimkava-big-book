# Create C:\dimkava\compose\.env.prod with empty values (fill on server only; never commit .env.prod)
param(
    [string]$ComposeDir = "C:\dimkava\compose",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$envPath = Join-Path $ComposeDir ".env.prod"

if ((Test-Path $envPath) -and -not $Force) {
    Write-Host ".env.prod already exists: $envPath" -ForegroundColor Yellow
    Write-Host "Use -Force to overwrite or edit the file manually."
    return
}

New-Item -ItemType Directory -Path $ComposeDir -Force | Out-Null

$content = @'
# Dim Kava production — fill all empty values on the server. Do not commit this file.

POSTGRES_DB=dimkava
POSTGRES_USER=dimkava
POSTGRES_PASSWORD=
POSTGRES_HOST=db
POSTGRES_PORT=5432

DIMKAVA_IMAGE=ghcr.io/ivanbondarenkoit/dimkava-big-book:latest

SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

DATABASE_SSL_REQUIRE=false
SECURE_SSL_REDIRECT=false
SESSION_COOKIE_SECURE=false
CSRF_COOKIE_SECURE=false

GUNICORN_WORKERS=3
GUNICORN_TIMEOUT=60
PORT=8000

AUTO_CREATE_DEFAULT_USERS=1
AUTO_SEED_DEMO_CONTENT=1
AUTO_LOAD_HR_CONTENT=1

DEFAULT_ADMIN_EMAIL=admin@dimkava.ge
DEFAULT_ADMIN_PASSWORD=

DEFAULT_HR_EMAIL=hr@dimkava.ge
DEFAULT_HR_PASSWORD=

DEFAULT_EMPLOYEE_EMAIL=employee@dimkava.ge
DEFAULT_EMPLOYEE_PASSWORD=

DEFAULT_CANDIDATE_EMAIL=candidate@dimkava.ge
DEFAULT_CANDIDATE_PASSWORD=
DEFAULT_CANDIDATE_PHONE=+995500000000

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=Dim Kava <noreply@dimkava.ge>
'@

Set-Content -Path $envPath -Value $content.TrimEnd() -Encoding utf8
Write-Host "Created $envPath — fill POSTGRES_PASSWORD, SECRET_KEY, and DEFAULT_* passwords before deploy." -ForegroundColor Green
