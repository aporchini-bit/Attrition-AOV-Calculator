@echo off
setlocal
cd /d "%~dp0"

set PY=python-embed\python.exe

if not exist "%PY%" (
  echo.
  echo  ============================================================
  echo   Setup needed (one time only):
  echo   The python-embed folder is missing or incomplete.
  echo   See SETUP.md in this folder for the one-time download step.
  echo  ============================================================
  echo.
  pause
  exit /b 1
)

echo Starting ROPS Attrition ^& AOV Calculator...
echo (Leave this window open while you use the tool. Close it when done.)
echo.

start "" /min cmd /c "timeout /t 2 >nul && start http://localhost:8766"
"%PY%" ..\rops-calculator-server.py

pause
