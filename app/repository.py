from abc import ABC, abstractmethod
from typing import List, Optional
from app.models import Task


class TaskRepository(ABC):
    """
    Storage-agnostic contract. main.py and service.py only ever talk to this
    interface. InMemoryTaskRepository and PostgresTaskRepository are two
    interchangeable implementations of it.
    """

    @abstractmethod
    def list(self, done: Optional[bool] = None, search: Optional[str] = None) -> List[Task]:
        ...

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        ...

    @abstractmethod
    def create(self, title: str) -> Task:
        ...

    @abstractmethod
    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[Task]:
        ...

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        ...

    @abstractmethod
    def reset(self) -> None:
        ...
