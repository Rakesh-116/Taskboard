"""Render task pages, escaping user data without a template dependency."""

from datetime import datetime
from html import escape
from pathlib import Path
from string import Template


TEMPLATE = Template((Path(__file__).parent / "templates" / "dashboard.html").read_text(encoding="utf-8"))
PAGE = Template((Path(__file__).parent / "templates" / "page.html").read_text(encoding="utf-8"))


def render_task_content(tasks: list[dict]) -> str:
    rows = []
    for task in reversed(tasks):
        status = task["status"]
        created = datetime.fromisoformat(task["created_at"]).strftime("%d %b %Y, %H:%M UTC")
        rows.append(
            f'<tr><td class="task-cell"><strong>{escape(task["title"])}</strong>'
            f'<span>{escape(task["description"] or "No description")}</span></td>'
            f'<td><span class="badge {escape(status, quote=True)}">{escape(status.replace("_", " ").title())}</span></td>'
            f'<td class="date">{escape(created)}</td>'
            f'<td><a class="view-link" href="/ui/tasks/{task["id"]}">Open #{task["id"]} &rarr;</a></td></tr>'
        )
    content = (
        '<div class="table-scroll"><table><thead><tr><th>Task</th><th>Status</th><th>Created</th><th>Details</th></tr></thead>'
        '<tbody>' + "".join(rows) + '</tbody></table></div>'
        if rows else
        '<div class="empty"><span class="empty-icon" aria-hidden="true">&#10003;</span>'
        '<h3>A fresh start.</h3><p>Create your first task to get started.</p>'
        '<a class="button primary" href="/ui/tasks/new">Create your first task &rarr;</a></div>'
    )
    return content


def render_dashboard(tasks: list[dict]) -> str:
    counts = {status: sum(task["status"] == status for task in tasks) for status in ("pending", "in_progress", "completed")}
    return TEMPLATE.substitute(total=len(tasks), **counts, task_content=render_task_content(tasks))


def render_task_list(tasks: list[dict], status: str | None = None) -> str:
    filters = []
    for value, label in ((None, "All tasks"), ("pending", "Pending"), ("in_progress", "In progress"), ("completed", "Completed")):
        href = "/ui/tasks" + (f"?status={value}" if value else "")
        count = len(tasks) if value is None else sum(task["status"] == value for task in tasks)
        current = ' aria-current="page"' if value == status else ""
        filters.append(f'<a class="filter-link" href="{href}"{current}>{label} <span>{count}</span></a>')
    selected = [task for task in tasks if status is None or task["status"] == status]
    content = render_task_content(selected)
    if status and not selected:
        content = '<div class="empty"><h3>No tasks with this status.</h3><p>Choose another filter or create a new task.</p><a class="button secondary" href="/ui/tasks">Show all tasks</a></div>'
    return render_page("Tasks", f'''
        <section class="intro"><div><p class="eyebrow">TASK WORKSPACE</p><h1>Manage your tasks.</h1><p class="subtitle">Browse tasks by status, then open one to view or edit it.</p></div><a class="button primary" href="/ui/tasks/new">+ Create a task</a></section>
        <nav class="filters" aria-label="Filter tasks by status">{''.join(filters)}</nav>
        <section class="panel"><div class="panel-head"><div><h2>Task list</h2><p>{len(selected)} task{'s' if len(selected) != 1 else ''} shown &middot; Newest first</p></div></div>{content}</section>''')


def render_page(title: str, content: str) -> str:
    return PAGE.substitute(page_title=escape(title), page_content=content)


def render_form(task: dict | None = None) -> str:
    editing = task is not None
    task = task or {"title": "", "description": None, "status": "pending"}
    title = "Edit task" if editing else "Create a task"
    endpoint = f'/tasks/{task["id"]}' if editing else "/tasks"
    cancel = f'/ui/tasks/{task["id"]}' if editing else "/ui/tasks"
    options = "".join(
        f'<option value="{status}"{" selected" if task["status"] == status else ""}>{status.replace("_", " ").title()}</option>'
        for status in ("pending", "in_progress", "completed")
    )
    return render_page(title, f'''
        <a class="breadcrumbs" href="{cancel}">&larr; Back to tasks</a>
        <section class="panel form-panel"><div class="panel-head"><div><h1>{title}</h1><p>A clear title makes the next step easier.</p></div></div>
        <div class="form-body"><div id="feedback" class="feedback" role="alert" hidden></div>
        <form id="task-form" data-endpoint="{endpoint}" data-method="{'PATCH' if editing else 'POST'}">
          <div class="field"><label for="title">Title *</label><input id="title" name="title" required maxlength="200" value="{escape(task['title'], quote=True)}" placeholder="What needs to get done?"><small>Required. Up to 200 characters.</small></div>
          <div class="field"><label for="description">Description</label><textarea id="description" name="description" maxlength="2000" placeholder="Add a little context…">{escape(task['description'] or '')}</textarea><small>Optional. Up to 2,000 characters.</small></div>
          <div class="field"><label for="status">Status</label><select id="status" name="status">{options}</select></div>
          <div class="actions"><button class="button primary" type="submit">{'Save changes' if editing else 'Create task'}</button><a class="button secondary" href="{cancel}">Cancel</a></div>
        </form></div></section>''')


def render_detail(task: dict) -> str:
    task_id = task["id"]
    return render_page(task["title"], f'''
        <a class="breadcrumbs" href="/ui/tasks">&larr; All tasks</a>
        <section class="panel form-panel"><div class="panel-head"><div><p>Task #{task_id}</p><h1 class="detail-title">{escape(task['title'])}</h1></div></div>
        <div class="form-body"><div id="feedback" class="feedback" role="alert" hidden></div>
        <div class="detail-grid"><div><div class="detail-label">Status</div><span class="badge {escape(task['status'], quote=True)}">{escape(task['status'].replace('_', ' ').title())}</span></div>
        <div><div class="detail-label">Created (UTC)</div><div>{escape(datetime.fromisoformat(task['created_at']).strftime('%d %b %Y, %H:%M'))}</div></div>
        <div class="wide"><div class="detail-label">Description</div><p class="description">{escape(task['description'] or 'No description provided.')}</p></div></div>
        <div class="actions"><a class="button primary" href="/ui/tasks/{task_id}/edit">Edit task</a><button class="button danger" id="delete-open" type="button">Delete task</button><a class="button secondary" href="/tasks/{task_id}">View JSON</a></div>
        </div></section>
        <dialog id="delete-dialog" aria-labelledby="delete-heading"><h2 id="delete-heading">Delete this task?</h2><p>This will permanently remove the task. This action cannot be undone.</p><div class="actions"><button id="delete-confirm" class="button danger" data-endpoint="/tasks/{task_id}" type="button">Delete task</button><button id="delete-cancel" class="button secondary" type="button">Keep task</button></div></dialog>''')


def render_not_found() -> str:
    return render_page("Task not found", '<section class="panel empty"><h1>Task not found</h1><p>This task may have been deleted, or the link may be incorrect.</p><a class="button primary" href="/ui/tasks">Back to tasks</a></section>')
