# Task API

A CRUD API for managing a to-do list, built with FastAPI.
FlyRank Internship — Backend Track — Week 3 — Postgres + Docker.

Builds on Week 2's in-memory CRUD API by swapping the storage layer for
real Postgres, running the whole stack with one command, and proving data
survives a restart.

## What changed from Week 2 — honestly

Week 2's `main.py` had everything inline: routes read and wrote a global
Python list directly. There was no interface to swap behind, so before I
could "just swap storage," I had to introduce the layering the assignment
assumes already exists:

- `app/models.py` — the `Task` shape every layer agrees on
- `app/repository.py` — the `TaskRepository` interface
- `app/memory_repo.py` — Week 2's logic, moved behind that interface, unchanged in behavior
- `app/service.py` — business rules (title validation, 404s), talks only to the interface
- `app/postgres_repo.py` — **new this week**, implements the same interface against real Postgres
- `app/main.py` — routes now call `service`, not a data structure directly

**That refactor was a one-time cost.** Once it existed, going from
`InMemoryTaskRepository` to `PostgresTaskRepository` touched exactly one
line of wiring in `app/main.py`:

```python
if _storage == "postgres":
    from app.postgres_repo import PostgresTaskRepository
    repository = PostgresTaskRepository()
else:
    repository = InMemoryTaskRepository()
```

`app/service.py` and every route in `app/main.py` are byte-for-byte
unchanged by the swap. That's the thing this week was actually testing.

## Run the whole stack

```bash
cp .env.example .env      # already gitignored — safe to edit
docker compose up --build
```

This starts two containers:
- `db` — Postgres 16, with `db/init.sql` creating the `tasks` table and
  seeding it on first boot, data written to a named volume (`a2_pgdata`)
- `app` — the FastAPI service, waits for `db`'s healthcheck before starting

API: `http://localhost:8000` — Swagger: `http://localhost:8000/docs`

## Persistence proof

How I checked (redo this yourself and paste the actual terminal output /
screenshot below before submitting):

```bash
docker compose up --build -d

curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" -d '{"title":"Survive a restart"}'
curl -s http://localhost:8000/tasks

docker compose down          # NOT `down -v` — that deletes the volume
docker compose up -d

curl -s http://localhost:8000/tasks   # "Survive a restart" is still there
```

_(paste your actual output here)_

## Endpoints

| Method | Path          | Description                                       | Success | Errors    |
|--------|---------------|----------------------------------------------------|---------|-----------|
| GET    | `/`           | API info (also reports which storage is active)   | 200     | —         |
| GET    | `/health`     | Health check                                       | 200     | —         |
| GET    | `/tasks`      | List tasks (`?done=`, `?search=`)                  | 200     | —         |
| GET    | `/tasks/{id}` | Get one task                                       | 200     | 404       |
| POST   | `/tasks`      | Create a task (`{"title": "..."}`)                 | 201     | 400       |
| PUT    | `/tasks/{id}` | Update title and/or done                           | 200     | 400, 404  |
| DELETE | `/tasks/{id}` | Delete a task                                      | 204     | 404       |
| GET    | `/stats`      | Task counts                                        | 200     | —         |
| POST   | `/reset`      | Re-seed the 3 example tasks                        | 200     | —         |

## Config

Everything is driven by `.env` (gitignored; see `.env.example`):

| Variable            | Meaning                                         |
|---------------------|--------------------------------------------------|
| `POSTGRES_USER`      | db username                                     |
| `POSTGRES_PASSWORD`  | db password                                     |
| `POSTGRES_DB`        | db name                                         |
| `DATABASE_URL`       | full connection string the app uses             |
| `STORAGE`            | `memory` or `postgres` (auto-defaults to `postgres` if `DATABASE_URL` is set) |

## Running without Docker (in-memory mode, Week 2 behavior)

```bash
pip install -r requirements.txt
STORAGE=memory uvicorn app.main:app --reload
```

## Stretch goals

Not yet done: Redis in compose, `EXPLAIN ANALYZE` before/after an index.
Both are natural next additions — Redis service in `docker-compose.yml` +
a `/health/redis` ping endpoint; the index would go on `tasks.done` or
`tasks.title` once the table has enough seeded rows to matter.
