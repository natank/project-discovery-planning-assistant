"""CrewAI adapter implementing the product runner protocol."""

import json
from collections.abc import Callable
from typing import Any, TypeVar

from crewai import Agent, Crew, Process, Task
from pydantic import BaseModel, ValidationError

from project_discovery_assistant.crew.agents import DiscoveryAgents, build_agents
from project_discovery_assistant.crew.model import build_llm
from project_discovery_assistant.crew.tasks import (
    BacklogOutput,
    QuestionsOutput,
    RequirementsOutput,
    ScopeOutput,
    clarification_task,
    discovery_task,
    planning_task,
    quality_task,
    requirements_task,
    scope_task,
)
from project_discovery_assistant.models import (
    BacklogItem,
    ClarificationQuestion,
    DiscoverySummary,
    ProductRequirement,
    ProjectContext,
    QualityReport,
    Risk,
    ScopeProposal,
    UserStory,
)
from project_discovery_assistant.services.runner import DiscoveryRunner, RunnerError

T = TypeVar("T", bound=BaseModel)


class CrewAIExecutionError(RunnerError):
    """Raised when CrewAI cannot produce a valid task result."""


class CrewAIRunner(DiscoveryRunner):
    """Sequential CrewAI runner with validated task boundaries."""

    def __init__(
        self,
        *,
        agents: DiscoveryAgents | None = None,
        llm: Any | None = None,
        max_attempts: int = 1,
        crew_factory: Callable[[Agent, Task], Crew] | None = None,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        resolved_llm = llm or build_llm()
        self.agents = agents or build_agents(resolved_llm)
        self.max_attempts = max_attempts
        self._crew_factory = crew_factory or self._default_crew

    def assess_clarification(
        self,
        context: ProjectContext,
    ) -> list[ClarificationQuestion]:
        result = self._execute(
            clarification_task(
                self.agents.clarification,
                context.model_dump_json(),
            ),
            QuestionsOutput,
        )
        return result.questions

    def frame_discovery(self, context: ProjectContext) -> DiscoverySummary:
        return self._execute(
            discovery_task(
                self.agents.discovery,
                context.model_dump_json(),
            ),
            DiscoverySummary,
        )

    def propose_scope(
        self,
        context: ProjectContext,
        summary: DiscoverySummary,
    ) -> tuple[ScopeProposal, list[Risk]]:
        result = self._execute(
            scope_task(
                self.agents.scope,
                _inputs(context, summary),
            ),
            ScopeOutput,
        )
        return result.scope, result.risks

    def specify_requirements(
        self,
        context: ProjectContext,
        summary: DiscoverySummary,
        scope: ScopeProposal,
        risks: list[Risk],
    ) -> tuple[list[ProductRequirement], list[UserStory]]:
        result = self._execute(
            requirements_task(
                self.agents.requirements,
                _inputs(context, summary, scope, risks),
            ),
            RequirementsOutput,
        )
        return result.requirements, result.stories

    def plan_delivery(
        self,
        requirements: list[ProductRequirement],
        stories: list[UserStory],
    ) -> list[BacklogItem]:
        result = self._execute(
            planning_task(
                self.agents.planning,
                _inputs(requirements, stories),
            ),
            BacklogOutput,
        )
        return result.backlog

    def review_quality(
        self,
        context: ProjectContext,
        summary: DiscoverySummary,
        scope: ScopeProposal,
        risks: list[Risk],
        requirements: list[ProductRequirement],
        stories: list[UserStory],
        backlog: list[BacklogItem],
    ) -> QualityReport:
        return self._execute(
            quality_task(
                self.agents.quality,
                _inputs(
                    context,
                    summary,
                    scope,
                    risks,
                    requirements,
                    stories,
                    backlog,
                ),
            ),
            QualityReport,
        )

    def _execute(self, task: Task, model: type[T]) -> T:
        last_error: Exception | None = None
        for attempt in range(self.max_attempts):
            try:
                crew = self._crew_factory(task.agent, task)
                result = crew.kickoff()
                return _validated_output(result, model)
            except (RuntimeError, TypeError, ValueError, ValidationError) as error:
                last_error = error
                if attempt + 1 == self.max_attempts:
                    break
        raise CrewAIExecutionError(
            f"CrewAI task '{task.name or 'unnamed'}' did not produce valid "
            f"{model.__name__} output after {self.max_attempts} attempt(s)."
        ) from last_error

    @staticmethod
    def _default_crew(agent: Agent, task: Task) -> Crew:
        return Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
            memory=False,
        )


def _inputs(*models: Any) -> str:
    """Serialize validated stage inputs without adding hidden context."""
    return "\n\n".join(_serialize_input(model) for model in models)


def _serialize_input(value: Any) -> str:
    if isinstance(value, BaseModel):
        return value.model_dump_json()
    if isinstance(value, (list, tuple)):
        return json.dumps(
            [
                item.model_dump(mode="json") if isinstance(item, BaseModel) else item
                for item in value
            ]
        )
    return json.dumps(value)


def _validated_output(result: Any, model: type[T]) -> T:
    """Convert CrewAI's structured result into the requested domain envelope."""
    structured = getattr(result, "pydantic", None)
    if structured is not None:
        return model.model_validate(structured)
    json_dict = getattr(result, "json_dict", None)
    if json_dict is not None:
        return model.model_validate(json_dict)
    raw = getattr(result, "raw", result)
    if not isinstance(raw, str):
        raise TypeError("CrewAI returned an unsupported task result.")
    return model.model_validate_json(raw)
