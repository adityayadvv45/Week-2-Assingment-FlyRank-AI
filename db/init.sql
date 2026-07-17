-- Runs automatically the first time the Postgres container starts
-- (mounted into /docker-entrypoint-initdb.d/ — see docker-compose.yml).

CREATE TABLE IF NOT EXISTS tasks (
    id    SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done  BOOLEAN NOT NULL DEFAULT false
);

INSERT INTO tasks (title, done) VALUES
    ('Buy milk', false),
    ('Write README', false),
    ('Walk the dog', true);
