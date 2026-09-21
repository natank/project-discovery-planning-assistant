"""Typed CrewAI task definitions and output envelopes."""

from crewai import Agent, Task
from pydantic import BaseModel, ConfigDict, Field

from project_discovery_assistant.models import (
    BacklogItem,
    ClarificationQuestion,
    DiscoverySummary,
    ProductRequirement,
    QualityReport,
    Risk,
    ScopeProposal,
    UserStory,
)


class TaskEnvelope(BaseModel):
    """Strict base for structured CrewAI task envelopes."""

    model_config = ConfigDict(extra="forbid")


class QuestionsOutput(TaskEnvelope):
    """CrewAI output for clarification assessment."""

    questions: list[ClarificationQuestion] = Field(default_factory=list)


class ScopeOutput(TaskEnvelope):
    """CrewAI output for scope and risk proposal."""

    scope: ScopeProposal
    risks: list[Risk] = Field(default_factory=list)


class RequirementsOutput(TaskEnvelope):
    """CrewAI output for product requirements and stories."""

    requirements: list[ProductRequirement] = Field(min_length=1)
    stories: list[UserStory] = Field(min_length=1)


class BacklogOutput(TaskEnvelope):
    """CrewAI output for delivery planning."""

    backlog: list[BacklogItem] = Field(min_length=1)


def _task(
    *,
    agent: Agent,
    title: str,
    inputs: str,
    output_model: type[BaseModel],
    expected: str,
) -> Task:
    return Task(
        name=title,
        description=(
            f"Use only the supplied input.\n\nInput:\n{inputs}\n\n"
            "Do not invent evidence, claim external validation, take external "
            "actions, or include private reasoning.\n\n"
            "Use these exact stable identifier prefixes and numbering formats: "
            "CQ-001 for clarification questions, RISK-001 for risks, REQ-001 "
            "for product requirements, US-001 for user stories, and BL-001 "
            "for backlog items. Preserve supplied identifiers; allocate the "
            "next sequential identifier only when creating a new artifact."
        ),
        expected_output=expected,
        agent=agent,
        output_pydantic=output_model,
        tools=[],
    )


def clarification_task(agent: Agent, inputs: str) -> Task:
    """Create the clarification task."""
    return _task(
        agent=agent,
        title="Assess clarification",
        inputs=inputs,
        output_model=QuestionsOutput,
        expected="A JSON object containing a questions array.",
    )


def discovery_task(agent: Agent, inputs: str) -> Task:
    """Create the discovery framing task."""
    return _task(
        agent=agent,
        title="Frame discovery",
        inputs=inputs,
        output_model=DiscoverySummary,
        expected="A JSON object matching the DiscoverySummary schema.",
    )


def scope_task(agent: Agent, inputs: str) -> Task:
    """Create the scope proposal task."""
    return _task(
        agent=agent,
        title="Propose scope",
        inputs=inputs,
        output_model=ScopeOutput,
        expected="A JSON object containing scope and risks arrays.",
    )


def requirements_task(agent: Agent, inputs: str) -> Task:
    """Create the requirements task."""
    return _task(
        agent=agent,
        title="Specify requirements",
        inputs=inputs,
        output_model=RequirementsOutput,
        expected="A JSON object containing requirements and stories arrays.",
    )


def planning_task(agent: Agent, inputs: str) -> Task:
    """Create the delivery planning task."""
    return _task(
        agent=agent,
        title="Plan delivery",
        inputs=inputs,
        output_model=BacklogOutput,
        expected="A JSON object containing a backlog array.",
    )


def quality_task(agent: Agent, inputs: str) -> Task:
    """Create the quality review task."""
    return _task(
        agent=agent,
        title="Review quality",
        inputs=inputs,
        output_model=QualityReport,
        expected="A JSON object matching the QualityReport schema.",
    )
