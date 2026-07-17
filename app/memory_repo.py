from typing import List, Optional
from app.models import Task
from app.repository import TaskRepository

_SEED = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Write README", "done": False},
    {"id": 3, "title": "Walk the dog", "done": True},
]


class InMemoryTaskRepository(TaskRepository):
    """Original storage from Week 2 — a plain Python list. Lost on restart."""

    def __init__(self):
        self._tasks = [dict(t) for t in _SEED]
        self._next_id = 4

    def list(self, done: Optional[bool] = None, search: Optional[str] = None) -> List[Task]:
        result = self._tasks
        if done is not None:
            result = [t for t in result if t["done"] == done]
        if search is not None:
            result = [t for t in result if search.lower() in t["title"].lower()]
        return [Task(**t) for t in result]

    def get(self, task_id: int) -> Optional[Task]:
        for t in self._tasks:
            if t["id"] == task_id:
                return Task(**t)
        return None

    def create(self, title: str) -> Task:
        new_task = {"id": self._next_id, "title": title, "done": False}
        self._tasks.append(new_task)
        self._next_id += 1
        return Task(**new_task)

    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[Task]:
        for t in self._tasks:
            if t["id"] == task_id:
                if title is not None:
                    t["title"] = title
                if done is not None:
                    t["done"] = done
                return Task(**t)
        return None

    def delete(self, task_id: int) -> bool:
        for i, t in enumerate(self._tasks):
            if t["id"] == task_id:
                self._tasks.pop(i)
                return True
        return False

    def reset(self) -> None:
        self._tasks = [dict(t) for t in _SEED]
        self._next_id = 4
