"""Provider-independent runner protocol and deterministic implementation."""

from enum import StrEnum
from typing import Protocol, runtime_checkable

from project_discovery_assistant.models import (
    BacklogItem,
    Certainty,
    ClarificationQuestion,
    DiscoverySummary,
    FindingSeverity,
    Priority,
    ProductRequirement,
    ProjectContext,
    ProvenanceClaim,
    QualityFinding,
    QualityReport,
    Risk,
    ScopeProposal,
    UserStory,
)


class RunnerError(RuntimeError):
    """Raised when a runner stage fails."""


class FakeFailureMode(StrEnum):
    """Controlled failures used by deterministic tests."""

    NONE = "none"
    INVALID_DISCOVERY = "invalid_discovery"
    FAILED_SCOPE = "failed_scope"
    QUALITY_ERROR = "quality_error"


@runtime_checkable
class DiscoveryRunner(Protocol):
    """Contract implemented by deterministic and CrewAI runners."""

    def assess_clarification(
        self,
        context: ProjectContext,
    ) -> list[ClarificationQuestion]:
        """Identify material clarification questions."""

    def frame_discovery(self, context: ProjectContext) -> DiscoverySummary:
        """Frame the problem and target users."""

    def propose_scope(
        self,
        context: ProjectContext,
        summary: DiscoverySummary,
    ) -> tuple[ScopeProposal, list[Risk]]:
        """Propose MVP scope and risks."""

    def specify_requirements(
        self,
        context: ProjectContext,
        summary: DiscoverySummary,
        scope: ScopeProposal,
        risks: list[Risk],
    ) -> tuple[list[ProductRequirement], list[UserStory]]:
        """Derive requirements and user stories."""

    def plan_delivery(
        self,
        requirements: list[ProductRequirement],
        stories: list[UserStory],
    ) -> list[BacklogItem]:
        """Build a delivery backlog."""

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
        """Review the generated artifacts."""


class DeterministicRunner:
    """Fixture-backed runner with no network or provider dependency."""

    def __init__(self, failure_mode: FakeFailureMode = FakeFailureMode.NONE) -> None:
        self.failure_mode = failure_mode

    def assess_clarification(
        self,
        context: ProjectContext,
    ) -> list[ClarificationQuestion]:
        if context.target_user:
            return []
        return [
            ClarificationQuestion(
                id="CQ-001",
                question="Who is the primary target user?",
                why_it_matters="The MVP boundary depends on the target user's outcome.",
                priority=Priority.P0,
            )
        ]

    def frame_discovery(self, context: ProjectContext) -> DiscoverySummary:
        if self.failure_mode == FakeFailureMode.INVALID_DISCOVERY:
            raise RunnerError(
                "Deterministic fixture returned invalid discovery output."
            )
        target_user = context.target_user or "Unconfirmed target user"
        certainty = (
            Certainty.PROVIDED if context.target_user else Certainty.OPEN_QUESTION
        )
        return DiscoverySummary(
            problem_statement="Software ideas lack a shared, actionable plan.",
            target_users=[target_user],
            stakeholders=["Delivery collaborator"],
            needs=["A clear project direction"],
            outcomes=[context.desired_outcome or "A reviewable discovery package"],
            constraints=context.constraints,
            claims=[
                ProvenanceClaim(
                    text=f"Primary target user: {target_user}",
                    certainty=certainty,
                    source_refs=["project-context"],
                )
            ],
        )

    def propose_scope(
        self,
        context: ProjectContext,
        summary: DiscoverySummary,
    ) -> tuple[ScopeProposal, list[Risk]]:
        if self.failure_mode == FakeFailureMode.FAILED_SCOPE:
            raise RunnerError("Deterministic scope stage failed.")
        return (
            ScopeProposal(
                mvp_outcome=summary.outcomes[0],
                included_capabilities=[
                    "Capture and clarify a software idea",
                    "Generate a reviewable planning package",
                ],
                non_goals=["Implement the proposed production software"],
                follow_ons=["External delivery-tool integration"],
                trade_offs=["Local single-project workflow first"],
            ),
            [
                Risk(
                    id="RISK-001",
                    category="product",
                    description="The idea may remain underspecified.",
                    impact="The proposed MVP may require revision.",
                    certainty=Certainty.ASSUMPTION,
                    validation_or_mitigation="Review open questions before acceptance.",
                )
            ],
        )

    def specify_requirements(
        self,
        context: ProjectContext,
        summary: DiscoverySummary,
        scope: ScopeProposal,
        risks: list[Risk],
    ) -> tuple[list[ProductRequirement], list[UserStory]]:
        requirement = ProductRequirement(
            id="REQ-001",
            statement="The idea owner can submit and review a software idea.",
            target_user_or_outcome=summary.target_users[0],
            priority=Priority.P0,
            rationale="Discovery must begin from explicit idea-owner context.",
            acceptance_considerations=["Submitted context is displayed for review."],
        )
        story = UserStory(
            id="US-001",
            target_user_role="Idea owner",
            capability="Submit and review a software idea",
            value="Discovery starts from shared context.",
            priority=Priority.P0,
            requirement_ids=[requirement.id],
            acceptance_criteria=["The submitted idea is visible in the package."],
        )
        return [requirement], [story]

    def plan_delivery(
        self,
        requirements: list[ProductRequirement],
        stories: list[UserStory],
    ) -> list[BacklogItem]:
        return [
            BacklogItem(
                id="BL-001",
                title="Capture and review idea",
                outcome="The project starts from explicit context.",
                story_ids=[stories[0].id],
                priority=requirements[0].priority,
                validation_method="CLI integration test",
            )
        ]

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
        if self.failure_mode == FakeFailureMode.QUALITY_ERROR:
            return QualityReport(
                findings=[
                    QualityFinding(
                        code="fixture-quality-error",
                        severity=FindingSeverity.ERROR,
                        message="Deterministic quality failure requested.",
                    )
                ]
            )
        return QualityReport()
