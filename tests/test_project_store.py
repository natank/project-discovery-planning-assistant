"""Tests for safe local project persistence."""

from pathlib import Path

import pytest

from project_discovery_assistant.errors import StorageError
from project_discovery_assistant.services.project_store import ProjectStore
from tests.test_models import make_package


def test_store_round_trips_state_and_package(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    package = make_package()

    saved = store.save_draft(package, "# Draft package")
    restored = store.load_state("demo")

    assert saved.current_package == package
    assert restored.current_package == package
    assert (tmp_path / "projects" / "demo" / "package-v001.md").read_text() == (
        "# Draft package"
    )


def test_accepted_package_survives_later_draft(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    accepted = make_package()
    store.save_accepted(accepted, "# Accepted")

    draft = accepted.model_copy(update={"version": 2})
    state = store.save_draft(draft, "# Draft")

    assert state.current_package == draft
    assert state.accepted_package == accepted
    assert state.package_versions == [1, 2]


def test_project_ids_are_safe(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")

    with pytest.raises(StorageError):
        store.project_dir("../escape")
    with pytest.raises(StorageError):
        store.project_dir("Project With Spaces")


def test_malformed_state_is_reported(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    project_dir = tmp_path / "projects" / "demo"
    project_dir.mkdir(parents=True)
    (project_dir / "state.json").write_text("{not-json", encoding="utf-8")

    with pytest.raises(StorageError, match="Could not load state"):
        store.load_state("demo")


def test_empty_package_artifact_is_rejected(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")

    with pytest.raises(StorageError, match="empty package"):
        store.save_draft(make_package(), " ")
