"""F11 packaging and clean-setup checks."""
from __future__ import annotations

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]


def test_required_submission_artifacts_exist():
    required = [
        "README.md",
        "requirements.txt",
        "presentation.pdf",
        "report.pdf",
        "starter/app.py",
        "starter/game_engine.py",
        "starter/student_core.py",
        "starter/sample_states.json",
        "tests/test_project_02_sanity.py",
        "reports/final/F11_PACKAGING.md",
    ]
    for relative_path in required:
        assert (PROJECT_DIR / relative_path).is_file(), relative_path


def test_project_does_not_contain_secret_files():
    forbidden_names = {".env", ".env.local", ".env.production"}
    files = [
        path
        for path in PROJECT_DIR.rglob("*")
        if path.is_file() and ".venv" not in path.parts
    ]
    assert not {path.name for path in files} & forbidden_names


def test_setup_instructions_use_windows_and_local_commands():
    readme = (PROJECT_DIR / "README.md").read_text(encoding="utf-8")
    packaging = (PROJECT_DIR / "reports" / "final" / "F11_PACKAGING.md").read_text(
        encoding="utf-8"
    )
    assert "python starter\\app.py" in readme
    assert "pip install -r requirements.txt" in packaging
    assert "pytest tests\\ -v" in packaging
