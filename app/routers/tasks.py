"""Tasks CRUD router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.task import Task, TaskCreate, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
) -> Task:
    """Create a new task."""
    return await task_service.create_task(session, task_data)


@router.get("", response_model=list[Task])
async def list_tasks(
    session: AsyncSession = Depends(get_session),
) -> list[Task]:
    """List all tasks."""
    return await task_service.get_tasks(session)


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Task:
    """Get a task by ID."""
    task = await task_service.get_task(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
) -> Task:
    """Update a task."""
    task = await task_service.update_task(session, task_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a task."""
    deleted = await task_service.delete_task(session, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
