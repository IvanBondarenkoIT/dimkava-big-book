@echo off
REM One-click Dim Kava update (git pull + build + recreate web)
REM Do NOT use "Run as administrator" — run as the user who owns C:\Projects\dimkava-big-book

cd /d "%~dp0"

net session >nul 2>&1
if %errorLevel%==0 (
  echo.
  echo WARNING: This window looks elevated ^(Administrator^).
  echo If git fails with FETCH_HEAD Permission denied, close this and
  echo double-click the .bat again WITHOUT "Run as administrator".
  echo.
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update-from-git.ps1" %*
if errorlevel 1 (
  echo.
  echo UPDATE FAILED.
  pause
  exit /b 1
)
echo.
pause
