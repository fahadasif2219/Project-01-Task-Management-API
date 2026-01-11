"""Task Prioritizer - Order tasks by priority and status with reasoning.

This workflow skill helps network engineers focus on the right tasks first by:
- Sorting tasks by priority (high > medium > low) and status
- Providing brief reasoning for the ordering
- Deterministic output for consistency

Input: List of tasks with title, status, priority
Output: Ordered list with reasoning
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def get_current_timestamp() -> str:
    """Get current timestamp in standard format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# Priority weights for sorting (higher = more urgent)
PRIORITY_WEIGHT = {
    "high": 3,
    "medium": 2,
    "low": 1,
}

# Status weights (in_progress first, then todo, done last)
STATUS_WEIGHT = {
    "in_progress": 3,
    "todo": 2,
    "done": 1,
}


@dataclass
class TaskItem:
    """Single task for prioritization."""

    title: str
    status: str = "todo"
    priority: str = "medium"

    def sort_key(self) -> tuple[int, int, str]:
        """Return sort key: (priority_weight, status_weight, title)."""
        return (
            -PRIORITY_WEIGHT.get(self.priority.lower(), 1),
            -STATUS_WEIGHT.get(self.status.lower(), 1),
            self.title.lower(),
        )


def get_reasoning(task: TaskItem, position: int) -> str:
    """Generate reasoning for task position."""
    reasons = []

    if task.priority.lower() == "high":
        reasons.append("high priority")
    elif task.priority.lower() == "medium":
        reasons.append("medium priority")
    else:
        reasons.append("low priority")

    if task.status.lower() == "in_progress":
        reasons.append("already in progress")
    elif task.status.lower() == "todo":
        reasons.append("ready to start")
    else:
        reasons.append("completed")

    return ", ".join(reasons)


def prioritize_tasks(tasks: list[dict[str, str]]) -> str:
    """Prioritize a list of tasks.

    Args:
        tasks: List of task dicts with title, status, priority

    Returns:
        Formatted prioritized list with reasoning
    """
    if not tasks:
        return "No tasks to prioritize."

    # Convert to TaskItem objects
    task_items = []
    for t in tasks:
        task_items.append(TaskItem(
            title=t.get("title", "Untitled"),
            status=t.get("status", "todo"),
            priority=t.get("priority", "medium"),
        ))

    # Sort by priority and status
    sorted_tasks = sorted(task_items, key=lambda t: t.sort_key())

    # Build output
    lines = [
        "# Task Priority List",
        "",
        f"**Generated:** {get_current_timestamp()}",
        f"**Total Tasks:** {len(sorted_tasks)}",
        "",
        "---",
        "",
        "## Prioritized Order",
        "",
    ]

    # Count by status
    in_progress = sum(1 for t in sorted_tasks if t.status.lower() == "in_progress")
    todo = sum(1 for t in sorted_tasks if t.status.lower() == "todo")
    done = sum(1 for t in sorted_tasks if t.status.lower() == "done")

    for i, task in enumerate(sorted_tasks, 1):
        reasoning = get_reasoning(task, i)
        status_icon = {
            "in_progress": "[IN PROGRESS]",
            "todo": "[TODO]",
            "done": "[DONE]",
        }.get(task.status.lower(), "[TODO]")

        priority_icon = {
            "high": "(!)",
            "medium": "(-)",
            "low": "(.)",
        }.get(task.priority.lower(), "(-)")

        lines.append(f"{i}. {priority_icon} **{task.title}** {status_icon}")
        lines.append(f"   _Reason: {reasoning}_")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Summary",
        f"- In Progress: {in_progress}",
        f"- To Do: {todo}",
        f"- Completed: {done}",
        "",
        "**Focus:** Start with task #1 and work down the list.",
    ])

    return "\n".join(lines)


def generate_from_dict(data: dict[str, Any]) -> str:
    """Generate prioritized list from dictionary input."""
    tasks = data.get("tasks", [])
    return prioritize_tasks(tasks)
