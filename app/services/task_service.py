"""Task CRUD service."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskCreate, TaskUpdate


async def create_task(session: AsyncSession, task_data: TaskCreate) -> Task:
    """Create a new task."""
    task = Task.model_validate(task_data)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_tasks(session: AsyncSession) -> list[Task]:
    """Get all tasks."""
    result = await session.execute(select(Task).order_by(Task.created_at.desc()))
    return list(result.scalars().all())


async def get_task(session: AsyncSession, task_id: UUID) -> Task | None:
    """Get a task by ID."""
    return await session.get(Task, task_id)


async def update_task(
    session: AsyncSession, task_id: UUID, task_data: TaskUpdate
) -> Task | None:
    """Update a task."""
    task = await session.get(Task, task_id)
    if not task:
        return None

    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task_id: UUID) -> bool:
    """Delete a task."""
    task = await session.get(Task, task_id)
    if not task:
        return False

    await session.delete(task)
    await session.commit()
    return True
