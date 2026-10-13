# Day 04 — Engineering Reflection

**Rakesh Penugonda (All Star)**

**Source repository:** [Rakesh-116/Taskboard](https://github.com/Rakesh-116/Taskboard)

## 1. Tool and project

I used Codex to build Taskboard for Assignment B. I worked in the Day 04 training folder using Python, FastAPI, SQLite, and PowerShell. I chose this track because I could build a small application from scratch without needing an existing customer-management API.

## 2. Goal and scope

My goal was to build a locally runnable task-management application with create, list, view, update, and delete operations. Each task needed a title, optional description, status, ID, and creation timestamp. I also needed input validation, persistent storage, automated tests, and documentation.

I initially kept the scope to the REST API. After running it in my browser, I requested a dashboard and separate task forms so I could use the application without relying on Swagger. The final UI includes an overview, a task list with status filters, create/edit forms, task details, and deletion confirmation. I kept authentication, cloud deployment, and external integrations outside this assessment.

## 3. Guidance I gave Codex

I asked Codex to keep the implementation small, work within the Day 04 folder, avoid unrelated changes, and report actual test results. The project includes AGENTS.md with guidance such as: "Add behavioral tests and run them before reporting success." It also requires parameterized SQL, meaningful validation errors, and no automatic commits or publishing.

## 4. Implementation decisions and trade-offs

I used the FastAPI and SQLite approach proposed by Codex. FastAPI provides request validation and API documentation, while SQLite stores tasks locally without needing a database server. Compared with in-memory storage, SQLite meets the restart-persistence requirement. Its trade-off is limited concurrent write capacity.

The implementation uses Python's built-in sqlite3 module instead of an ORM to keep dependencies and setup small. PATCH supports partial updates, and Pydantic validates titles and statuses. The UI uses shared HTML/CSS and a small JavaScript file that calls the same API, keeping validation and persistence in one place.

One design choice I questioned during testing was using the same dashboard view for Overview and Tasks. I pointed out that the two navigation items looked identical and asked for them to be separated. Overview now shows summary counts, while Tasks provides a dedicated list with status filters.

## 5. Verification and evidence

I ran the application locally and opened it in the browser. This helped me identify the missing home page, the earlier Create Task link pointing to Swagger, and the duplicate Overview/Tasks view. I used that feedback to request focused UI changes.

Codex ran the automated checks and saved the outputs in evidence/. The final suite passed **52 tests with one dependency deprecation warning**. It covers CRUD operations, invalid input, missing IDs, persistence, page rendering, HTML escaping, and status filtering. The command used was:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The HTTP verification script also completed **13 real HTTP exchanges**, including checks that an updated task and its later deletion survived server restarts:

```powershell
.\.venv\Scripts\python.exe scripts\verify_http.py
```

The project includes actual responses, test logs, a source-additions diff, and file hashes. The automated UI checks verify server responses; they do not simulate browser clicks or prove every JavaScript interaction.

## 6. Problems and recovery

The first package installation was blocked by the sandbox's network restrictions. Codex identified the cause and completed installation using approved network access. Git was initially unavailable when I tried git init, so Git for Windows was installed.

The root URL initially returned 404 because only API routes existed. I requested a home dashboard, then task CRUD pages. When Overview and Tasks still showed the same content, I raised the issue and Codex separated their views. These issues showed me why I needed to check the application myself even when automated tests passed.

## 7. Security and remaining improvements

The application validates input, uses parameterized SQL, and escapes task text before displaying it in HTML. Tests use temporary databases and synthetic data. I did not need to provide credentials or confidential information.

A remaining risk is SQLite write contention if the application grows. My next improvements would be pagination and concurrency tests. Before production use, I would also add access control, backups, migrations, and a dependency security review. The existing TestClient deprecation warning should be addressed during a dependency update.

## 8. Responsible AI use and cost control

I kept requests focused on one small project and used a single coding agent. I avoided parallel agents, cloud setup, and unnecessary framework additions. Tests were rerun after behavior changes, and existing logs were retained as evidence. I did not measure token or financial savings, so I cannot claim a specific reduction.

If repeated attempts failed, I would stop and inspect the error before requesting another change. This would avoid spending time on retries that do not address the cause.

## 9. Value of AI and my responsibility

Codex helped turn the requirements into application code, tests, UI pages, and documentation. My role was to define the scope, run the application, point out usability issues, and request corrections. The test logs, API responses, and documented trade-offs provide evidence I could show a technical customer.

My main takeaway is that generated code still needs verification. Passing tests was useful, but checking the browser exposed issues that the earlier tests had not covered. I remain responsible for understanding and reviewing the final result before submission.
