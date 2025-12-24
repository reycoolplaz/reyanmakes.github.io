@echo off
cd /d "%~dp0"
echo Starting Reyan Makes server...
echo Admin panel: http://localhost:5000/admin
echo.
python server.py
pause
