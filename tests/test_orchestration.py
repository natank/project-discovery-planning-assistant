"""Tests for deterministic end-to-end orchestration."""

from pathlib import Path

import pytest

from project_discovery_assistant.errors import StorageError
from project_discovery_assistant.models import ProjectState
from project_discovery_assistant.services.intake import create_project
from project_discovery_assistant.services.orchestration import generate_project
from project_discovery_assistant.services.project_store import ProjectStore
from project_discovery_assistant.services.runner import (
    DeterministicRunner,
    FakeFailureMode,
    RunnerError,
)


def test_generate_persists_complete_draft_and_stage_events(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    create_project(
        store,
        project_id="demo",
        idea="Create a planning assistant.",
        target_user="Idea owner",
    )

    package = generate_project(store, DeterministicRunner(), "demo")

    assert package.version == 1
    assert package.requirements
    assert (tmp_path / "projects" / "demo" / "package-v001.md").exists()
    events = store.load_events("demo")
    assert any(event.stage == "package" for event in events)
    assert all(event.outcome.value != "failed" for event in events)


def test_failed_stage_is_recorded_and_propagated(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    create_project(store, project_id="demo", idea="Create a plan.")

    with pytest.raises(RunnerError):
        generate_project(
            store,
            DeterministicRunner(FakeFailureMode.FAILED_SCOPE),
            "demo",
        )

    events = store.load_events("demo")
    assert any(event.outcome.value == "failed" for event in events)
    assert not (tmp_path / "projects" / "demo" / "package-v001.md").exists()


def test_generation_requires_context(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    store._write_state(ProjectState(project_id="demo"))
    with pytest.raises(StorageError, match="no input context"):
        generate_project(store, DeterministicRunner(), "demo")
