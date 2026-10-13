# Day 04 implementation plan and acceptance criteria

Selected track: **Assignment B — Build a New Application**.

The Day 04 directory was empty at inspection. Assignment A would require an existing authorized API and a baseline; building a new minimal API is the more direct option here.

## Scope and authorization

The user requested completion of the easier/faster assessment and changes inside the Day 04 folder. A plan was presented in chat before application files were written. The final instruction to complete and make changes was treated as authorization to execute that plan. There was no separate interactive plan-approval exchange; this document does not claim one.

## Minimal architecture

- `app/models.py`: Pydantic request validation and response contracts.
- `app/database.py`: standard-library SQLite repository, parameterized queries, transaction/connection cleanup.
- `app/main.py`: FastAPI application factory, startup initialization, five CRUD routes.
- `tests/test_tasks.py`: isolated temporary databases and behavioral API tests.
- `scripts/verify_http.py`: actual Uvicorn processes, HTTP requests, restart verification.

Use synchronous routes for synchronous SQLite calls. Each database operation owns and closes its connection. No ORM, frontend, authentication, cloud deployment, external integrations, or parallel agents.

## Implementation stages

1. Create project guidance, dependencies, schemas, SQLite setup, and routes.
2. Add tests for CRUD, validation, missing resources, and persistent state.
3. Install dependencies in a project virtual environment; run actual tests.
4. Exercise actual HTTP endpoints and restart the service against the same SQLite file.
5. Review source/dependencies and capture an additions diff from the initially empty folder.
6. Prepare README, test logs, actual request/response evidence, reflection, and a submission archive.

## Acceptance criteria

| Requirement | Expected behavior |
| --- | --- |
| Task fields | Server-generated positive ID, nonblank title, optional description, allowed status, UTC creation timestamp |
| Create | POST `/tasks`: 201 and saved task |
| List | GET `/tasks`: 200 and tasks in ID order |
| Retrieve | GET `/tasks/{id}`: 200 or 404 |
| Update | PATCH `/tasks/{id}`: 200; only supplied fields change |
| Delete | DELETE `/tasks/{id}`: 204; subsequent get is 404 |
| Validation | Missing/blank title, unknown status, invalid IDs, and invalid update payloads return 422 |
| Persistence | Create/update/delete state survives fresh applications and actual process restarts |
| Evidence | Real test output, actual HTTP exchanges, source review, README, honest reflection |

## Delivery boundary

All local deliverables are prepared inside this folder. The learner has now supplied the repository URL: [Rakesh-116/Taskboard](https://github.com/Rakesh-116/Taskboard). The agent has not committed or pushed local updates. Tool access was demonstrated, but organizational approval of the learner's account cannot be certified by this agent.

## User-requested UI extensions

After the original API assessment, the user explicitly requested a home dashboard and then UI for the other task operations. The implemented extension uses `/ui/tasks` list/create/detail/edit pages, shared templates/static assets, and JavaScript calling the same CRUD API. SQLite behavior and API contracts remain centralized. This is an authorized expansion of the original scope. Browser interaction verification is a manual follow-up; HTTP/API tests and UI rendering checks are recorded separately.
