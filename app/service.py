from typing import List, Optional
from app.models import Task
from app.repository import TaskRepository


class TaskNotFound(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id


class InvalidTitle(Exception):
    pass


class TaskService:
    """
    All business rules live here (validation, 404s). Never talks to a
    database directly — only to whatever TaskRepository it was given.
    This class does not change between Week 2 and Week 3.
    """

    def __init__(self, repository: TaskRepository):
        self._repo = repository

    def list_tasks(self, done: Optional[bool] = None, search: Optional[str] = None) -> List[Task]:
        return self._repo.list(done=done, search=search)

    def get_task(self, task_id: int) -> Task:
        task = self._repo.get(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def create_task(self, title: Optional[str]) -> Task:
        if not title or not title.strip():
            raise InvalidTitle("title is required and cannot be empty")
        return self._repo.create(title.strip())

    def update_task(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Task:
        if title is not None and not title.strip():
            raise InvalidTitle("title cannot be empty")
        clean_title = title.strip() if title is not None else None
        task = self._repo.update(task_id, clean_title, done)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def delete_task(self, task_id: int) -> None:
        deleted = self._repo.delete(task_id)
        if not deleted:
            raise TaskNotFound(task_id)

    def stats(self) -> dict:
        all_tasks = self._repo.list()
        total = len(all_tasks)
        done_count = sum(1 for t in all_tasks if t.done)
        return {"total": total, "done": done_count, "open": total - done_count}

    def reset(self) -> None:
        self._repo.reset()
