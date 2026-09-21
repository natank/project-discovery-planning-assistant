"""Safe local persistence for one-project runtime artifacts."""

import os
import re
import tempfile
from collections.abc import Iterable
from pathlib import Path

from pydantic import ValidationError

from project_discovery_assistant.errors import StorageError
from project_discovery_assistant.models import (
    DiscoveryPackage,
    ProjectContext,
    ProjectState,
    RunEvent,
)

PROJECT_ID_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")


class ProjectStore:
    """Persist validated project state and package artifacts under one root."""

    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()

    def project_dir(self, project_id: str) -> Path:
        """Return a safe project directory, rejecting traversal and ambiguity."""
        if not PROJECT_ID_PATTERN.fullmatch(project_id):
            raise StorageError(
                "Project ID must contain lowercase letters, numbers, and internal "
                "hyphens only."
            )
        project_dir = (self.root / project_id).resolve()
        try:
            project_dir.relative_to(self.root)
        except ValueError as error:
            raise StorageError(
                "Project ID resolves outside the projects directory."
            ) from error
        return project_dir

    def load_state(self, project_id: str) -> ProjectState:
        """Load and validate state for a project."""
        path = self.project_dir(project_id) / "state.json"
        if not path.exists():
            raise StorageError(f"No state exists for project '{project_id}'.")
        try:
            return ProjectState.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValidationError) as error:
            raise StorageError(
                f"Could not load state for project '{project_id}'."
            ) from error

    def save_draft(self, package: DiscoveryPackage, markdown: str) -> ProjectState:
        """Persist a draft while retaining any previously accepted package."""
        state = self._state_for_save(package.project_id)
        state.current_package = package
        if package.version not in state.package_versions:
            state.package_versions.append(package.version)
        self._write_package(package, markdown)
        self._write_state(state)
        return state

    def save_context(self, context: ProjectContext) -> ProjectState:
        """Persist idea-owner input before package generation."""
        state = self._state_for_save(context.project_id)
        state.context = context
        self._write_state(state)
        return state

    def save_accepted(
        self,
        package: DiscoveryPackage,
        markdown: str,
    ) -> ProjectState:
        """Persist an accepted package as both current and accepted state."""
        state = self._state_for_save(package.project_id)
        state.current_package = package
        state.accepted_package = package
        if package.version not in state.package_versions:
            state.package_versions.append(package.version)
        self._write_package(package, markdown)
        self._write_state(state)
        return state

    def append_event(
        self,
        event: RunEvent,
        *,
        redactions: Iterable[str] = (),
    ) -> None:
        """Append one validated, redacted event to a project's JSONL log."""
        directory = self.project_dir(event.project_id)
        directory.mkdir(parents=True, exist_ok=True)
        serialized = event.model_dump_json()
        for secret in redactions:
            if secret:
                serialized = serialized.replace(secret, "[REDACTED]")
        try:
            with (directory / "run-events.jsonl").open(
                "a",
                encoding="utf-8",
            ) as events_file:
                events_file.write(serialized + "\n")
                events_file.flush()
                os.fsync(events_file.fileno())
        except OSError as error:
            raise StorageError("Could not persist run event.") from error

    def load_events(self, project_id: str) -> list[RunEvent]:
        """Load and validate all events for a project."""
        path = self.project_dir(project_id) / "run-events.jsonl"
        if not path.exists():
            return []
        events: list[RunEvent] = []
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    events.append(RunEvent.model_validate_json(line))
        except (OSError, UnicodeDecodeError, ValidationError) as error:
            raise StorageError(
                f"Could not load events for project '{project_id}'."
            ) from error
        return events

    def _state_for_save(self, project_id: str) -> ProjectState:
        try:
            return self.load_state(project_id)
        except StorageError as error:
            if not str(error).startswith("No state exists"):
                raise
            return ProjectState(project_id=project_id)

    def _write_package(self, package: DiscoveryPackage, markdown: str) -> None:
        if not markdown.strip():
            raise StorageError("Cannot persist an empty package.")
        directory = self.project_dir(package.project_id)
        directory.mkdir(parents=True, exist_ok=True)
        self._atomic_write_text(
            directory / f"package-v{package.version:03d}.md",
            markdown,
        )

    def _write_state(self, state: ProjectState) -> None:
        directory = self.project_dir(state.project_id)
        directory.mkdir(parents=True, exist_ok=True)
        self._atomic_write_text(
            directory / "state.json",
            state.model_dump_json(indent=2),
        )

    def _atomic_write_text(self, target: Path, content: str) -> None:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=target.parent,
                prefix=f".{target.name}.",
                delete=False,
            ) as temporary:
                temporary.write(content)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = Path(temporary.name)
            os.replace(temporary_path, target)
        except OSError as error:
            if "temporary_path" in locals():
                temporary_path.unlink(missing_ok=True)
            raise StorageError(f"Could not persist '{target.name}'.") from error
