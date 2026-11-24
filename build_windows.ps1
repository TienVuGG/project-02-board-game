$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}

& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".venv\Scripts\python.exe" -m pip install -r requirements-build.txt

if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force
}
if (Test-Path "dist") {
    Remove-Item "dist" -Recurse -Force
}

& ".venv\Scripts\python.exe" -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onefile `
    --name "ConnectFourArena" `
    --icon "images.ico" `
    --add-data "starter\sample_states.json;starter" `
    --add-data "assets;assets" `
    --add-data "images.png;." `
    --paths "starter" `
    "starter\app.py"

Write-Host ""
Write-Host "Build complete: dist\ConnectFourArena.exe"
