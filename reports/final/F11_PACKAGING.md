# F11 — Clean Packaging and Setup

## Supported setup

From the repository root:

```powershell
python -m venv project-02-board-game\.venv
project-02-board-game\.venv\Scripts\Activate.ps1
pip install -r project-02-board-game\requirements.txt
python project-02-board-game\starter\app.py
pytest project-02-board-game\tests\ -v
```

From inside `project-02-board-game`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python starter\app.py
pytest tests\ -v
```

The application uses only local files and does not require network services,
credentials, API keys, or hosted AI providers.

## Package contents

The submission package must include:

- `starter/` source, game rules, and benchmark states.
- `tests/` regression and final acceptance tests.
- `experiments/` scripts and recorded CSV/plot evidence.
- `reports/final/` F01–F11 acceptance documents.
- `presentation.pdf`, `report.pdf`, `README.md`, and `requirements.txt`.

The package must exclude:

- `.venv/`, `venv/`, `__pycache__/`, `.pytest_cache/`, and build artifacts.
- Secrets, `.env` files, credentials, and machine-local configuration.

## Release checks

```powershell
pytest tests\ -q
python -m py_compile starter\app.py starter\student_core.py
```

Before creating an archive, inspect the file list and confirm the excluded
directories are absent. The project-level `.gitignore` and repository-level
`.gitignore` both protect virtual environments and caches.
