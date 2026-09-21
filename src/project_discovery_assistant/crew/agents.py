"""CrewAI agent definitions for the discovery workflow."""

from dataclasses import dataclass

from crewai import LLM, Agent


@dataclass(frozen=True)
class DiscoveryAgents:
    """The six restricted agents used by the sequential workflow."""

    clarification: Agent
    discovery: Agent
    scope: Agent
    requirements: Agent
    planning: Agent
    quality: Agent


def build_agents(llm: LLM) -> DiscoveryAgents:
    """Build agents with no tools, delegation, or code execution."""
    common = {
        "llm": llm,
        "allow_delegation": False,
        "tools": [],
        "allow_code_execution": False,
        "verbose": False,
    }
    return DiscoveryAgents(
        clarification=Agent(
            role="Clarification analyst",
            goal="Identify only material unanswered questions in the supplied context.",
            backstory="You separate known facts from uncertainty.",
            **common,
        ),
        discovery=Agent(
            role="Discovery analyst",
            goal="Frame the problem, users, needs, outcomes, and constraints.",
            backstory="You produce evidence-aware discovery summaries.",
            **common,
        ),
        scope=Agent(
            role="Scope planner",
            goal="Propose a disciplined MVP boundary and material risks.",
            backstory="You make trade-offs explicit and avoid invented evidence.",
            **common,
        ),
        requirements=Agent(
            role="Product requirements analyst",
            goal=(
                "Derive testable requirements and user stories from validated context."
            ),
            backstory="You preserve traceability from outcomes to behavior.",
            **common,
        ),
        planning=Agent(
            role="Delivery planner",
            goal="Turn requirements and stories into an actionable backlog.",
            backstory="You create navigable delivery links and validation methods.",
            **common,
        ),
        quality=Agent(
            role="Quality reviewer",
            goal="Find completeness, certainty, scope, and traceability issues.",
            backstory="You report findings without rewriting the source artifacts.",
            **common,
        ),
    )
