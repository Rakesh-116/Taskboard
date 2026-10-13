from datetime import datetime

from fastapi.testclient import TestClient
import pytest

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "tasks.db")) as test_client:
        yield test_client


def test_complete_task_lifecycle(client):
    assert client.get("/tasks").json() == []
    response = client.post("/tasks", json={"title": "  Prepare assessment  ", "description": "Day 04"})
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Prepare assessment"
    assert task["description"] == "Day 04"
    assert task["status"] == "pending"
    assert task["id"] > 0
    assert datetime.fromisoformat(task["created_at"]).utcoffset().total_seconds() == 0
    url = f"/tasks/{task['id']}"
    assert response.headers["location"] == url
    assert client.get("/tasks").json() == [task]
    assert client.get(url).json() == task

    response = client.patch(url, json={"title": "Submit assessment", "status": "completed"})
    assert response.status_code == 200
    changed = response.json()
    assert changed == {**task, "title": "Submit assessment", "status": "completed"}
    assert client.get(url).json() == changed
    assert client.patch(url, json={"description": None}).json()["description"] is None
    response = client.delete(url)
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(url).status_code == 404
    assert client.get("/tasks").json() == []


@pytest.mark.parametrize("payload", [
    {}, {"title": ""}, {"title": " \t\n "}, {"title": None}, {"title": 123},
    {"title": "x" * 201}, {"title": "Valid", "description": "x" * 2001},
    {"title": "Valid", "status": "done"}, {"title": "Valid", "status": None},
    {"title": "Valid", "id": 99}, {"title": "Valid", "created_at": "2026-01-01"},
])
def test_invalid_create_does_not_write(client, payload):
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"]
    assert client.get("/tasks").json() == []


@pytest.mark.parametrize("status", ["pending", "in_progress", "completed"])
def test_all_statuses_and_optional_description(client, status):
    response = client.post("/tasks", json={"title": "Task", "status": status})
    assert response.status_code == 201
    assert response.json()["status"] == status
    assert response.json()["description"] is None


@pytest.mark.parametrize("payload", [
    {}, {"title": ""}, {"title": "   "}, {"title": None}, {"status": None},
    {"status": "done"}, {"description": "x" * 2001}, {"id": 99},
])
def test_invalid_update_preserves_existing_task(client, payload):
    task = client.post("/tasks", json={"title": "Keep me"}).json()
    url = f"/tasks/{task['id']}"
    response = client.patch(url, json=payload)
    assert response.status_code == 422
    assert response.json()["detail"]
    assert client.get(url).json() == task


@pytest.mark.parametrize("method,payload", [("get", None), ("patch", {"status": "completed"}), ("delete", None)])
def test_nonexistent_id(client, method, payload):
    kwargs = {"json": payload} if payload is not None else {}
    response = getattr(client, method)("/tasks/999", **kwargs)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


@pytest.mark.parametrize("task_id", ["0", "-1", "abc", "1.5", "9223372036854775808"])
@pytest.mark.parametrize("method,payload", [("get", None), ("patch", {"title": "Valid"}), ("delete", None)])
def test_invalid_ids(client, task_id, method, payload):
    kwargs = {"json": payload} if payload is not None else {}
    response = getattr(client, method)(f"/tasks/{task_id}", **kwargs)
    assert response.status_code == 422
    assert response.json()["detail"]


def test_persistence_across_fresh_applications(tmp_path):
    database = tmp_path / "persist.db"
    with TestClient(create_app(database)) as first:
        task = first.post("/tasks", json={"title": "Persist me"}).json()
    with TestClient(create_app(database)) as second:
        assert second.get(f"/tasks/{task['id']}").json() == task
        assert second.patch(f"/tasks/{task['id']}", json={"status": "in_progress"}).status_code == 200
    with TestClient(create_app(database)) as third:
        assert third.get(f"/tasks/{task['id']}").json()["status"] == "in_progress"
        assert third.delete(f"/tasks/{task['id']}").status_code == 204
    with TestClient(create_app(database)) as fourth:
        assert fourth.get("/tasks").json() == []


def test_parameterized_sql_and_unique_ids(client):
    title = "Robert'); DROP TABLE tasks;--"
    first = client.post("/tasks", json={"title": title}).json()
    second = client.post("/tasks", json={"title": "Another task"}).json()
    assert first["title"] == title
    assert second["id"] != first["id"]
    assert client.get("/tasks").json() == [first, second]
    assert client.delete(f"/tasks/{first['id']}").status_code == 204
    assert client.get(f"/tasks/{second['id']}").json() == second


def test_missing_request_body(client):
    assert client.post("/tasks").status_code == 422


def test_title_and_description_boundaries(client):
    response = client.post("/tasks", json={"title": "x" * 200, "description": "y" * 2000})
    assert response.status_code == 201


def test_docs_available(client):
    assert client.get("/docs").status_code == 200
    assert "/tasks/{task_id}" in client.get("/openapi.json").json()["paths"]


def test_dashboard_empty_and_saved_tasks(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "A fresh start." in response.text
    assert 'href="/docs"' in response.text
    task = client.post("/tasks", json={"title": "<script>alert(1)</script>", "description": "<b>unsafe</b>", "status": "completed"}).json()
    page = client.get("/").text
    assert "A fresh start." not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
    assert "<script>alert(1)</script>" not in page
    assert "&lt;b&gt;unsafe&lt;/b&gt;" in page
    assert 'Completed</span><strong>1</strong>' in page
    assert f'href="/ui/tasks/{task["id"]}"' in page


def test_ui_create_view_edit_delete_workflow(client):
    page = client.get("/ui/tasks/new")
    assert page.status_code == 200
    assert 'data-endpoint="/tasks" data-method="POST"' in page.text
    assert 'name="title" required maxlength="200"' in page.text
    assert 'src="/static/tasks.js"' in page.text
    task = client.post("/tasks", json={"title": 'Review "UI" <script>', "description": "</textarea><script>alert(1)</script>"}).json()
    task_id = task["id"]
    listing = client.get("/ui/tasks")
    assert listing.status_code == 200
    assert f'href="/ui/tasks/{task_id}"' in listing.text
    detail = client.get(f"/ui/tasks/{task_id}")
    assert detail.status_code == 200
    assert f'href="/ui/tasks/{task_id}/edit"' in detail.text
    assert 'id="delete-dialog"' in detail.text
    assert f'data-endpoint="/tasks/{task_id}"' in detail.text
    edit = client.get(f"/ui/tasks/{task_id}/edit")
    assert edit.status_code == 200
    assert f'data-endpoint="/tasks/{task_id}" data-method="PATCH"' in edit.text
    assert 'value="Review &quot;UI&quot; &lt;script&gt;"' in edit.text
    assert "&lt;/textarea&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in edit.text
    assert "</textarea><script>alert(1)</script>" not in edit.text
    response = client.patch(f"/tasks/{task_id}", json={"title": "Updated from form", "description": None, "status": "completed"})
    assert response.status_code == 200
    detail = client.get(f"/ui/tasks/{task_id}")
    assert "Updated from form" in detail.text
    assert "No description provided." in detail.text
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/ui/tasks/{task_id}").status_code == 404
    assert "A fresh start." in client.get("/ui/tasks").text


@pytest.mark.parametrize("suffix", ["", "/edit"])
def test_ui_missing_task_has_friendly_page(client, suffix):
    response = client.get(f"/ui/tasks/999{suffix}")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("text/html")
    assert "Task not found" in response.text
    assert 'href="/ui/tasks"' in response.text


def test_ui_assets_are_served(client):
    css = client.get("/static/styles.css")
    script = client.get("/static/tasks.js")
    assert css.status_code == 200
    assert "@media" in css.text
    assert script.status_code == 200
    assert "fetch(endpoint, options)" in script.text


def test_overview_and_tasks_are_distinct_with_status_filters(client):
    for status in ("pending", "in_progress", "completed"):
        client.post("/tasks", json={"title": f"Unique {status} task", "status": status})
    overview = client.get("/").text
    listing = client.get("/ui/tasks").text
    assert "A little clarity for your day." in overview
    assert 'href="/" aria-current="page"' in overview
    assert "Manage your tasks." in listing
    assert "A little clarity for your day." not in listing
    assert 'href="/ui/tasks" aria-current="page"' in listing
    for status in ("pending", "in_progress", "completed"):
        page = client.get(f"/ui/tasks?status={status}")
        assert page.status_code == 200
        assert f"Unique {status} task" in page.text
        for other in ("pending", "in_progress", "completed"):
            if other != status:
                assert f"Unique {other} task" not in page.text
    assert client.get("/ui/tasks?status=done").status_code == 422
    assert len(client.get("/tasks").json()) == 3
