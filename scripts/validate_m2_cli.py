"""Run the provider-free M2 CLI validation journey in an isolated directory."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ID = "m2-validation"


def run_cli(projects_dir: Path, *arguments: str) -> str:
    """Run one CLI command and fail with its captured output on error."""
    environment = os.environ.copy()
    environment.pop("OPENAI_API_KEY", None)
    environment["PDPA_PROJECTS_DIR"] = str(projects_dir)
    result = subprocess.run(
        [sys.executable, "-m", "project_discovery_assistant.cli", *arguments],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"CLI command failed ({result.returncode}):\n"
            f"$ pdpa {' '.join(arguments)}\n"
            f"{result.stdout}{result.stderr}"
        )
    return result.stdout


def main() -> None:
    """Validate new, clarify, and generate as a real CLI subprocess journey."""
    with tempfile.TemporaryDirectory(prefix="pdpa-m2-validation-") as temporary_dir:
        projects_dir = Path(temporary_dir) / "projects"

        created = run_cli(
            projects_dir,
            "new",
            "--project-id",
            PROJECT_ID,
            "--idea",
            "Create a project discovery and planning assistant.",
        )
        assert f"Created project '{PROJECT_ID}'." in created

        clarified = run_cli(projects_dir, "clarify", PROJECT_ID)
        assert "No clarification questions are currently pending." in clarified

        generated = run_cli(projects_dir, "generate", PROJECT_ID)
        assert "Generated package v001" in generated
        assert "Next action: review the generated package." in generated

        project_dir = projects_dir / PROJECT_ID
        state = json.loads((project_dir / "state.json").read_text(encoding="utf-8"))
        package = (project_dir / "package-v001.md").read_text(encoding="utf-8")
        events = (project_dir / "run-events.jsonl").read_text(encoding="utf-8")

        assert state["context"]["idea"] == (
            "Create a project discovery and planning assistant."
        )
        for artifact_id in ("REQ-001", "US-001", "BL-001"):
            assert artifact_id in package
        assert "## Traceability" in package
        assert "OPENAI_API_KEY" not in package
        assert '"outcome":"succeeded"' in events

    print("M2 CLI validation passed: new -> clarify -> generate")


if __name__ == "__main__":
    main()
