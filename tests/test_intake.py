"""Tests for project intake and clarification updates."""

from pathlib import Path

from project_discovery_assistant.models import (
    ClarificationQuestion,
    Priority,
    QuestionStatus,
)
from project_discovery_assistant.services.intake import (
    create_project,
    update_clarification,
)
from project_discovery_assistant.services.project_store import ProjectStore


def test_create_project_persists_optional_unknown_context(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")

    context = create_project(
        store,
        project_id="demo",
        idea="A project planning assistant",
    )

    assert context.target_user is None
    assert store.load_state("demo").context == context


def test_update_clarification_persists_deferred_answer(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    context = create_project(store, project_id="demo", idea="An idea")
    context.clarification_questions.append(
        ClarificationQuestion(
            id="CQ-001",
            question="Who is the target user?",
            why_it_matters="Scope depends on the user.",
            priority=Priority.P0,
        )
    )
    store.save_context(context)

    updated = update_clarification(
        store,
        project_id="demo",
        question_id="CQ-001",
        status=QuestionStatus.DEFERRED,
    )

    question = updated.clarification_questions[0]
    assert question.status == QuestionStatus.DEFERRED
    assert question.answer is not None
    assert question.answer.status == QuestionStatus.DEFERRED
