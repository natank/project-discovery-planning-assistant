"""Validated domain contracts for discovery projects and packages."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Certainty(StrEnum):
    """Provenance of a material claim."""

    PROVIDED = "provided"
    INFERRED = "inferred"
    ASSUMPTION = "assumption"
    OPEN_QUESTION = "open_question"


class ArtifactStatus(StrEnum):
    """Lifecycle state of an artifact or package."""

    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    ACCEPTED = "accepted"
    DEFERRED = "deferred"
    FAILED = "failed"
    STALE = "stale"


class Priority(StrEnum):
    """Delivery priority."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class QuestionStatus(StrEnum):
    """Answer state for a clarification question."""

    UNANSWERED = "unanswered"
    ANSWERED = "answered"
    SKIPPED = "skipped"
    DEFERRED = "deferred"


class ReviewDecisionType(StrEnum):
    """Decision available to the idea owner during review."""

    ACCEPT = "accept"
    REJECT = "reject"
    DEFER = "defer"


class GenerationStatus(StrEnum):
    """Status of a package generation run."""

    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    ACCEPTED = "accepted"
    FAILED = "failed"


class FindingSeverity(StrEnum):
    """Severity emitted by structural or semantic quality checks."""

    ERROR = "error"
    WARNING = "warning"
    NOTE = "note"


class ContractModel(BaseModel):
    """Base model with strict fields and stable schema metadata."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    schema_version: int = Field(default=1, ge=1)


class ProvenanceClaim(ContractModel):
    """A reviewable claim with certainty and source references."""

    text: NonEmptyText
    certainty: Certainty
    source_refs: list[NonEmptyText] = Field(default_factory=list)
    rationale: NonEmptyText | None = None


class ClarificationAnswer(ContractModel):
    """An idea-owner answer or explicit non-answer."""

    value: str | None = None
    status: QuestionStatus = QuestionStatus.UNANSWERED

    @field_validator("value")
    @classmethod
    def normalize_value(cls, value: str | None) -> str | None:
        """Treat whitespace-only answers as unknown."""
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class ClarificationQuestion(ContractModel):
    """A bounded question that addresses material uncertainty."""

    id: NonEmptyText
    question: NonEmptyText
    why_it_matters: NonEmptyText
    priority: Priority
    status: QuestionStatus = QuestionStatus.UNANSWERED
    answer: ClarificationAnswer | None = None


class ProjectContext(ContractModel):
    """Idea-owner input and clarification context for one project."""

    project_id: NonEmptyText
    idea: NonEmptyText
    target_user: NonEmptyText | None = None
    desired_outcome: NonEmptyText | None = None
    constraints: list[NonEmptyText] = Field(default_factory=list)
    provided_facts: list[ProvenanceClaim] = Field(default_factory=list)
    clarification_questions: list[ClarificationQuestion] = Field(default_factory=list)


class DiscoverySummary(ContractModel):
    """Problem, target-user, need, outcome, and constraint framing."""

    problem_statement: NonEmptyText
    target_users: list[NonEmptyText] = Field(min_length=1)
    stakeholders: list[NonEmptyText] = Field(default_factory=list)
    needs: list[NonEmptyText] = Field(min_length=1)
    outcomes: list[NonEmptyText] = Field(min_length=1)
    constraints: list[NonEmptyText] = Field(default_factory=list)
    claims: list[ProvenanceClaim] = Field(default_factory=list)


class ScopeProposal(ContractModel):
    """Proposed first-release boundary."""

    mvp_outcome: NonEmptyText
    included_capabilities: list[NonEmptyText] = Field(min_length=1)
    non_goals: list[NonEmptyText] = Field(min_length=1)
    follow_ons: list[NonEmptyText] = Field(default_factory=list)
    trade_offs: list[NonEmptyText] = Field(min_length=1)


class Risk(ContractModel):
    """A material risk and its suggested validation or mitigation."""

    id: NonEmptyText
    category: NonEmptyText
    description: NonEmptyText
    impact: NonEmptyText
    certainty: Certainty
    validation_or_mitigation: NonEmptyText


class ProductRequirement(ContractModel):
    """Observable product behavior derived from discovery."""

    id: NonEmptyText
    statement: NonEmptyText
    target_user_or_outcome: NonEmptyText
    priority: Priority
    rationale: NonEmptyText
    dependencies: list[NonEmptyText] = Field(default_factory=list)
    acceptance_considerations: list[NonEmptyText] = Field(min_length=1)


class UserStory(ContractModel):
    """A user-centered expression of one or more requirements."""

    id: NonEmptyText
    target_user_role: NonEmptyText
    capability: NonEmptyText
    value: NonEmptyText
    priority: Priority
    requirement_ids: list[NonEmptyText] = Field(min_length=1)
    acceptance_criteria: list[NonEmptyText] = Field(min_length=1)


class BacklogItem(ContractModel):
    """Actionable delivery work linked to user stories."""

    id: NonEmptyText
    title: NonEmptyText
    outcome: NonEmptyText
    story_ids: list[NonEmptyText] = Field(min_length=1)
    priority: Priority
    dependencies: list[NonEmptyText] = Field(default_factory=list)
    validation_method: NonEmptyText
    blockers: list[NonEmptyText] = Field(default_factory=list)


class ReviewDecision(ContractModel):
    """An explicit idea-owner decision on a package or artifact."""

    artifact_ref: NonEmptyText
    decision: ReviewDecisionType
    comment: NonEmptyText | None = None
    decided_at: datetime


class QualityFinding(ContractModel):
    """A quality result that may block acceptance."""

    code: NonEmptyText
    severity: FindingSeverity
    message: NonEmptyText
    artifact_refs: list[NonEmptyText] = Field(default_factory=list)


class QualityReport(ContractModel):
    """Quality findings for one generated package."""

    findings: list[QualityFinding] = Field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Whether any finding blocks acceptance."""
        return any(
            finding.severity == FindingSeverity.ERROR for finding in self.findings
        )


class TraceabilityEntry(ContractModel):
    """One readable link in the outcome-to-delivery chain."""

    outcome_ref: NonEmptyText
    requirement_ids: list[NonEmptyText] = Field(min_length=1)
    story_ids: list[NonEmptyText] = Field(min_length=1)
    backlog_ids: list[NonEmptyText] = Field(min_length=1)


class DiscoveryPackage(ContractModel):
    """Complete, versioned package assembled from validated task outputs."""

    project_id: NonEmptyText
    version: int = Field(ge=1)
    status: ArtifactStatus = ArtifactStatus.DRAFT
    generation_status: GenerationStatus = GenerationStatus.DRAFT
    context: ProjectContext
    summary: DiscoverySummary
    scope: ScopeProposal
    risks: list[Risk] = Field(default_factory=list)
    requirements: list[ProductRequirement] = Field(min_length=1)
    stories: list[UserStory] = Field(min_length=1)
    backlog: list[BacklogItem] = Field(min_length=1)
    quality_report: QualityReport = Field(default_factory=QualityReport)
    traceability: list[TraceabilityEntry] = Field(min_length=1)
    review_decisions: list[ReviewDecision] = Field(default_factory=list)

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: int) -> int:
        """Require positive package versions."""
        if value < 1:
            raise ValueError("version must be positive")
        return value
