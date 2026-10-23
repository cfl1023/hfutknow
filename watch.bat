@echo off
setlocal
cd /d "%~dp0"
:loop
call update.bat
timeout /t 300 /nobreak >nul
goto loop
