"""Skill execution service."""

from typing import Any

from app.models.task import SkillType
from app.skills.reused import generate_incident_update, generate_runbook, generate_fcr_content
from app.skills.task_prioritizer import prioritize_tasks
from app.skills.daily_status_summary import generate_daily_summary


def execute_skill(skill_type: SkillType, input_payload: dict[str, Any]) -> dict[str, Any]:
    """Execute a skill based on type and return the output.

    Args:
        skill_type: The type of skill to execute
        input_payload: Input data for the skill

    Returns:
        Dictionary with skill output
    """
    output = ""

    if skill_type == SkillType.INCIDENT:
        output = generate_incident_update(
            incident_title=input_payload.get("incident_title", ""),
            impact_summary=input_payload.get("impact_summary", ""),
            audience=input_payload.get("audience", "manager"),
            severity=input_payload.get("severity", "P2"),
            current_status=input_payload.get("current_status", "investigating"),
            next_update_time=input_payload.get("next_update_time"),
            checks_done=input_payload.get("checks_done", []),
            evidence=input_payload.get("evidence", []),
        )

    elif skill_type == SkillType.RUNBOOK:
        output = generate_runbook(
            domain=input_payload.get("domain", "firewall"),
            symptom_category=input_payload.get("symptom_category", "high_cpu"),
            access_mode=input_payload.get("access_mode", "gui_only"),
            environment=input_payload.get("environment", "prod"),
        )

    elif skill_type == SkillType.FCR:
        output = generate_fcr_content(
            purpose=input_payload.get("purpose", ""),
            change_type=input_payload.get("change_type", "firewall_rule"),
            rule_count=input_payload.get("rule_count", "single"),
            direction=input_payload.get("direction", "inbound"),
            risk_level=input_payload.get("risk_level", "low"),
            environment=input_payload.get("environment", "prod"),
        )

    elif skill_type == SkillType.PRIORITIZER:
        tasks = input_payload.get("tasks", [])
        output = prioritize_tasks(tasks)

    elif skill_type == SkillType.DAILY_SUMMARY:
        tasks = input_payload.get("tasks", [])
        summary_date = input_payload.get("date")
        team_name = input_payload.get("team_name", "Network Operations")
        output = generate_daily_summary(tasks, summary_date, team_name)

    else:
        output = f"Unknown skill type: {skill_type}"

    return {
        "skill_type": skill_type.value,
        "output": output,
    }
