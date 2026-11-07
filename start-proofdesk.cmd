@echo off
setlocal
cd /d "%~dp0"
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
  "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" -m workflow.web %*
  exit /b
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -m workflow.web %*
  exit /b
)
where python >nul 2>nul
if not errorlevel 1 (
  python -m workflow.web %*
  exit /b
)
echo Python 3.11 or newer is required. Install Python, then run this launcher again.
exit /b 1
