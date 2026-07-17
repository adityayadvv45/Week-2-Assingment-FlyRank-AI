import os
from fastapi import FastAPI, HTTPException
from app.models import TaskCreate, TaskUpdate
from app.service import TaskService, TaskNotFound, InvalidTitle
from app.memory_repo import InMemoryTaskRepository

app = FastAPI(title="Task API", version="2.0")

# ---- Wiring: the ONLY place that knows which storage backend is in use ----
# STORAGE=postgres (default when DATABASE_URL is set) or STORAGE=memory.
# Swapping backends never touches service.py or the routes below.
_storage = os.environ.get("STORAGE", "postgres" if os.environ.get("DATABASE_URL") else "memory")

if _storage == "postgres":
    from app.postgres_repo import PostgresTaskRepository
    repository = PostgresTaskRepository()
else:
    repository = InMemoryTaskRepository()

service = TaskService(repository)


# ---- Stage 1: root & health ----
@app.get("/", summary="API info")
def root():
    return {
        "name": "Task API",
        "version": "2.0",
        "storage": _storage,
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


# ---- Stage 2: read ----
@app.get("/tasks", summary="List all tasks")
def list_tasks(done: bool | None = None, search: str | None = None):
    return service.list_tasks(done=done, search=search)


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    try:
        return service.get_task(task_id)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---- Stage 3: create ----
@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(body: TaskCreate):
    try:
        return service.create_task(body.title)
    except InvalidTitle as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- Stage 4: update & delete ----
@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, body: TaskUpdate):
    try:
        return service.update_task(task_id, body.title, body.done)
    except InvalidTitle as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TaskNotFound:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    try:
        service.delete_task(task_id)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---- Optional extras ----
@app.get("/stats", summary="Task stats")
def stats():
    return service.stats()


@app.post("/reset", summary="Reset to example tasks")
def reset():
    service.reset()
    return {"status": "reset"}
