@echo off
setlocal
cd /d "%~dp0"
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY ( where py >nul 2>nul && set "PY=py" )
if not defined PY set "PY=C:\Users\lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

echo Starting server. Keep this window open.
echo Open the http://... address below on your phone (same Wi-Fi).
echo.
"%PY%" serve.py 8710
pause
