"""One-command demo for Task Management API.

Run with: python -m app.demo
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv


def print_header():
    """Print demo header."""
    print()
    print("=" * 60)
    print("  TASK MANAGEMENT API - DEMO")
    print("  AI-400 Class-1 Project")
    print("=" * 60)
    print()


def print_section(title: str):
    """Print section header."""
    print()
    print(f">>> {title}")
    print("-" * 40)


def print_success(msg: str):
    """Print success message."""
    print(f"[OK] {msg}")


def print_output(output: str, max_lines: int = 25):
    """Print skill output with line limit."""
    lines = output.split("\n")
    for line in lines[:max_lines]:
        print(f"    {line}")
    if len(lines) > max_lines:
        print(f"    ... ({len(lines) - max_lines} more lines)")


async def run_demo():
    """Run the demo flow."""
    print_header()

    # Step 1: Load environment
    print_section("Step 1: Loading Environment")
    load_dotenv()

    import os
    db_url = os.getenv("NEON_DATABASE_URL")
    if not db_url:
        print("[ERROR] NEON_DATABASE_URL not found in environment.")
        print("        Create a .env file with your Neon database URL.")
        print("        Example: NEON_DATABASE_URL='postgresql+asyncpg://user:pass@host/db?sslmode=require'")
        sys.exit(1)

    # Mask password in output
    masked_url = db_url.split("@")[1] if "@" in db_url else "configured"
    print_success(f"Database URL loaded (host: {masked_url.split('/')[0]})")

    # Step 2: Initialize database
    print_section("Step 2: Initializing Database")

    from app.core.database import init_db, async_session
    await init_db()
    print_success("Database tables created/verified")

    # Step 3: Create sample task
    print_section("Step 3: Creating Sample Task")

    from app.models.task import Task, SkillType, TaskStatus, TaskPriority
    from uuid import uuid4
    from datetime import datetime, timezone

    sample_input = {
        "domain": "firewall",
        "symptom_category": "high_cpu",
        "access_mode": "gui_only",
        "environment": "prod",
    }

    task = Task(
        id=uuid4(),
        title="Troubleshoot Firewall High CPU",
        description="Production firewall showing elevated CPU usage",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        skill_type=SkillType.RUNBOOK,
        input_payload=sample_input,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async with async_session() as session:
        session.add(task)
        await session.commit()
        await session.refresh(task)

    print_success(f"Task created")
    print(f"    ID: {task.id}")
    print(f"    Title: {task.title}")
    print(f"    Status: {task.status.value}")
    print(f"    Priority: {task.priority.value}")
    print(f"    Skill Type: {task.skill_type.value}")

    # Step 4: Execute skill
    print_section("Step 4: Executing RUNBOOK Skill")

    from app.services.skill_service import execute_skill

    result = execute_skill(task.skill_type, sample_input)
    print_success(f"Skill executed: {result['skill_type']}")
    print()
    print("    OUTPUT PREVIEW:")
    print("    " + "-" * 36)
    print_output(result["output"])

    # Step 5: Store output
    print_section("Step 5: Storing Output in Task")

    async with async_session() as session:
        task_db = await session.get(Task, task.id)
        task_db.output_payload = result
        task_db.updated_at = datetime.now(timezone.utc)
        await session.commit()

    print_success(f"Output saved to task {task.id}")

    # Summary
    print()
    print("=" * 60)
    print("  DEMO COMPLETE")
    print("=" * 60)
    print()
    print("  What happened:")
    print("  1. Connected to Neon PostgreSQL database")
    print("  2. Created a task for firewall troubleshooting")
    print("  3. Executed the RUNBOOK skill with safe diagnostic steps")
    print("  4. Stored the output back in the database")
    print()
    print("  Next steps:")
    print("  - Run the API: make run")
    print("  - Open Swagger docs: http://localhost:8000/docs")
    print("  - Run tests: make test")
    print()


def main():
    """Main entry point."""
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
