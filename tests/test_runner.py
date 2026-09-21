"""Contract tests for the deterministic runner."""

from project_discovery_assistant.models import ProjectContext
from project_discovery_assistant.services.runner import (
    DeterministicRunner,
    DiscoveryRunner,
    FakeFailureMode,
    RunnerError,
)


def make_context() -> ProjectContext:
    return ProjectContext(
        project_id="demo",
        idea="Create a project planning assistant.",
        target_user="Idea owner",
        desired_outcome="A reviewable plan",
    )


def test_deterministic_runner_implements_protocol() -> None:
    runner = DeterministicRunner()

    assert isinstance(runner, DiscoveryRunner)


def test_runner_returns_typed_outputs_for_each_stage() -> None:
    runner = DeterministicRunner()
    context = make_context()
    questions = runner.assess_clarification(context)
    summary = runner.frame_discovery(context)
    scope, risks = runner.propose_scope(context, summary)
    requirements, stories = runner.specify_requirements(context, summary, scope, risks)
    backlog = runner.plan_delivery(requirements, stories)
    report = runner.review_quality(
        context, summary, scope, risks, requirements, stories, backlog
    )

    assert questions == []
    assert summary.target_users
    assert scope.included_capabilities
    assert risks
    assert requirements[0].id == "REQ-001"
    assert stories[0].requirement_ids == ["REQ-001"]
    assert backlog[0].story_ids == ["US-001"]
    assert report.findings == []


def test_runner_can_return_clarification_question() -> None:
    context = make_context().model_copy(update={"target_user": None})

    questions = DeterministicRunner().assess_clarification(context)

    assert questions[0].id == "CQ-001"


def test_runner_failure_modes_are_explicit() -> None:
    context = make_context()
    summary = DeterministicRunner().frame_discovery(context)

    try:
        DeterministicRunner(FakeFailureMode.FAILED_SCOPE).propose_scope(
            context, summary
        )
    except RunnerError as error:
        assert "scope stage failed" in str(error)
    else:
        raise AssertionError("Expected deterministic scope failure.")

    report = DeterministicRunner(FakeFailureMode.QUALITY_ERROR).review_quality(
        context,
        summary,
        DeterministicRunner().propose_scope(context, summary)[0],
        [],
        [],
        [],
        [],
    )
    assert report.has_errors
