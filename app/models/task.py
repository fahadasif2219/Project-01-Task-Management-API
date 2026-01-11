"""Task model for SQLModel."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, JSON


class TaskStatus(str, Enum):
    """Task status enum."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, Enum):
    """Task priority enum."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SkillType(str, Enum):
    """Skill type enum."""

    INCIDENT = "incident"
    RUNBOOK = "runbook"
    FCR = "fcr"
    DAILY_SUMMARY = "daily_summary"
    PRIORITIZER = "prioritizer"


class TaskBase(SQLModel):
    """Base task schema."""

    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    skill_type: SkillType = SkillType.RUNBOOK
    input_payload: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    output_payload: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))


class Task(TaskBase, table=True):
    """Task database model."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskCreate(TaskBase):
    """Schema for creating a task."""

    pass


class TaskUpdate(SQLModel):
    """Schema for updating a task."""

    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    skill_type: SkillType | None = None
    input_payload: dict[str, Any] | None = None
    output_payload: dict[str, Any] | None = None
