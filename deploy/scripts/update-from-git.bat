@echo off
REM One-click Dim Kava update on the Windows server (git pull + build + recreate web)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update-from-git.ps1" %*
if errorlevel 1 (
  echo.
  echo UPDATE FAILED.
  pause
  exit /b 1
)
echo.
pause
