"""FastAPI routes and lifespan; run with python -m uvicorn app.main:app."""

from contextlib import asynccontextmanager
import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path as PathParameter, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.database import TaskStore
from app.dashboard import render_dashboard, render_detail, render_form, render_not_found, render_task_list
from app.models import Task, TaskCreate, TaskUpdate, TaskStatus


TaskId = Annotated[int, PathParameter(gt=0, le=9223372036854775807)]
DEFAULT_DATABASE = Path(__file__).resolve().parents[1] / "data" / "tasks.db"


def create_app(database_path: str | Path | None = None) -> FastAPI:
    path = Path(database_path if database_path is not None else os.environ.get("TASK_DB_PATH", DEFAULT_DATABASE))
    store = TaskStore(path)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        store.initialize()
        yield

    application = FastAPI(title="Task Management API", version="1.0.0", lifespan=lifespan)
    application.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

    @application.get("/", response_class=HTMLResponse, include_in_schema=False)
    def dashboard():
        return render_dashboard(store.list())

    @application.get("/ui/tasks", response_class=HTMLResponse, include_in_schema=False)
    def task_list_page(status: TaskStatus | None = None):
        return render_task_list(store.list(), status.value if status else None)

    @application.get("/ui/tasks/new", response_class=HTMLResponse, include_in_schema=False)
    def new_task_page():
        return render_form()

    @application.get("/ui/tasks/{task_id}", response_class=HTMLResponse, include_in_schema=False)
    def task_page(task_id: TaskId):
        task = store.get(task_id)
        if task is None:
            return HTMLResponse(render_not_found(), status_code=404)
        return render_detail(task)

    @application.get("/ui/tasks/{task_id}/edit", response_class=HTMLResponse, include_in_schema=False)
    def edit_task_page(task_id: TaskId):
        task = store.get(task_id)
        if task is None:
            return HTMLResponse(render_not_found(), status_code=404)
        return render_form(task)

    @application.post("/tasks", response_model=Task, status_code=201)
    def create_task(task: TaskCreate, response: Response):
        result = store.create(task)
        response.headers["Location"] = f"/tasks/{result['id']}"
        return result

    @application.get("/tasks", response_model=list[Task])
    def list_tasks():
        return store.list()

    @application.get("/tasks/{task_id}", response_model=Task)
    def get_task(task_id: TaskId):
        result = store.get(task_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return result

    @application.patch("/tasks/{task_id}", response_model=Task)
    def update_task(task_id: TaskId, task: TaskUpdate):
        result = store.update(task_id, task)
        if result is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return result

    @application.delete("/tasks/{task_id}", status_code=204)
    def delete_task(task_id: TaskId):
        if not store.delete(task_id):
            raise HTTPException(status_code=404, detail="Task not found")
        return Response(status_code=204)

    return application


app = create_app()
