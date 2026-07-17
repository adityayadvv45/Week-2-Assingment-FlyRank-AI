import os
from typing import List, Optional
import psycopg2
import psycopg2.extras
from app.models import Task
from app.repository import TaskRepository

_SEED = [
    ("Buy milk", False),
    ("Write README", False),
    ("Walk the dog", True),
]


class PostgresTaskRepository(TaskRepository):
    """
    Same interface as InMemoryTaskRepository, backed by real Postgres.
    Data survives app restarts and container restarts because Postgres
    itself writes to a Docker volume (see docker-compose.yml).
    """

    def __init__(self, dsn: Optional[str] = None):
        self._dsn = dsn or os.environ["DATABASE_URL"]

    def _conn(self):
        conn = psycopg2.connect(self._dsn)
        conn.autocommit = True
        return conn

    def list(self, done: Optional[bool] = None, search: Optional[str] = None) -> List[Task]:
        query = "SELECT id, title, done FROM tasks WHERE 1=1"
        params: list = []
        if done is not None:
            query += " AND done = %s"
            params.append(done)
        if search is not None:
            query += " AND title ILIKE %s"
            params.append(f"%{search}%")
        query += " ORDER BY id"
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                return [Task(**row) for row in cur.fetchall()]

    def get(self, task_id: int) -> Optional[Task]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
                row = cur.fetchone()
                return Task(**row) if row else None

    def create(self, title: str) -> Task:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, false) "
                    "RETURNING id, title, done",
                    (title,),
                )
                return Task(**cur.fetchone())

    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[Task]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "UPDATE tasks SET "
                    "title = COALESCE(%s, title), "
                    "done = COALESCE(%s, done) "
                    "WHERE id = %s "
                    "RETURNING id, title, done",
                    (title, done, task_id),
                )
                row = cur.fetchone()
                return Task(**row) if row else None

    def delete(self, task_id: int) -> bool:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                return cur.rowcount > 0

    def reset(self) -> None:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE tasks RESTART IDENTITY")
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)", _SEED
                )
