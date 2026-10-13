"""Small SQLite repository with one connection per operation."""

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from app.models import TaskCreate, TaskUpdate


class TaskStore:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(str(self.path), timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 200),
                    description TEXT CHECK(description IS NULL OR length(description) <= 2000),
                    status TEXT NOT NULL CHECK(status IN ('pending', 'in_progress', 'completed')),
                    created_at TEXT NOT NULL
                )
            """)

    def create(self, task: TaskCreate):
        with self.connection() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, description, status, created_at) VALUES (?, ?, ?, ?)",
                (task.title, task.description, task.status.value, datetime.now(timezone.utc).isoformat()),
            )
            return dict(connection.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone())

    def list(self):
        with self.connection() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM tasks ORDER BY id")]

    def get(self, task_id: int):
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return dict(row) if row else None

    def update(self, task_id: int, task: TaskUpdate):
        # The only interpolated SQL identifiers come from this fixed allowlist.
        changes = task.model_dump(exclude_unset=True, mode="json")
        columns = [name for name in ("title", "description", "status") if name in changes]
        assignments = ", ".join(f"{name} = ?" for name in columns)
        with self.connection() as connection:
            cursor = connection.execute(
                f"UPDATE tasks SET {assignments} WHERE id = ?",
                (*[changes[name] for name in columns], task_id),
            )
            if cursor.rowcount == 0:
                return None
            return dict(connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())

    def delete(self, task_id: int):
        with self.connection() as connection:
            return connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,)).rowcount > 0
