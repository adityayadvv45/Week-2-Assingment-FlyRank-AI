from typing import Optional
from pydantic import BaseModel


class Task(BaseModel):
    """The shape every repository returns, regardless of storage backend."""
    id: int
    title: str
    done: bool


class TaskCreate(BaseModel):
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
