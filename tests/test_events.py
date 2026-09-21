"""Tests for redacted run-event persistence."""

from datetime import UTC, datetime
from pathlib import Path

from project_discovery_assistant.models import RunEvent, RunOutcome
from project_discovery_assistant.services.project_store import ProjectStore


def make_event(message: str | None = None) -> RunEvent:
    return RunEvent(
        timestamp=datetime.now(UTC),
        project_id="demo",
        package_version=1,
        stage="validation",
        task_name="quality-check",
        outcome=RunOutcome.FAILED if message else RunOutcome.SUCCEEDED,
        duration_ms=12,
        error_category="provider" if message else None,
        error_message=message,
    )


def test_events_round_trip_as_structured_jsonl(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    event = make_event()
    store.append_event(event)

    events = store.load_events("demo")

    assert events == [event]
    assert events[0].stage == "validation"
    assert events[0].outcome == RunOutcome.SUCCEEDED


def test_event_redactions_are_not_persisted(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    event = make_event("provider failed with sentinel-secret")

    store.append_event(event, redactions=["sentinel-secret"])

    raw = (tmp_path / "projects" / "demo" / "run-events.jsonl").read_text()
    assert "sentinel-secret" not in raw
    assert "[REDACTED]" in raw
    assert store.load_events("demo")[0].error_message == (
        "provider failed with [REDACTED]"
    )


def test_missing_event_log_is_empty(tmp_path: Path) -> None:
    assert ProjectStore(tmp_path / "projects").load_events("demo") == []
