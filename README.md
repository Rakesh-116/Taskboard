# Day 04 — Task Management REST API

Assignment B addresses a small team's need to create, view, update, and delete tasks using a lightweight local service. FastAPI handles HTTP and validation; SQLite keeps tasks after restarts. This folder contains the implementation, tests, project guidance, and assessment evidence.

## Project structure

```text
Day-4_Assignment_B_Build_New_Application/
|-- app/                                  # Application package
|   |-- __init__.py
|   |-- main.py                           # App factory, startup, HTTP routes
|   |-- models.py                         # Request/response schemas and validation
|   |-- database.py                       # SQLite persistence and transactions
|   |-- dashboard.py                      # Escaped dashboard, detail, and form pages
|   |-- templates/
|   |   |-- dashboard.html                # Task list and dashboard
|   |   `-- page.html                     # Shared form/detail page layout
|   `-- static/
|       |-- styles.css                    # Shared responsive styling
|       `-- tasks.js                      # Form submission and delete actions
|-- tests/
|   `-- test_tasks.py                     # Automated behavioral API tests
|-- scripts/
|   `-- verify_http.py                    # Real HTTP and server-restart verification
|-- evidence/                             # Captured results and review artifacts
|   |-- pytest.txt
|   |-- http-verification.txt
|   |-- http-exchanges.json
|   |-- server.log
|   |-- dependency-check.txt
|   |-- source-additions.diff
|   `-- source-sha256.json
|-- data/                                 # Created at runtime; database not submitted
|   `-- tasks.db
|-- .venv/                                # Local environment; not submitted
|-- .gitignore
|-- AGENTS.md                             # Coding-agent guidance
|-- requirements.txt                      # Direct dependency ranges
|-- requirements-lock.txt                 # Exact verified dependency versions
|-- PLAN.md                               # Scope, plan, acceptance criteria
|-- README.md                             # Project explanation and usage
|-- VERIFICATION.md                       # Results, source review, limitations
|-- ENGINEERING_REFLECTION.md              # Reflection in readable text
|-- Day04_Engineering_Reflection_Completed.docx
`-- Day04_Assignment_B_Submission.zip      # Packaged local deliverables
```

Application code, tests, verification tools, and assessment evidence have separate folders. `data/` and `.venv/` are runtime/local resources excluded from the submission archive. Python and test caches are also ignored. The application modules separate API routes, schemas, persistence, and dashboard rendering; separate controller/service packages would add layers without additional business logic.

## Architecture and request flow

```text
Client HTTP request
        |
        v
FastAPI route + Pydantic validation (main.py / models.py)
        |
        v
TaskStore operation + parameterized SQL (database.py)
        |
        v
SQLite file (data/tasks.db)
        |
        v
Response validated against the Task schema -> JSON to client
```

`create_app()` builds the API and its database repository. Its lifespan handler creates the table on startup without deleting existing tasks. The repository opens a connection for each operation, commits successful writes, rolls back failures, and closes the connection.

For example, POST `/tasks` first validates the title and status. The repository inserts the task with a generated ID and UTC timestamp, then the route returns the saved task with HTTP 201. Invalid requests return 422 before writing. GET/PATCH/DELETE on a valid but nonexistent ID return 404.

## How we implemented the project

1. Read the assignment requirements, inspect the empty Day 04 folder, and select Track B. Document the minimum architecture and acceptance criteria in `PLAN.md`.
2. Add `AGENTS.md` to constrain changes, require real verification, and avoid unrelated features.
3. Define `TaskCreate`, `TaskUpdate`, `Task`, and allowed statuses in `models.py`. Enforce title/description limits, reject unknown fields, and distinguish omitted PATCH fields from explicit null values.
4. Implement the `TaskStore` repository in `database.py`, using SQLite constraints, parameterized queries, and transaction cleanup.
5. Connect five CRUD routes in `main.py`, with explicit success codes, positive integer ID validation, and not-found errors.
6. Add isolated automated tests in `tests/test_tasks.py`; add a real HTTP verification script that restarts Uvicorn against the same temporary database.
7. Run tests and HTTP checks, inspect the resulting source/dependencies, record the outputs, and prepare the reflection and submission package.

This is a small layered design: schemas define the contract, routes handle HTTP, and the repository handles storage. Tests exercise observable behavior rather than replacing database operations with mocks.

## Prerequisites and setup

Python 3.10+ is required; this submission was actually tested on Windows with Python 3.14.8. Run these PowerShell commands from this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The existing `.venv` in the working folder is already installed. The submission ZIP excludes it. `requirements-lock.txt` captures the exact installed versions used for verification; `requirements.txt` lists direct dependencies with version ranges. Install only one of these files. For local development, append `--reload` to the run command. No activation or PowerShell execution-policy change is needed.

Open **`http://127.0.0.1:8000/`** for the home dashboard and task controls. Create a task with the form, open its detail page, edit its title/description/status, or delete it after confirmation. The dashboard renders current SQLite data when loaded. Task titles and descriptions are HTML-escaped before display.

Open `http://127.0.0.1:8000/docs` for optional interactive API documentation. OpenAPI JSON is at `/openapi.json`. The home page and CRUD UI were added at the user's explicit request after the original API assessment implementation.

SQLite creates `data/tasks.db` on startup. The default path is anchored to the project, so changing the working directory does not change that default file. To use another persistent database:

```powershell
$env:TASK_DB_PATH = Join-Path $PWD 'data\custom-tasks.db'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Reuse the same database path on restart. Do not set it to `:memory:`: the repository deliberately uses file persistence and a new connection per operation.

## Using the task UI

| Page | URL | What you can do |
| --- | --- | --- |
| Overview | `/` | See counts and saved tasks |
| Task list | `/ui/tasks` | Filter by status, browse tasks, and open their details |
| Create | `/ui/tasks/new` | Enter a title, optional description, and status |
| Details | `/ui/tasks/{id}` | Read the task, open edit, or confirm deletion |
| Edit | `/ui/tasks/{id}/edit` | Update fields or clear the description |

Overview (`/`) shows summary counts; Tasks (`/ui/tasks`) is a separate list with All/Pending/In progress/Completed filters. The current navigation item is highlighted. The Create/Save buttons use POST/PATCH on the existing JSON API, then open the saved task. Delete calls DELETE only after confirmation and returns to the task list. Forms require JavaScript; validation/network failures appear inline without discarding entered values. A missing task has a friendly 404 page. Swagger remains available, but is not needed for ordinary task management.

To verify manually: create a task, open it, edit its status and description, return to the list, restart the server and confirm it persists, then delete it. Try a whitespace-only title and confirm an error appears. Cancel deletion once to confirm that nothing changes.

## Task contract

| Field | Behavior |
| --- | --- |
| `id` | Server-generated positive SQLite integer; clients cannot set it |
| `title` | Required for creation; whitespace trimmed; 1–200 characters after trimming |
| `description` | Optional string or null; maximum 2,000 characters |
| `status` | `pending` (default), `in_progress`, or `completed` |
| `created_at` | Server-generated timestamp in UTC; cannot be edited |

Unknown fields are rejected. PATCH must contain at least one editable field. Omitted fields remain unchanged; `description: null` clears a description; null title/status are rejected. IDs must be positive integers within SQLite's signed 64-bit range. A collection request `/tasks` intentionally has no ID; an individual operation requires `/tasks/{id}`.

## Endpoints

| Method | Path | Success | Errors |
| --- | --- | --- | --- |
| GET | `/` | 200, HTML dashboard | — |
| POST | `/tasks` | 201, task object, Location header | 422 invalid/missing input |
| GET | `/tasks` | 200, array ordered by ID | — |
| GET | `/tasks/{id}` | 200, task object | 422 invalid ID; 404 missing task |
| PATCH | `/tasks/{id}` | 200, updated task | 422 invalid input/ID; 404 missing task |
| DELETE | `/tasks/{id}` | 204, empty body | 422 invalid ID; 404 missing task |

For a PATCH with both an invalid body and a nonexistent ID, request validation runs first and returns 422.

## Sample requests

With the server running, use a second PowerShell terminal:

```powershell
$base = 'http://127.0.0.1:8000'
$task = Invoke-RestMethod -Method Post -Uri "$base/tasks" -ContentType 'application/json' -Body '{"title":"Complete Day 04","description":"Prepare assessment"}'
Invoke-RestMethod -Uri "$base/tasks"
Invoke-RestMethod -Uri "$base/tasks/$($task.id)"
Invoke-RestMethod -Method Patch -Uri "$base/tasks/$($task.id)" -ContentType 'application/json' -Body '{"status":"completed"}'
Invoke-WebRequest -Method Delete -Uri "$base/tasks/$($task.id)"
```

Illustrative creation response (ID and timestamp vary):

```json
{
  "id": 1,
  "title": "Complete Day 04",
  "description": "Prepare assessment",
  "status": "pending",
  "created_at": "2026-10-13T00:00:00Z"
}
```

A nonexistent task returns `404` with `{"detail":"Task not found"}`. Validation returns `422` with a `detail` array identifying the field and validation failure. Exact responses from the actual run are in [evidence/http-exchanges.json](evidence/http-exchanges.json); the illustrative timestamp above is not test evidence.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe scripts\verify_http.py
.\.venv\Scripts\python.exe -m pip check
```

Actual results: **46 tests passed**, **13 real HTTP exchanges passed**, and `pip check` reported no broken requirements. The HTTP script starts three local Uvicorn processes in sequence, verifies state after two restarts, and stops each process. It uses a temporary database and does not alter `data/tasks.db`.

After adding the user-requested dashboard, **47 tests passed**; the new test covers empty state, saved task display, completed count, links, and HTML escaping. Output is in `evidence/dashboard-tests.txt`. The earlier API and restart evidence remains available. After adding the CRUD UI, **51 tests passed**, recorded in `evidence/ui-tests.txt`. These tests validate HTTP page rendering, escaped form values, friendly missing-task pages, asset serving, and API state transitions. Browser JavaScript execution and visual appearance were not automated in this environment.

One test warning comes from installed Starlette's deprecation of HTTPX-based TestClient. Tests passed with the locked versions; a future dependency refresh should review the recommended successor rather than hiding the warning.

See [VERIFICATION.md](VERIFICATION.md) and raw logs under `evidence/`.

## Design choices and limitations

- **SQLite over in-memory storage:** restart persistence with no database server. Trade-off: concurrent writes serialize; this design suits a small local workload, not a high-throughput service.
- **Standard-library SQLite over an ORM:** fewer direct dependencies and visible SQL. Trade-off: schema changes would require an explicit migration approach.
- **Pydantic over custom request parsing:** consistent 422 responses and OpenAPI contracts. A small update validator enforces nonempty PATCH and prevents null title/status.
- **Synchronous routes:** match blocking SQLite operations; FastAPI runs synchronous endpoint functions outside the event loop.
- **PATCH over PUT:** supports partial updates without replacing omitted fields; creation time is immutable.
- All user values use SQL parameters; dynamic update columns come from a fixed allowlist. Tests include an SQL-like title and show it is stored as text.
- Local use only: no authentication, authorization, backups, migrations, pagination, rate limiting, or load testing. Use the loopback host shown above. Production use needs those decisions and operational verification.
- Dependency consistency was checked, but no vulnerability audit or load test was performed.

Implementation conventions follow [FastAPI's testing guide](https://fastapi.tiangolo.com/tutorial/testing/) and [Python's sqlite3 documentation](https://docs.python.org/3.14/library/sqlite3.html).

## Assessment submission

**Complete Assignment A OR Assignment B, not both.** The assignment document explicitly says “Choose this track OR the alternative track.” This project completes the local implementation for Assignment B.

**Code alone is not the full submission.** Include the following:

- Source, tests, guidance: `app/`, `tests/`, `scripts/`, `AGENTS.md`, dependency files.
- Planning and acceptance criteria: [PLAN.md](PLAN.md).
- Actual evidence and review: [VERIFICATION.md](VERIFICATION.md), `evidence/`.
- Reflection: [ENGINEERING_REFLECTION.md](ENGINEERING_REFLECTION.md) and its Word copy.
- Submission archive: `Day04_Assignment_B_Submission.zip`, excluding environment, caches, and databases.

The documents require an engineering reflection but do not prescribe Word as the submission format. The completed Word file is provided for convenience; include it if your submission portal accepts Word or your trainer requests it. You do not need to fill out or submit Assignment A for this track. The original assignment documents and presentation are reference materials, not listed as completed deliverables to resubmit.

The local assessment package is prepared. The assignment also asks for a repository URL: upload these source files to an approved GitHub/internal repository and provide its link. No repository was published or commit created. Read the code/reflection and perform your own review before submitting; agent review does not certify human acceptance or organizational tool approval.

Navigation follow-up: **52 tests passed** after separating Overview and Tasks, including status filters and active navigation. Output: `evidence/navigation-tests.txt`.
