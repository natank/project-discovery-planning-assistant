"""Human-readable discovery-package rendering."""

from project_discovery_assistant.models import (
    Certainty,
    DiscoveryPackage,
    QuestionStatus,
)


def render_package(package: DiscoveryPackage) -> str:
    """Render a validated package without provider or runtime configuration."""
    lines = [
        f"# Discovery Package — {package.project_id}",
        "",
        f"- **Version:** {package.version}",
        f"- **Generation status:** {package.generation_status.value}",
        f"- **Review status:** {package.status.value}",
        "",
        "## Project input",
        "",
        f"**Idea:** {package.context.idea}",
        f"**Target user:** {package.context.target_user or 'Unknown'}",
        f"**Desired outcome:** {package.context.desired_outcome or 'Unknown'}",
        "",
        "### Constraints",
        "",
        *_bullets(package.context.constraints, "None recorded."),
        "",
        "### Provided evidence",
        "",
        *(
            _claim_line(claim.text, claim.certainty)
            for claim in package.context.provided_facts
        ),
        *(
            _bullets([], "No evidence supplied.")
            if not package.context.provided_facts
            else []
        ),
        "",
        "## Discovery summary",
        "",
        f"**Problem:** {package.summary.problem_statement}",
        "",
        "### Target users",
        "",
        *_bullets(package.summary.target_users, "None recorded."),
        "",
        "### Needs and outcomes",
        "",
        *_bullets(package.summary.needs, "No needs recorded."),
        *_bullets(package.summary.outcomes, "No outcomes recorded."),
        "",
        "### Claims",
        "",
        *(_claim_line(claim.text, claim.certainty) for claim in package.summary.claims),
        *(
            _bullets([], "No additional claims recorded.")
            if not package.summary.claims
            else []
        ),
        "",
        "## Assumptions and open questions",
        "",
        *_assumption_lines(package),
        "",
        "## Risks",
        "",
        *(
            f"- **{risk.id} ({risk.category}):** {risk.description} "
            f"(impact: {risk.impact}; certainty: {risk.certainty.value}; "
            f"mitigation: {risk.validation_or_mitigation})"
            for risk in package.risks
        ),
        *(_bullets([], "No risks recorded.") if not package.risks else []),
        "",
        "## MVP scope",
        "",
        f"**Outcome:** {package.scope.mvp_outcome}",
        "",
        "### Included capabilities",
        "",
        *_bullets(package.scope.included_capabilities, "None recorded."),
        "",
        "### Non-goals",
        "",
        *_bullets(package.scope.non_goals, "None recorded."),
        "",
        "### Follow-ons and trade-offs",
        "",
        *_bullets(package.scope.follow_ons, "No follow-ons recorded."),
        *_bullets(package.scope.trade_offs, "No trade-offs recorded."),
        "",
        "## Requirements",
        "",
        *(
            f"- **{requirement.id} [{requirement.priority.value}]:** "
            f"{requirement.statement} (serves: "
            f"{requirement.target_user_or_outcome})"
            for requirement in package.requirements
        ),
        "",
        "## User stories and acceptance criteria",
        "",
        *(
            f"### {story.id} [{story.priority.value}] — {story.capability}\n\n"
            f"**As a {story.target_user_role}, I want to {story.capability.lower()} "
            f"so that {story.value.lower()}.**\n\n"
            f"Requirements: {', '.join(story.requirement_ids)}\n\n"
            "Acceptance criteria:\n\n"
            + "\n".join(f"- {criterion}" for criterion in story.acceptance_criteria)
            for story in package.stories
        ),
        "",
        "## Delivery backlog",
        "",
        *(
            f"- **{item.id} [{item.priority.value}] — {item.title}:** "
            f"{item.outcome} (stories: {', '.join(item.story_ids)}; "
            f"validation: {item.validation_method})"
            for item in package.backlog
        ),
        "",
        "## Traceability",
        "",
        "| Outcome | Requirements | Stories | Backlog |",
        "| --- | --- | --- | --- |",
        *(
            f"| {entry.outcome_ref} | {', '.join(entry.requirement_ids)} | "
            f"{', '.join(entry.story_ids)} | {', '.join(entry.backlog_ids)} |"
            for entry in package.traceability
        ),
        "",
        "## Quality findings",
        "",
        *(
            f"- **{finding.severity.value}:** {finding.message} "
            f"({', '.join(finding.artifact_refs) or 'package'})"
            for finding in package.quality_report.findings
        ),
        *(
            _bullets([], "No quality findings.")
            if not package.quality_report.findings
            else []
        ),
        "",
    ]
    return "\n".join(lines)


def _bullets(items: list[str], empty_message: str) -> list[str]:
    return [f"- {item}" for item in items] or [f"- {empty_message}"]


def _claim_line(text: str, certainty: Certainty) -> str:
    return f"- **{certainty.value}:** {text}"


def _assumption_lines(package: DiscoveryPackage) -> list[str]:
    lines: list[str] = []
    for claim in package.summary.claims:
        if claim.certainty in {Certainty.ASSUMPTION, Certainty.OPEN_QUESTION}:
            lines.append(_claim_line(claim.text, claim.certainty))
    for question in package.context.clarification_questions:
        if question.status in {QuestionStatus.DEFERRED, QuestionStatus.SKIPPED}:
            lines.append(
                f"- **open_question:** {question.id} — {question.question} "
                f"({question.status.value})"
            )
    return lines or ["- None recorded."]
