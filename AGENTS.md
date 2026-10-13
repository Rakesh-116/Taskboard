# Task Management API — Project Guidance

- Use Python, FastAPI, Pydantic, and the standard-library sqlite3 module.
- Keep changes inside this project and keep the application small.
- Validate titles, status values, task IDs, and unknown request fields.
- Use parameterized SQL; never expose secrets or add sensitive sample data.
- Add behavioral tests and run them before reporting success.
- Verify persistence using a fresh application and an actual server restart.
- Review all changed files and dependencies, and report actual commands/results.
- Keep the user-requested dashboard and task CRUD pages small. UI forms must call the existing API and escape user data. Do not add authentication, cloud services, or parallel agents unless requested.
- Do not commit or publish automatically.
