@echo off
setlocal
cd /d "%~dp0"
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY ( where py >nul 2>nul && set "PY=py" )
if not defined PY set "PY=C:\Users\lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

echo [1/2] Fetching official sites...
"%PY%" -m pipeline.sync --limit 8 --enrich
echo.
echo [2/2] Packaging single file...
"%PY%" tools\build_standalone.py

echo.
echo Done. Double-click the file in the parent folder: gongdazhidao.html
pause
