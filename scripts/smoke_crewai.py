"""Run the opt-in real-provider CrewAI smoke validation."""

import argparse
import sys

from project_discovery_assistant.config import Settings
from project_discovery_assistant.crew.runner import CrewAIRunner
from project_discovery_assistant.errors import ConfigurationError, StorageError
from project_discovery_assistant.services.orchestration import generate_project
from project_discovery_assistant.services.project_store import ProjectStore
from project_discovery_assistant.services.runner import RunnerError


def main() -> int:
    """Generate one reviewable package using the configured CrewAI runner."""
    parser = argparse.ArgumentParser(
        description="Run an opt-in CrewAI smoke generation for an existing project.",
    )
    parser.add_argument("project_id", help="Existing project identifier.")
    args = parser.parse_args()

    try:
        settings = Settings()
        store = ProjectStore(settings.resolved_projects_dir())
        package = generate_project(store, CrewAIRunner(), args.project_id)
    except (ConfigurationError, RunnerError, StorageError, ValueError) as error:
        print(f"CrewAI smoke run failed: {error}", file=sys.stderr)
        return 1

    package_path = (
        store.project_dir(args.project_id) / f"package-v{package.version:03d}.md"
    )
    print(
        f"CrewAI smoke run produced package v{package.version:03d} "
        f"with status '{package.generation_status.value}'."
    )
    print(f"Package: {package_path}")
    print("Review the package and run-events.jsonl for secret-free output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
