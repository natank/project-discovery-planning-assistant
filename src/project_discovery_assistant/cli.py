"""Command-line entry point for the Project Discovery and Planning Assistant."""

from typing import Annotated

import typer

from project_discovery_assistant.config import Settings
from project_discovery_assistant.errors import StorageError
from project_discovery_assistant.models import QuestionStatus
from project_discovery_assistant.services.intake import (
    create_project,
    update_clarification,
)
from project_discovery_assistant.services.project_store import ProjectStore

app = typer.Typer(
    help="Explore and plan a software project from an initial idea.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Run the Project Discovery and Planning Assistant."""


@app.command()
def new(
    project_id: Annotated[str, typer.Option(help="Lowercase project identifier.")],
    idea: Annotated[str, typer.Option(help="Initial software idea.")],
    target_user: Annotated[
        str | None,
        typer.Option(help="Intended target user or audience."),
    ] = None,
    desired_outcome: Annotated[
        str | None,
        typer.Option(help="Desired outcome."),
    ] = None,
    constraint: Annotated[
        list[str] | None,
        typer.Option(help="Relevant constraint; may be repeated."),
    ] = None,
) -> None:
    """Create a project from idea-owner input."""
    store = ProjectStore(Settings().resolved_projects_dir())
    try:
        context = create_project(
            store,
            project_id=project_id,
            idea=idea,
            target_user=target_user,
            desired_outcome=desired_outcome,
            constraints=constraint,
        )
    except (StorageError, ValueError) as error:
        typer.echo(f"Could not create project: {error}", err=True)
        raise typer.Exit(code=1) from error
    typer.echo(f"Created project '{context.project_id}'.")
    typer.echo("Next action: run 'pdpa clarify' or 'pdpa generate'.")


@app.command()
def clarify(
    project_id: Annotated[str, typer.Argument(help="Project identifier.")],
    question_id: Annotated[
        str | None,
        typer.Option(help="Question identifier to answer."),
    ] = None,
    answer: Annotated[
        str | None,
        typer.Option(help="Answer text."),
    ] = None,
    skip: Annotated[
        bool,
        typer.Option(help="Skip the selected question."),
    ] = False,
    defer: Annotated[
        bool,
        typer.Option(help="Defer the selected question."),
    ] = False,
) -> None:
    """Review or update clarification questions."""
    store = ProjectStore(Settings().resolved_projects_dir())
    try:
        state = store.load_state(project_id)
        if state.context is None:
            raise StorageError(f"Project '{project_id}' has no input context.")
        if question_id is None:
            questions = state.context.clarification_questions
            if not questions:
                typer.echo("No clarification questions are currently pending.")
                return
            for question in questions:
                typer.echo(f"{question.id}: {question.question} ({question.status})")
            return
        if skip and defer:
            raise StorageError("A question cannot be both skipped and deferred.")
        status = (
            QuestionStatus.SKIPPED
            if skip
            else QuestionStatus.DEFERRED
            if defer
            else QuestionStatus.ANSWERED
        )
        update_clarification(
            store,
            project_id=project_id,
            question_id=question_id,
            answer=answer,
            status=status,
        )
    except (StorageError, ValueError) as error:
        typer.echo(f"Could not update clarification: {error}", err=True)
        raise typer.Exit(code=1) from error
    typer.echo(f"Updated clarification '{question_id}' to {status}.")


if __name__ == "__main__":
    app()
