"""Deterministic discovery-package orchestration."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import TypeVar

from pydantic import ValidationError

from project_discovery_assistant.errors import StorageError
from project_discovery_assistant.models import (
    ClarificationQuestion,
    DiscoveryPackage,
    ProjectContext,
    RunEvent,
    RunOutcome,
)
from project_discovery_assistant.services.package_assembly import assemble_package
from project_discovery_assistant.services.project_store import ProjectStore
from project_discovery_assistant.services.rendering import render_package
from project_discovery_assistant.services.runner import DiscoveryRunner, RunnerError

T = TypeVar("T")


def generate_project(
    store: ProjectStore,
    runner: DiscoveryRunner,
    project_id: str,
) -> DiscoveryPackage:
    """Run all deterministic stages and persist a draft package."""
    state = store.load_state(project_id)
    if state.context is None:
        raise StorageError(f"Project '{project_id}' has no input context.")
    context = state.context

    questions = _stage(
        store,
        project_id,
        "clarification",
        "assess-clarification",
        lambda: runner.assess_clarification(context),
    )
    context = _merge_questions(context, questions)
    store.save_context(context)

    summary = _stage(
        store,
        project_id,
        "discovery",
        "frame-discovery",
        lambda: runner.frame_discovery(context),
    )
    scope, risks = _stage(
        store,
        project_id,
        "scope",
        "propose-scope",
        lambda: runner.propose_scope(context, summary),
    )
    requirements, stories = _stage(
        store,
        project_id,
        "requirements",
        "specify-requirements",
        lambda: runner.specify_requirements(context, summary, scope, risks),
    )
    backlog = _stage(
        store,
        project_id,
        "planning",
        "plan-delivery",
        lambda: runner.plan_delivery(requirements, stories),
    )
    quality = _stage(
        store,
        project_id,
        "quality",
        "review-quality",
        lambda: runner.review_quality(
            context,
            summary,
            scope,
            risks,
            requirements,
            stories,
            backlog,
        ),
    )

    version = max(state.package_versions, default=0) + 1
    package = assemble_package(
        context=context,
        summary=summary,
        scope=scope,
        risks=risks,
        requirements=requirements,
        stories=stories,
        backlog=backlog,
        quality_report=quality,
        version=version,
    )
    markdown = render_package(package)
    store.save_draft(package, markdown)
    _record_event(
        store,
        project_id=project_id,
        stage="package",
        task_name="persist-draft",
        outcome=RunOutcome.SUCCEEDED,
        package_version=package.version,
    )
    return package


def _stage(
    store: ProjectStore,
    project_id: str,
    stage: str,
    task_name: str,
    operation: Callable[[], T],
) -> T:
    started = datetime.now(UTC)
    _record_event(
        store,
        project_id=project_id,
        stage=stage,
        task_name=task_name,
        outcome=RunOutcome.STARTED,
    )
    try:
        result = operation()
    except (RunnerError, StorageError, ValidationError, ValueError) as error:
        _record_event(
            store,
            project_id=project_id,
            stage=stage,
            task_name=task_name,
            outcome=RunOutcome.FAILED,
            duration_ms=_duration_ms(started),
            error_category=error.__class__.__name__,
            error_message=str(error),
        )
        raise
    _record_event(
        store,
        project_id=project_id,
        stage=stage,
        task_name=task_name,
        outcome=RunOutcome.SUCCEEDED,
        duration_ms=_duration_ms(started),
    )
    return result


def _record_event(
    store: ProjectStore,
    *,
    project_id: str,
    stage: str,
    task_name: str,
    outcome: RunOutcome,
    duration_ms: int | None = None,
    package_version: int | None = None,
    error_category: str | None = None,
    error_message: str | None = None,
) -> None:
    store.append_event(
        RunEvent(
            timestamp=datetime.now(UTC),
            project_id=project_id,
            package_version=package_version,
            stage=stage,
            task_name=task_name,
            outcome=outcome,
            duration_ms=duration_ms,
            error_category=error_category,
            error_message=error_message,
        )
    )


def _duration_ms(started: datetime) -> int:
    return max(0, int((datetime.now(UTC) - started).total_seconds() * 1000))


def _merge_questions(
    context: ProjectContext,
    questions: list[ClarificationQuestion],
) -> ProjectContext:
    existing = {question.id: question for question in context.clarification_questions}
    merged = [existing.get(question.id, question) for question in questions]
    return context.model_copy(update={"clarification_questions": merged})
