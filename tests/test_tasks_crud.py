"""Tests for Task CRUD operations."""

import pytest
from uuid import UUID


@pytest.mark.asyncio
async def test_create_task(client):
    """Test creating a task."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "Test description",
            "status": "todo",
            "priority": "medium",
            "skill_type": "runbook",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test description"
    assert data["status"] == "todo"
    assert data["priority"] == "medium"
    assert data["skill_type"] == "runbook"
    assert "id" in data
    assert UUID(data["id"])  # Valid UUID


@pytest.mark.asyncio
async def test_list_tasks(client):
    """Test listing tasks."""
    # Create two tasks
    await client.post("/tasks", json={"title": "Task 1"})
    await client.post("/tasks", json={"title": "Task 2"})

    response = await client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_task(client):
    """Test getting a single task."""
    # Create task
    create_response = await client.post("/tasks", json={"title": "Get Task"})
    task_id = create_response.json()["id"]

    # Get task
    response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Get Task"
    assert data["id"] == task_id


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    """Test getting a non-existent task."""
    response = await client.get("/tasks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task(client):
    """Test updating a task."""
    # Create task
    create_response = await client.post("/tasks", json={"title": "Original Title"})
    task_id = create_response.json()["id"]

    # Update task
    response = await client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Title", "status": "in_progress"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "in_progress"


@pytest.mark.asyncio
async def test_delete_task(client):
    """Test deleting a task."""
    # Create task
    create_response = await client.post("/tasks", json={"title": "Delete Me"})
    task_id = create_response.json()["id"]

    # Delete task
    response = await client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = await client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_not_found(client):
    """Test deleting a non-existent task."""
    response = await client.delete("/tasks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
