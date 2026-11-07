# Builds dist\Gitta.exe (single file, no console window).
# Run from the gitta folder:  .\build.ps1
python -m pip install --upgrade pyinstaller
python -m PyInstaller --noconfirm --onefile --noconsole --name Gitta run_gitta.py
Write-Host "Done: dist\Gitta.exe"
