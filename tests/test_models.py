"""Tests for the M1 domain contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from project_discovery_assistant.models import (
    ArtifactStatus,
    BacklogItem,
    Certainty,
    ClarificationAnswer,
    DiscoveryPackage,
    DiscoverySummary,
    FindingSeverity,
    Priority,
    ProductRequirement,
    ProjectContext,
    ProvenanceClaim,
    QualityFinding,
    QualityReport,
    ReviewDecision,
    ReviewDecisionType,
    ScopeProposal,
    TraceabilityEntry,
    UserStory,
)


def make_context() -> ProjectContext:
    return ProjectContext(
        project_id="demo",
        idea="Help teams turn ideas into plans.",
        target_user="Idea owner",
        desired_outcome="A reviewable delivery plan",
        provided_facts=[
            ProvenanceClaim(
                text="The idea owner has limited planning time.",
                certainty=Certainty.PROVIDED,
            )
        ],
    )


def make_package() -> DiscoveryPackage:
    requirement = ProductRequirement(
        id="REQ-001",
        statement="The idea owner can submit an idea.",
        target_user_or_outcome="Idea owner",
        priority=Priority.P0,
        rationale="Starts discovery.",
        acceptance_considerations=["Input is retained."],
    )
    story = UserStory(
        id="US-001",
        target_user_role="Idea owner",
        capability="Submit an idea",
        value="Discovery can begin.",
        priority=Priority.P0,
        requirement_ids=["REQ-001"],
        acceptance_criteria=["The idea is displayed for confirmation."],
    )
    backlog = BacklogItem(
        id="BL-001",
        title="Capture idea",
        outcome="A project starts from explicit context.",
        story_ids=["US-001"],
        priority=Priority.P0,
        validation_method="CLI integration test",
    )
    return DiscoveryPackage(
        project_id="demo",
        version=1,
        context=make_context(),
        summary=DiscoverySummary(
            problem_statement="Ideas lack a shared plan.",
            target_users=["Idea owner"],
            needs=["Clarity"],
            outcomes=["A useful plan"],
        ),
        scope=ScopeProposal(
            mvp_outcome="Create a reviewable plan.",
            included_capabilities=["Discovery"],
            non_goals=["Production implementation"],
            trade_offs=["Local-only first release"],
        ),
        requirements=[requirement],
        stories=[story],
        backlog=[backlog],
        traceability=[
            TraceabilityEntry(
                outcome_ref="OUTCOME-001",
                requirement_ids=["REQ-001"],
                story_ids=["US-001"],
                backlog_ids=["BL-001"],
            )
        ],
    )


def test_package_round_trips_with_required_artifacts() -> None:
    package = make_package()

    restored = DiscoveryPackage.model_validate_json(package.model_dump_json())

    assert restored == package
    assert restored.status == ArtifactStatus.DRAFT


def test_blank_required_text_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectContext(project_id=" ", idea="An idea")


def test_clarification_answer_normalizes_whitespace() -> None:
    answer = ClarificationAnswer(value="   ")

    assert answer.value is None


def test_quality_report_exposes_blocking_errors() -> None:
    report = QualityReport(
        findings=[
            QualityFinding(
                code="missing-link",
                severity=FindingSeverity.ERROR,
                message="A link is missing.",
            )
        ]
    )

    assert report.has_errors


def test_review_decision_is_typed_and_timestamped() -> None:
    decision = ReviewDecision(
        artifact_ref="package-v001",
        decision=ReviewDecisionType.ACCEPT,
        decided_at=datetime.now(UTC),
    )

    assert decision.decision == ReviewDecisionType.ACCEPT
