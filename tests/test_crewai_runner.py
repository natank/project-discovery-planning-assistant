"""Contract and failure tests for the CrewAI adapter."""

from types import SimpleNamespace

import pytest

from project_discovery_assistant.crew.agents import build_agents
from project_discovery_assistant.crew.runner import CrewAIExecutionError, CrewAIRunner
from project_discovery_assistant.crew.tasks import (
    BacklogOutput,
    QuestionsOutput,
    RequirementsOutput,
    ScopeOutput,
)
from project_discovery_assistant.models import ProjectContext
from project_discovery_assistant.services.runner import (
    DeterministicRunner,
    DiscoveryRunner,
)


def make_context() -> ProjectContext:
    return ProjectContext(
        project_id="demo",
        idea="Create a project planning assistant.",
        target_user="Idea owner",
        desired_outcome="A reviewable plan",
    )


def test_crewai_runner_implements_protocol_without_provider_call() -> None:
    runner = CrewAIRunner(agents=build_agents("fixture"), crew_factory=fixture_crew)

    assert isinstance(runner, DiscoveryRunner)
    assert runner.frame_discovery(make_context()).target_users == ["Idea owner"]


def test_crewai_runner_converts_all_stage_envelopes() -> None:
    context = make_context()
    runner = CrewAIRunner(agents=build_agents("fixture"), crew_factory=fixture_crew)
    summary = runner.frame_discovery(context)
    scope, risks = runner.propose_scope(context, summary)
    requirements, stories = runner.specify_requirements(
        context,
        summary,
        scope,
        risks,
    )
    backlog = runner.plan_delivery(requirements, stories)
    report = runner.review_quality(
        context,
        summary,
        scope,
        risks,
        requirements,
        stories,
        backlog,
    )

    assert runner.assess_clarification(context) == []
    assert scope.included_capabilities
    assert requirements[0].id == "REQ-001"
    assert stories[0].requirement_ids == ["REQ-001"]
    assert backlog[0].story_ids == ["US-001"]
    assert report.findings == []


def test_crewai_runner_retries_only_configured_attempts() -> None:
    calls = 0

    def flaky_crew(agent, task):
        nonlocal calls
        calls += 1
        if calls == 1:
            return FailingCrew()
        return fixture_crew(agent, task)

    runner = CrewAIRunner(
        agents=build_agents("fixture"),
        max_attempts=2,
        crew_factory=flaky_crew,
    )

    assert runner.frame_discovery(make_context()).target_users
    assert calls == 2


def test_crewai_runner_stops_on_invalid_output() -> None:
    runner = CrewAIRunner(
        agents=build_agents("fixture"),
        crew_factory=lambda agent, task: InvalidCrew(),
    )

    with pytest.raises(CrewAIExecutionError, match="DiscoverySummary"):
        runner.frame_discovery(make_context())


class FailingCrew:
    def kickoff(self):
        raise RuntimeError("temporary provider failure")


class InvalidCrew:
    def kickoff(self):
        return SimpleNamespace(raw="{}")


def fixture_crew(agent, task):
    fixture = DeterministicRunner()
    context = make_context()
    summary = fixture.frame_discovery(context)
    scope, risks = fixture.propose_scope(context, summary)
    requirements, stories = fixture.specify_requirements(
        context,
        summary,
        scope,
        risks,
    )
    backlog = fixture.plan_delivery(requirements, stories)
    values = {
        "Assess clarification": QuestionsOutput(questions=[]),
        "Frame discovery": summary,
        "Propose scope": ScopeOutput(scope=scope, risks=risks),
        "Specify requirements": RequirementsOutput(
            requirements=requirements,
            stories=stories,
        ),
        "Plan delivery": BacklogOutput(backlog=backlog),
        "Review quality": fixture.review_quality(
            context,
            summary,
            scope,
            risks,
            requirements,
            stories,
            backlog,
        ),
    }
    return SimpleNamespace(kickoff=lambda: SimpleNamespace(pydantic=values[task.name]))
