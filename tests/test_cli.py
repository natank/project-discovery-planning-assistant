"""CLI tests for the M2 intake commands."""

from pathlib import Path

from typer.testing import CliRunner

from project_discovery_assistant.cli import app
from project_discovery_assistant.config import Settings


def test_new_command_creates_project(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("PDPA_PROJECTS_DIR", str(tmp_path / "projects"))

    result = CliRunner().invoke(
        app,
        [
            "new",
            "--project-id",
            "demo",
            "--idea",
            "Create a discovery assistant",
        ],
    )

    assert result.exit_code == 0
    assert "Created project 'demo'." in result.stdout
    assert Settings().resolved_projects_dir().joinpath("demo", "state.json").exists()


def test_clarify_lists_empty_questions(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("PDPA_PROJECTS_DIR", str(tmp_path / "projects"))
    runner = CliRunner()
    runner.invoke(
        app,
        ["new", "--project-id", "demo", "--idea", "Create a plan"],
    )

    result = runner.invoke(app, ["clarify", "demo"])

    assert result.exit_code == 0
    assert "No clarification questions" in result.stdout
