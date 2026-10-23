@echo off
setlocal
cd /d "%~dp0"
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY ( where py >nul 2>nul && set "PY=py" )
if not defined PY set "PY=C:\Users\lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

if not exist cloudflared.exe (
  echo Downloading cloudflared ...
  powershell -NoProfile -Command "Invoke-WebRequest -Uri https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe -OutFile cloudflared.exe"
)
start "hfutknow-server" /min "%PY%" serve.py 8710
echo.
echo Starting public tunnel. Look for the https://xxxx.trycloudflare.com address below.
echo Open that address on your phone (works on mobile data, no same-WiFi needed).
echo.
cloudflared.exe tunnel --url http://127.0.0.1:8710
pause
