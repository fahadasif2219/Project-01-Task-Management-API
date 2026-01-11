"""Incident Update Composer - Generate ready-to-send incident updates from minimal input.

This skill reduces the time spent drafting incident communications by:
- Requiring only 2 typed fields (incident_title, impact_summary)
- Auto-filling all other fields with smart defaults
- Generating appropriate next steps based on status
- Creating audience-specific formatting (manager vs client)

Reused from PI-300 with imports adapted for standalone operation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# Inline helper functions (adapted from netops_skills.common)
def get_current_timestamp() -> str:
    """Get current timestamp in standard format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def format_bullet_list(items: list[str], indent: int = 0) -> str:
    """Format a list of items as markdown bullets."""
    if not items:
        return ""
    prefix = " " * indent
    return "\n".join(f"{prefix}- {item}" for item in items)


def format_numbered_list(items: list[str], start: int = 1) -> str:
    """Format a list of items as numbered list."""
    if not items:
        return ""
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, start=start))


# Inline defaults (adapted from defaults.yaml)
DEFAULTS = {
    "incident": {
        "audience": "manager",
        "severity": "P2",
        "current_status": "investigating",
        "next_steps": {
            "investigating": [
                "Continue analyzing logs and alerts",
                "Gather additional evidence",
                "Identify root cause",
            ],
            "identified": [
                "Implement fix",
                "Test in staging environment",
                "Schedule production deployment",
            ],
            "mitigating": [
                "Monitor service recovery",
                "Validate fix effectiveness",
                "Document resolution steps",
            ],
            "resolved": [
                "Complete post-incident documentation",
                "Schedule post-mortem meeting",
                "Update runbooks if needed",
            ],
        },
        "next_update_time": {
            "P1": "30 minutes",
            "P2": "1 hour",
            "P3": "2 hours",
            "P4": "4 hours",
        },
        "evidence_checklist": [
            "Screenshots of error messages/alerts",
            "Relevant log entries with timestamps",
            "Timeline of events",
        ],
    }
}


@dataclass
class IncidentInput:
    """Schema for incident update input."""

    incident_title: str
    impact_summary: str
    audience: str = "manager"
    severity: str = "P2"
    current_status: str = "investigating"
    next_update_time: str | None = None
    checks_done: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Validate required fields. Returns list of errors."""
        errors = []
        if not self.incident_title or not self.incident_title.strip():
            errors.append("incident_title is required")
        if not self.impact_summary or not self.impact_summary.strip():
            errors.append("impact_summary is required")
        return errors


def get_next_steps(status: str) -> list[str]:
    """Get auto-generated next steps based on current status."""
    next_steps_map = DEFAULTS["incident"]["next_steps"]
    return next_steps_map.get(status, ["Continue investigation"])


def get_next_update_time(severity: str) -> str:
    """Get default next update time based on severity."""
    time_map = DEFAULTS["incident"]["next_update_time"]
    return time_map.get(severity, "1 hour")


def get_evidence_checklist(has_evidence: bool) -> list[str]:
    """Get evidence checklist when no evidence provided."""
    if has_evidence:
        return []
    return DEFAULTS["incident"]["evidence_checklist"]


def render_manager_template(context: dict[str, Any]) -> str:
    """Render manager incident update template."""
    lines = [
        f"# Incident Update: {context['incident_title']}",
        "",
        f"**Severity:** {context['severity']} | **Status:** {context['current_status'].title()}",
        f"**Generated:** {context['timestamp']}",
        "",
        "## Impact Summary",
        context["impact_summary"],
        "",
    ]

    if context["has_checks"]:
        lines.extend([
            "## Diagnostic Checks Completed",
            context["checks_done_formatted"],
            "",
        ])

    if context["has_evidence"]:
        lines.extend([
            "## Evidence Collected",
            context["evidence_formatted"],
            "",
        ])
    else:
        lines.extend([
            "## Evidence To Collect",
            context["evidence_checklist_formatted"],
            "",
        ])

    lines.extend([
        "## Next Steps",
        context["next_steps_formatted"],
        "",
        f"**Next Update:** {context['next_update_time']}",
    ])

    return "\n".join(lines)


def render_client_template(context: dict[str, Any]) -> str:
    """Render client incident update template."""
    lines = [
        f"# Service Update: {context['incident_title']}",
        "",
        f"**Status:** {context['current_status'].title()}",
        f"**Updated:** {context['timestamp']}",
        "",
        "## Current Situation",
        context["impact_summary"],
        "",
        "## What We're Doing",
    ]

    for step in context["next_steps"][:2]:
        lines.append(f"- {step}")

    lines.extend([
        "",
        f"We will provide another update in {context['next_update_time']}.",
        "",
        "Thank you for your patience.",
    ])

    return "\n".join(lines)


def generate_incident_update(
    incident_title: str,
    impact_summary: str,
    audience: str = "manager",
    severity: str = "P2",
    current_status: str = "investigating",
    next_update_time: str | None = None,
    checks_done: list[str] | None = None,
    evidence: list[str] | None = None,
) -> str:
    """Generate an incident update from input parameters.

    This is the main entry point for the skill.

    Args:
        incident_title: Short title describing the incident (REQUIRED)
        impact_summary: Brief description of user/business impact (REQUIRED)
        audience: Target audience ('manager', 'client') - default: 'manager'
        severity: Incident severity (P1-P4) - default: 'P2'
        current_status: Current status - default: 'investigating'
        next_update_time: When next update will be provided (auto-filled if None)
        checks_done: List of diagnostic checks completed
        evidence: List of evidence collected

    Returns:
        Formatted incident update string for the specified audience
    """
    input_data = IncidentInput(
        incident_title=incident_title,
        impact_summary=impact_summary,
        audience=audience,
        severity=severity,
        current_status=current_status,
        next_update_time=next_update_time,
        checks_done=checks_done or [],
        evidence=evidence or [],
    )

    errors = input_data.validate()
    if errors:
        raise ValueError(f"Invalid input: {', '.join(errors)}")

    # Auto-fill next update time if not provided
    if not input_data.next_update_time:
        input_data.next_update_time = get_next_update_time(severity)

    # Auto-generate next steps
    next_steps = get_next_steps(current_status)

    # Get evidence or checklist
    has_evidence = bool(input_data.evidence)
    evidence_checklist = get_evidence_checklist(has_evidence)

    # Build context for template
    context = {
        "incident_title": input_data.incident_title,
        "impact_summary": input_data.impact_summary,
        "severity": input_data.severity,
        "current_status": input_data.current_status,
        "next_update_time": input_data.next_update_time,
        "checks_done": input_data.checks_done,
        "checks_done_formatted": format_bullet_list(input_data.checks_done),
        "evidence": input_data.evidence,
        "evidence_formatted": format_bullet_list(input_data.evidence),
        "evidence_checklist": evidence_checklist,
        "evidence_checklist_formatted": format_bullet_list(evidence_checklist),
        "next_steps": next_steps,
        "next_steps_formatted": format_numbered_list(next_steps),
        "timestamp": get_current_timestamp(),
        "has_evidence": has_evidence,
        "has_checks": bool(input_data.checks_done),
    }

    if audience == "client":
        return render_client_template(context)
    return render_manager_template(context)


def generate_from_dict(data: dict[str, Any]) -> str:
    """Generate incident update from dictionary input."""
    return generate_incident_update(
        incident_title=data.get("incident_title", ""),
        impact_summary=data.get("impact_summary", ""),
        audience=data.get("audience", "manager"),
        severity=data.get("severity", "P2"),
        current_status=data.get("current_status", "investigating"),
        next_update_time=data.get("next_update_time"),
        checks_done=data.get("checks_done", []),
        evidence=data.get("evidence", []),
    )
