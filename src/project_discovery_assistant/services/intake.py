"""Project intake and clarification context updates."""

from project_discovery_assistant.errors import StorageError
from project_discovery_assistant.models import (
    ClarificationAnswer,
    ProjectContext,
    QuestionStatus,
)
from project_discovery_assistant.services.project_store import ProjectStore


def create_project(
    store: ProjectStore,
    *,
    project_id: str,
    idea: str,
    target_user: str | None = None,
    desired_outcome: str | None = None,
    constraints: list[str] | None = None,
) -> ProjectContext:
    """Create and persist one normalized project context."""
    context = ProjectContext(
        project_id=project_id,
        idea=idea,
        target_user=target_user,
        desired_outcome=desired_outcome,
        constraints=constraints or [],
    )
    store.save_context(context)
    return context


def update_clarification(
    store: ProjectStore,
    *,
    project_id: str,
    question_id: str,
    answer: str | None = None,
    status: QuestionStatus = QuestionStatus.ANSWERED,
) -> ProjectContext:
    """Record an answer, skip, or deferral for an existing question."""
    state = store.load_state(project_id)
    if state.context is None:
        raise StorageError(f"Project '{project_id}' has no input context.")
    for question in state.context.clarification_questions:
        if question.id == question_id:
            question.status = status
            question.answer = ClarificationAnswer(value=answer, status=status)
            store.save_context(state.context)
            return state.context
    raise StorageError(
        f"Clarification question '{question_id}' does not exist in project "
        f"'{project_id}'."
    )
