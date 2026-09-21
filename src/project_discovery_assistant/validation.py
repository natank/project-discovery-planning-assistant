"""Package validation and deterministic artifact identifier allocation."""

from collections.abc import Iterable
from re import fullmatch
from typing import Protocol

from project_discovery_assistant.models import (
    BacklogItem,
    DiscoveryPackage,
    FindingSeverity,
    QualityFinding,
    QualityReport,
)


class PackageValidationError(ValueError):
    """Raised when a package cannot be accepted."""


class Identified(Protocol):
    """Structural type for artifacts with stable identifiers."""

    id: str


class IdentifierAllocator:
    """Allocate stable, sequential identifiers for one artifact collection."""

    def __init__(self, prefix: str, existing_ids: Iterable[str] = ()) -> None:
        self.prefix = prefix
        self.next_number = self._next_number(existing_ids)

    def allocate(self) -> str:
        """Return the next identifier and advance the allocator."""
        identifier = f"{self.prefix}-{self.next_number:03d}"
        self.next_number += 1
        return identifier

    def _next_number(self, existing_ids: Iterable[str]) -> int:
        numbers = [
            int(match.group(1))
            for identifier in existing_ids
            if (match := fullmatch(rf"{self.prefix}-(\d+)", identifier))
        ]
        return max(numbers, default=0) + 1


def validate_package(package: DiscoveryPackage) -> QualityReport:
    """Return structural and traceability findings for a package."""
    findings: list[QualityFinding] = []
    requirement_ids = _unique_ids(package.requirements, "requirements", findings)
    story_ids = _unique_ids(package.stories, "stories", findings)
    backlog_ids = _unique_ids(package.backlog, "backlog", findings)

    for story in package.stories:
        _require_references(
            findings,
            owner=story.id,
            references=story.requirement_ids,
            valid_ids=requirement_ids,
            code="story-requirement-link",
        )
        if not story.acceptance_criteria:
            findings.append(
                QualityFinding(
                    code="missing-acceptance-criteria",
                    severity=FindingSeverity.ERROR,
                    message="Every story must have acceptance criteria.",
                    artifact_refs=[story.id],
                )
            )

    for item in package.backlog:
        _require_references(
            findings,
            owner=item.id,
            references=item.story_ids,
            valid_ids=story_ids,
            code="backlog-story-link",
        )
        _validate_backlog_item(item, findings)

    for entry in package.traceability:
        _require_references(
            findings,
            owner=entry.outcome_ref,
            references=entry.requirement_ids,
            valid_ids=requirement_ids,
            code="traceability-requirement-link",
        )
        _require_references(
            findings,
            owner=entry.outcome_ref,
            references=entry.story_ids,
            valid_ids=story_ids,
            code="traceability-story-link",
        )
        _require_references(
            findings,
            owner=entry.outcome_ref,
            references=entry.backlog_ids,
            valid_ids=backlog_ids,
            code="traceability-backlog-link",
        )

    return QualityReport(findings=findings)


def ensure_package_valid(package: DiscoveryPackage) -> None:
    """Raise when a package contains an acceptance-blocking finding."""
    report = validate_package(package)
    if report.has_errors:
        messages = "; ".join(finding.message for finding in report.findings)
        raise PackageValidationError(messages)


def _unique_ids(
    artifacts: Iterable[Identified],
    artifact_type: str,
    findings: list[QualityFinding],
) -> set[str]:
    all_ids = [artifact.id for artifact in artifacts]
    identifiers = set(all_ids)
    duplicates = {identifier for identifier in all_ids if all_ids.count(identifier) > 1}
    for identifier in sorted(duplicates):
        findings.append(
            QualityFinding(
                code="duplicate-id",
                severity=FindingSeverity.ERROR,
                message=f"Duplicate {artifact_type} identifier: {identifier}.",
                artifact_refs=[identifier],
            )
        )
    return identifiers


def _require_references(
    findings: list[QualityFinding],
    *,
    owner: str,
    references: Iterable[str],
    valid_ids: set[str],
    code: str,
) -> None:
    missing = sorted(set(references) - valid_ids)
    if missing:
        findings.append(
            QualityFinding(
                code=code,
                severity=FindingSeverity.ERROR,
                message=(
                    f"{owner} references missing identifiers: {', '.join(missing)}."
                ),
                artifact_refs=[owner, *missing],
            )
        )


def _validate_backlog_item(
    item: BacklogItem,
    findings: list[QualityFinding],
) -> None:
    if not item.outcome:
        findings.append(
            QualityFinding(
                code="missing-backlog-outcome",
                severity=FindingSeverity.ERROR,
                message="Every backlog item must have an outcome.",
                artifact_refs=[item.id],
            )
        )
    if not item.validation_method:
        findings.append(
            QualityFinding(
                code="missing-validation-method",
                severity=FindingSeverity.ERROR,
                message="Every backlog item must have a validation method.",
                artifact_refs=[item.id],
            )
        )
