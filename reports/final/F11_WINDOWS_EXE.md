# Windows `.exe` Build

The project can be distributed as a standalone Windows desktop game. The
generated executable includes Python, Pygame, the AI core, and
`starter/sample_states.json`; the recipient does not need Python installed.
The application resolves this benchmark file from both the normal source tree
and PyInstaller's temporary `_MEIPASS` bundle directory.

From `project-02-board-game` in PowerShell:

```powershell
.\build_windows.ps1
```

The output is:

```text
dist\ConnectFourArena.exe
```

Double-click `ConnectFourArena.exe` to launch the game. The build is offline
at runtime and does not use a hosted service.

The first build downloads build dependencies if they are not installed. After
the `.exe` is created, only the file in `dist\` is needed for normal gameplay.
Windows Defender or SmartScreen may show a warning for locally unsigned
executables; choose the normal Windows option to allow a trusted local build.

## Manual equivalent

```powershell
pip install -r requirements-build.txt
python -m PyInstaller --windowed --onefile `
  --name ConnectFourArena `
  --add-data "starter\sample_states.json;starter" `
  --paths starter starter\app.py
```
