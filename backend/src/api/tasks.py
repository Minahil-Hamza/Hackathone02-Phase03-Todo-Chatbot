"""Tasks endpoints for CRUD operations on user tasks."""

import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from src.api.deps import CurrentUser
from src.db import async_session_factory
from src.models import Task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tasks"])


class TaskResponse(BaseModel):
    """Response model for a task."""
    id: str
    title: str
    is_completed: bool
    created_at: str
    updated_at: str


class TasksListResponse(BaseModel):
    """Response model for listing tasks."""
    tasks: List[TaskResponse]
    total: int
    completed: int
    pending: int


class CreateTaskRequest(BaseModel):
    """Request model for creating a task."""
    title: str


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = None
    is_completed: Optional[bool] = None


def _task_to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        is_completed=task.is_completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.get("/tasks", response_model=TasksListResponse)
async def list_tasks(current_user: CurrentUser) -> TasksListResponse:
    """Get all tasks for the authenticated user."""
    user_id = str(current_user.id)

    async with async_session_factory() as session:
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        result = await session.execute(statement)
        tasks = result.scalars().all()

        task_responses = [_task_to_response(task) for task in tasks]
        completed_count = sum(1 for t in tasks if t.is_completed)
        total_count = len(tasks)

        return TasksListResponse(
            tasks=task_responses,
            total=total_count,
            completed=completed_count,
            pending=total_count - completed_count,
        )


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    request: CreateTaskRequest,
    current_user: CurrentUser,
) -> TaskResponse:
    """Create a new task for the authenticated user."""
    user_id = str(current_user.id)
    title = request.title.strip()

    if not title:
        raise HTTPException(status_code=400, detail="Task title cannot be empty.")

    async with async_session_factory() as session:
        task = Task(user_id=user_id, title=title)
        session.add(task)
        await session.commit()
        await session.refresh(task)

        logger.info(f"Created task {task.id} for user {user_id}")
        return _task_to_response(task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    request: UpdateTaskRequest,
    current_user: CurrentUser,
) -> TaskResponse:
    """Update a task's title and/or completion status."""
    user_id = str(current_user.id)

    async with async_session_factory() as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")

        if request.title is not None:
            task.update_title(request.title.strip())
        if request.is_completed is not None:
            if request.is_completed:
                task.mark_complete()
            else:
                task.is_completed = False
                task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return _task_to_response(task)


@router.put("/tasks/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task(
    task_id: str,
    current_user: CurrentUser,
) -> TaskResponse:
    """Toggle a task's completion status."""
    user_id = str(current_user.id)

    async with async_session_factory() as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")

        if task.is_completed:
            task.is_completed = False
        else:
            task.mark_complete()
        task.updated_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return _task_to_response(task)


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    current_user: CurrentUser,
) -> None:
    """Delete a task."""
    user_id = str(current_user.id)

    async with async_session_factory() as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")

        await session.delete(task)
        await session.commit()

        logger.info(f"Deleted task {task_id} for user {user_id}")
