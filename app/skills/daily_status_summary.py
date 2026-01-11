"""Daily Status Summary - Generate manager-ready daily task summaries.

This workflow skill helps network engineers communicate progress by:
- Grouping tasks by status
- Creating clear, manager-friendly output
- Highlighting blockers and next actions

Input: List of tasks + date (default today)
Output: Manager-ready summary (Completed / In Progress / Blocked / Next)
"""

from dataclasses import dataclass
from datetime import datetime, timezone, date
from typing import Any


def get_current_timestamp() -> str:
    """Get current timestamp in standard format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def get_today() -> str:
    """Get today's date formatted."""
    return date.today().strftime("%Y-%m-%d")


@dataclass
class TaskItem:
    """Single task for summary."""

    title: str
    status: str = "todo"
    priority: str = "medium"
    description: str | None = None
    blocked: bool = False
    blocker_reason: str | None = None


def generate_daily_summary(
    tasks: list[dict[str, Any]],
    summary_date: str | None = None,
    team_name: str = "Network Operations",
) -> str:
    """Generate a daily status summary.

    Args:
        tasks: List of task dicts with title, status, priority, etc.
        summary_date: Date for summary (default: today)
        team_name: Team name for header

    Returns:
        Formatted daily summary string
    """
    if summary_date is None:
        summary_date = get_today()

    # Convert to TaskItem objects
    task_items = []
    for t in tasks:
        task_items.append(TaskItem(
            title=t.get("title", "Untitled"),
            status=t.get("status", "todo"),
            priority=t.get("priority", "medium"),
            description=t.get("description"),
            blocked=t.get("blocked", False),
            blocker_reason=t.get("blocker_reason"),
        ))

    # Group by status
    completed = [t for t in task_items if t.status.lower() == "done"]
    in_progress = [t for t in task_items if t.status.lower() == "in_progress"]
    blocked = [t for t in task_items if t.blocked]
    todo = [t for t in task_items if t.status.lower() == "todo" and not t.blocked]

    # High priority items for "Next" section
    high_priority_todo = [t for t in todo if t.priority.lower() == "high"]
    next_up = high_priority_todo[:3] if high_priority_todo else todo[:3]

    # Build output
    lines = [
        f"# Daily Status Summary - {team_name}",
        "",
        f"**Date:** {summary_date}",
        f"**Generated:** {get_current_timestamp()}",
        "",
        "---",
        "",
    ]

    # Completed section
    lines.append("## Completed")
    if completed:
        for task in completed:
            lines.append(f"- {task.title}")
    else:
        lines.append("- _No tasks completed_")
    lines.append("")

    # In Progress section
    lines.append("## In Progress")
    if in_progress:
        for task in in_progress:
            priority_tag = f"[{task.priority.upper()}]" if task.priority.lower() == "high" else ""
            lines.append(f"- {task.title} {priority_tag}".strip())
    else:
        lines.append("- _No tasks in progress_")
    lines.append("")

    # Blocked section
    lines.append("## Blocked")
    if blocked:
        for task in blocked:
            reason = f" - {task.blocker_reason}" if task.blocker_reason else ""
            lines.append(f"- {task.title}{reason}")
    else:
        lines.append("- _No blockers_")
    lines.append("")

    # Next section
    lines.append("## Next Up")
    if next_up:
        for task in next_up:
            priority_tag = f"[{task.priority.upper()}]" if task.priority.lower() == "high" else ""
            lines.append(f"- {task.title} {priority_tag}".strip())
    else:
        lines.append("- _No pending tasks_")
    lines.append("")

    # Summary stats
    lines.extend([
        "---",
        "",
        "## Quick Stats",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| Completed | {len(completed)} |",
        f"| In Progress | {len(in_progress)} |",
        f"| Blocked | {len(blocked)} |",
        f"| To Do | {len(todo)} |",
        f"| **Total** | **{len(task_items)}** |",
    ])

    return "\n".join(lines)


def generate_from_dict(data: dict[str, Any]) -> str:
    """Generate daily summary from dictionary input."""
    tasks = data.get("tasks", [])
    summary_date = data.get("date")
    team_name = data.get("team_name", "Network Operations")
    return generate_daily_summary(tasks, summary_date, team_name)
