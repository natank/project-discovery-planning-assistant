"""Tests for package assembly and Markdown rendering."""

from project_discovery_assistant.models import (
    FindingSeverity,
    GenerationStatus,
    QualityFinding,
)
from project_discovery_assistant.services.package_assembly import assemble_package
from project_discovery_assistant.services.rendering import render_package
from project_discovery_assistant.services.runner import DeterministicRunner
from tests.test_runner import make_context


def make_assembled_package():
    context = make_context()
    runner = DeterministicRunner()
    summary = runner.frame_discovery(context)
    scope, risks = runner.propose_scope(context, summary)
    requirements, stories = runner.specify_requirements(
        context,
        summary,
        scope,
        risks,
    )
    backlog = runner.plan_delivery(requirements, stories)
    quality = runner.review_quality(
        context,
        summary,
        scope,
        risks,
        requirements,
        stories,
        backlog,
    )
    return assemble_package(
        context=context,
        summary=summary,
        scope=scope,
        risks=risks,
        requirements=requirements,
        stories=stories,
        backlog=backlog,
        quality_report=quality,
        version=1,
    )


def test_assembly_creates_traceability() -> None:
    package = make_assembled_package()

    assert package.generation_status == GenerationStatus.DRAFT
    assert package.traceability[0].requirement_ids == ["REQ-001"]
    assert package.traceability[0].story_ids == ["US-001"]
    assert package.traceability[0].backlog_ids == ["BL-001"]


def test_renderer_contains_required_sections_and_ids() -> None:
    package = make_assembled_package()

    rendered = render_package(package)

    assert "## Discovery summary" in rendered
    assert "## MVP scope" in rendered
    assert "REQ-001" in rendered
    assert "US-001" in rendered
    assert "BL-001" in rendered
    assert "## Traceability" in rendered
    assert "OPENAI_API_KEY" not in rendered
    assert "hidden reasoning" not in rendered


def test_quality_errors_make_package_needs_review() -> None:
    package = make_assembled_package()
    package.quality_report.findings.append(
        QualityFinding(
            code="fixture",
            severity=FindingSeverity.ERROR,
            message="Needs review.",
        )
    )
    package.generation_status = GenerationStatus.NEEDS_REVIEW

    assert package.quality_report.has_errors
