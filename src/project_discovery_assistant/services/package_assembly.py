"""Assembly of validated runner outputs into a discovery package."""

from project_discovery_assistant.models import (
    BacklogItem,
    DiscoveryPackage,
    DiscoverySummary,
    GenerationStatus,
    ProductRequirement,
    ProjectContext,
    QualityReport,
    Risk,
    ScopeProposal,
    TraceabilityEntry,
    UserStory,
)
from project_discovery_assistant.validation import validate_package


def assemble_package(
    *,
    context: ProjectContext,
    summary: DiscoverySummary,
    scope: ScopeProposal,
    risks: list[Risk],
    requirements: list[ProductRequirement],
    stories: list[UserStory],
    backlog: list[BacklogItem],
    quality_report: QualityReport,
    version: int,
) -> DiscoveryPackage:
    """Assemble and structurally validate a draft discovery package."""
    traceability = [
        TraceabilityEntry(
            outcome_ref=f"OUTCOME-{index:03d}",
            requirement_ids=[requirement.id for requirement in requirements],
            story_ids=[story.id for story in stories],
            backlog_ids=[item.id for item in backlog],
        )
        for index, _ in enumerate(summary.outcomes, start=1)
    ]
    package = DiscoveryPackage(
        project_id=context.project_id,
        version=version,
        generation_status=(
            GenerationStatus.NEEDS_REVIEW
            if quality_report.has_errors
            else GenerationStatus.DRAFT
        ),
        context=context,
        summary=summary,
        scope=scope,
        risks=risks,
        requirements=requirements,
        stories=stories,
        backlog=backlog,
        quality_report=quality_report,
        traceability=traceability,
    )
    structural_report = validate_package(package)
    package.quality_report.findings.extend(structural_report.findings)
    if package.quality_report.has_errors:
        package.generation_status = GenerationStatus.NEEDS_REVIEW
    return package
