@echo off
cd /d "%~dp0"
where pythonw >nul 2>nul
if errorlevel 1 (
    echo Python hittades inte. Installera Python fran https://www.python.org/downloads/
    echo och kryssa i "Add python.exe to PATH". Starta sedan om den har filen.
    pause
    exit /b 1
)
start "" pythonw run_gitta.py
