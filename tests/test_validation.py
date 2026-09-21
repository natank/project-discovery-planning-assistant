"""Tests for identifiers and package-quality validation."""

from copy import deepcopy

import pytest

from project_discovery_assistant.models import DiscoveryPackage
from project_discovery_assistant.validation import (
    IdentifierAllocator,
    PackageValidationError,
    ensure_package_valid,
    validate_package,
)
from tests.test_models import make_package


def test_identifier_allocator_continues_existing_sequence() -> None:
    allocator = IdentifierAllocator("REQ", ["REQ-001", "REQ-007", "other"])

    assert allocator.allocate() == "REQ-008"
    assert allocator.allocate() == "REQ-009"


def test_valid_package_has_no_findings() -> None:
    report = validate_package(make_package())

    assert report.findings == []
    ensure_package_valid(make_package())


def test_broken_story_reference_is_an_error() -> None:
    package = make_package()
    package.stories[0].requirement_ids = ["REQ-999"]

    report = validate_package(package)

    assert any(finding.code == "story-requirement-link" for finding in report.findings)
    with pytest.raises(PackageValidationError):
        ensure_package_valid(package)


def test_broken_backlog_reference_is_an_error() -> None:
    package = make_package()
    package.backlog[0].story_ids = ["US-999"]

    report = validate_package(package)

    assert any(finding.code == "backlog-story-link" for finding in report.findings)


def test_duplicate_ids_are_rejected() -> None:
    package = make_package()
    duplicate_story = deepcopy(package.stories[0])
    package.stories.append(duplicate_story)

    report = validate_package(package)

    assert any(finding.code == "duplicate-id" for finding in report.findings)


def test_package_json_remains_a_discovery_package() -> None:
    package = make_package()

    assert isinstance(
        DiscoveryPackage.model_validate_json(package.model_dump_json()),
        DiscoveryPackage,
    )
