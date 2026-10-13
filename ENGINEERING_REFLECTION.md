# Day 04 — Engineering Reflection

This reflection describes the observed coding-agent session. It does not invent learner interventions, model usage metrics, or independent human review. The learner should read and confirm the statements before submission.

## 1. Tool and repository

Codex was used through this session on a non-sensitive local training folder, `Day-4_Assignment_B_Build_New_Application`. Python/PowerShell were used for implementation and verification. The folder was initially empty. Tool functionality was available; compliance with the learner's organizational account/access policy must be confirmed by the learner. No confidential repository or credentials were needed.

## 2. Goal, context, constraints, and definition of done

The request was to complete the easier/faster Day 04 assessment inside the Day 04 folder. Track B was selected because Track A needs a suitable existing authorized API. The goal was a local task-management REST API with create/list/get/update/delete, validation, SQLite persistence, automated tests, setup instructions, and honest evidence/reflection.

Scope excluded frontend, authentication, cloud deployment, external integrations, unnecessary dependencies, automatic commits, and multi-agent orchestration. Local completion required working CRUD operations, meaningful 422/404 errors, verified restart persistence, captured actual results, and reviewed source. The hosted repository link required by the assignment remains a learner submission step because no remote destination was supplied.

## 3. Project guidance

The project contains `AGENTS.md`. One concrete instruction is: “Add behavioral tests and run them before reporting success.” Other guidance requires parameterized SQL, bounded changes, actual restart verification, no sensitive data, and no automatic publication. This keeps future coding-agent work aligned with the assessment.

## 4. Suggestions, choices, and a suggestion to question

The agent proposed FastAPI, Pydantic, built-in SQLite, three small application modules, isolated tests, and an actual HTTP restart check. These choices were implemented under the user's instruction to complete the assessment. No separate plan-approval exchange or learner architecture challenge occurred; neither is claimed here.

SQLite was chosen over in-memory storage to satisfy persistence. Built-in sqlite3 was chosen over an ORM to reduce direct dependencies and keep queries inspectable. PATCH was chosen for partial updates. Framework validation supplies consistent errors; a small custom validator handles nonempty updates and null rules.

A suggestion I would question before further work is adding an ORM or authentication to this assessment. An ORM would add setup and migration decisions; authentication would expand the business scope and test matrix. Both should require a concrete need. This is a proposed question, not an intervention that occurred in this session.

## 5. What was actually verified

`.\.venv\Scripts\python.exe -m pytest -v` ran successfully: **46 passed, 1 warning in 2.16 seconds**. Tests cover task lifecycle, validation, field limits, allowed statuses, nonexistent and invalid IDs, SQL-like input, documentation availability, and create/update/delete persistence through fresh applications.

`.\.venv\Scripts\python.exe scripts\verify_http.py` ran actual Uvicorn processes and **13 HTTP exchanges**, verifying updated task state after one restart and deletion after another. Actual payloads/responses and server output are saved under `evidence/`. `pip check` found no broken requirements.

The agent reviewed the source and captured an additions diff from the empty folder, since Git was unavailable on PATH. This is not a claimed Git diff or independent human acceptance. The learner still needs to inspect the code/diff and approve the final behavior before submission.

## 6. Failures, investigation, and recovery

The first dependency installation failed because the sandbox blocked PyPI sockets (WinError 10013). The agent identified the network restriction and retried using requested/approved network access rather than changing application code or running repeated blind retries. Installation then succeeded.

Git was unavailable on PATH, so the evidence explicitly uses a generated unified additions diff and file hashes. No application-test failures occurred. A Starlette TestClient deprecation warning was retained and documented; it did not fail the tests. No fabricated debugging story is needed.

## 7. Security, remaining risk, and improvement

The API uses input validation, parameterized SQL, a fixed allowlist of update columns, and transaction/connection cleanup. Verification uses synthetic task data and isolated temporary databases. No secrets were inspected or embedded, and no remote publication occurred.

A remaining risk is SQLite write contention as usage grows. A next iteration should add measured concurrency tests and pagination before considering a larger database. Production use would additionally need access controls, backup/migration plans, and a dependency vulnerability review; these were not performed here. The TestClient warning should be addressed when dependencies are refreshed.

## 8. Cost efficiency and responsible AI use

Work stayed in the Day 04 folder after a small workspace inspection. Only the relevant assignment/reflection documents were extracted; the user-supplied presentation summary provided workflow context, and the PDF was not independently parsed. Official FastAPI/Python documentation was consulted for implementation conventions. No parallel agents, model switching, frontend generation, or cloud setup were used.

The test suite was run once after implementation, then a separate real HTTP check covered the acceptance gap of process restart persistence. Parameterized tests cover many invalid inputs without repetitive manual requests. A project-local environment avoids unrelated package changes. No token, financial, or percentage savings are claimed because measured usage data was not collected.

For a repeated failed attempt, stop, identify the failing command and cause, and make a focused correction or request the missing permission. Do not rerun the entire workflow without new evidence. The sandbox failure in this session followed that principle.

## 9. AI value and the FDE lens

The agent turned a bounded requirement set into a small implementation, tests, and reproducible evidence. This can accelerate delivery while preserving customer confidence through inspectable source, documented contracts, actual error responses, and restart checks. A technical customer could review the test log, HTTP exchanges, architecture trade-offs, and additions diff.

AI-assisted execution remains subject to human responsibility: the learner must understand data flow (request validation → route → SQLite transaction → response), confirm tool approval, inspect the source/dependencies, and accept the result. Passing tests support acceptance but do not authorize a merge or publication.

## 10. Day 05 preparation

Retrieval helps answer questions from private or changing knowledge that is not reliably available in a model's training. Parse documents into usable text, remove repeated headers/footers and noise while preserving structure, choose chunk size based on coherent content and retrieval needs, use overlap where context would otherwise be lost, and attach source/section/access metadata for filtering and citation. This is preparatory reading, not an additional application assignment.

## Follow-up: requested home dashboard

After the original assessment implementation, the learner ran the service and observed a 404 at `/`. The API was operating as designed; the learner then explicitly requested a home/dashboard there. This authorized a small extension to the original no-frontend scope. The dashboard displays actual task counts and saved tasks, and links to the interactive API docs for mutations. Server-rendered HTML keeps the extension small with no new dependencies; user-provided text is escaped to prevent HTML injection.

The agent used the Sites skill's local-only workflow guidance while implementing the page in the existing FastAPI project; no Site was registered or deployed. After the code change, the full test suite passed **47 tests** with the existing TestClient deprecation warning. The added test verifies dashboard content, counts, links, empty state, and HTML escaping. Browser visual inspection was not performed. The original 46-test and restart results remain historical evidence, and the new test log is recorded separately. The learner should verify the dashboard visually and refresh it after task changes.

## Follow-up: task management UI

The learner then requested UI for the other API operations. The extension adds task list/create/detail/edit pages and a deletion confirmation dialog. Forms call the original JSON endpoints; validation and SQLite persistence remain centralized. Plain HTML/CSS and small JavaScript keep the application understandable and avoid new frontend dependencies. User data remains escaped in templates, and errors are inserted with textContent.

The agent reran the full suite: **51 tests passed**, with the existing warning. Tests exercise page rendering, prefilled forms and escaping, missing-task pages, asset delivery, and corresponding API state transitions. They do not simulate browser clicks or execute JavaScript; that verification remains a manual learner step. This distinction prevents treating HTTP tests as proof of complete browser behavior. The Sites skill was used for local UI workflow guidance; the app remains local.

## Follow-up: navigation correction

The learner identified that Overview and Tasks looked identical. Both URLs originally shared the dashboard renderer. The agent corrected this by separating their handlers: Overview retains summary counts, while Tasks provides a dedicated list with status filters and active navigation styling. The full suite passed **52 tests**, including a regression test for distinct views and correct filtering. This was an implementation issue identified through learner feedback; earlier screenshots did not prove the navigation views were distinct.
