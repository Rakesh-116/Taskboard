# Verification and change review

Verification completed during the Day 04 work session ending 13 October 2026 (Asia/Calcutta). This report records actual execution, rather than expected results.

## Environment and commands

Windows PowerShell; Python 3.14.8; project-local `.venv`. Exact dependency versions are in `requirements-lock.txt`.

| Command (from this folder) | Actual result | Evidence |
| --- | --- | --- |
| `python -m venv .venv` | Exit 0 | Executed in chat terminal |
| `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` | Initial sandbox attempt failed with WinError 10013; approved retry installed dependencies | Executed in chat terminal; resolved versions in lock file |
| `.\.venv\Scripts\python.exe -m pytest -v` | Exit 0; 46 passed, 1 warning in 2.16 seconds | `evidence/pytest.txt` |
| `.\.venv\Scripts\python.exe scripts\verify_http.py` | Exit 0; 13 HTTP exchanges passed, including state across two restarts | `evidence/http-verification.txt`, `evidence/http-exchanges.json`, `evidence/server.log` |
| `.\.venv\Scripts\python.exe -m pip check` | Exit 0; no broken requirements | `evidence/dependency-check.txt` |
| `.\.venv\Scripts\python.exe -m pip freeze` | Captured actual installed versions | `requirements-lock.txt` |

Test and HTTP output were captured with `2>&1 | Tee-Object -FilePath evidence\<filename>`; the commands propagated the Python process exit code with `exit $LASTEXITCODE`.

## Requirement evidence

| Requirement | Evidence |
| --- | --- |
| ID/title/description/status/time | Lifecycle test checks all fields, positive ID, default status, normalized title, UTC time |
| Create/list/get | Lifecycle test plus real POST/GET requests |
| Update/delete | Lifecycle test verifies retained fields and immutable timestamp; real PATCH/DELETE requests |
| Invalid/missing fields | Parameterized create/update tests; real invalid title/status requests |
| Invalid task IDs | Parameterized GET/PATCH/DELETE checks for zero, negative, text, decimal, and oversized IDs |
| Nonexistent task IDs | GET/PATCH/DELETE tests return 404; real missing-resource GET |
| Restart persistence | Fresh-app test covers create/update/delete; actual Uvicorn process restarts verify persisted update and deletion |
| SQL parameterization | SQL-like task title round-trips without harming table or another task |
| Documentation | README includes setup/run commands, contract, examples, trade-offs, limitations |

## Source review

Baseline: Day 04 folder existed and contained no files before this work. Git was unavailable on PATH (`git rev-parse --show-toplevel` could not run). An additions diff from the empty baseline is captured in `evidence/source-additions.diff`; it is a generated unified diff, **not** output from `git diff`. A SHA-256 source manifest is included alongside it.

Reviewed application schemas, routes, database operations, tests, verification script, guidance, dependencies, README, and reflection. Review found:

- Five intended CRUD API routes plus the user-requested home dashboard; no unrelated authentication or deployment code.
- Valid requests preserve task fields; failed validation writes no data.
- Response codes match documented contracts; DELETE sends no response body.
- SQLite operations commit/rollback and explicitly close connections.
- All values are parameterized; interpolated identifiers use a fixed allowlist.
- Temporary test databases isolate verification from normal user data.
- App import does not initialize the database; startup does, enabling isolated app factories.
- Dependencies are limited to the framework, validation, server, and test clients/tools; transitive packages are recorded in the lock file.

Agent review is complete; learner review/acceptance is still a human submission responsibility. The learner supplied the repository URL: [Rakesh-116/Taskboard](https://github.com/Rakesh-116/Taskboard). No remote-content verification, agent commit/push, vulnerability-audit claim, or independent human acceptance is asserted.

## Observed issues and remaining risks

The dependency download required network approval after the sandbox restriction. No application-test failure occurred. Installed Starlette emits one TestClient deprecation warning recommending `httpx2`; the current locked combination passed. A dependency update should address that warning deliberately.

SQLite write contention, unlimited list size, and absence of identity/access controls remain local-demo limitations. Before production, establish access control, migrations/backups, pagination, dependency security review, and concurrency/load tests.

## Home dashboard follow-up

The user explicitly requested a home/dashboard at `/` after seeing the root return 404. Added a server-rendered HTML page with task counts, saved task rows, empty state, refresh, and API docs links. User text is HTML-escaped; no new packages were installed. The dashboard reads the existing SQLite store.

Ran `.\.venv\Scripts\python.exe -m pytest -v` again after this code change: **47 tests passed**, with the same dependency deprecation warning. The added behavioral test verifies root HTML, empty state, task rendering, status count, task links, and escaping of script-like title/description values. Actual output is in `evidence/dashboard-tests.txt`. Browser visual inspection was not performed; responsive layout is implemented in CSS. The previously captured real HTTP/restart evidence applies to the existing API routes.

## Task CRUD UI follow-up

The user requested UI for all task operations. Added `/ui/tasks`, `/ui/tasks/new`, `/ui/tasks/{id}`, and `/ui/tasks/{id}/edit`. Shared HTML/CSS presents forms, details, and deletion confirmation. JavaScript uses the existing POST/PATCH/DELETE API, displays errors with textContent, prevents duplicate submissions, and navigates after successful actions. No new dependencies were added.

Ran `.\.venv\Scripts\python.exe -m pytest -v`: **51 passed, 1 warning in 5.77 seconds**. Actual log: `evidence/ui-tests.txt`. Tests cover page/form endpoints, title/description escaping, task links, update/delete API state reflected in pages, friendly 404s, and CSS/JavaScript asset delivery. These are server-side HTTP tests; browser clicks, JavaScript execution, and visual layout were not tested because no browser-testing tool/runtime is available. Manual UI verification steps are in README.

## Navigation correction

Overview and Tasks initially used different URLs but shared a dashboard handler. They now have distinct handlers/views: overview summary at `/`, and task workspace at `/ui/tasks` with validated status filters and highlighted navigation. Ran the full suite: **52 passed, 1 warning in 5.22 seconds**; output in `evidence/navigation-tests.txt`. The regression test verifies distinct content, active navigation, filter results, invalid filter rejection, and unchanged API data.
