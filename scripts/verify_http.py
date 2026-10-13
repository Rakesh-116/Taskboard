"""Exercise actual HTTP and restart Uvicorn using an isolated temporary database."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

import httpx


ROOT = Path(__file__).resolve().parents[1]


def main():
    evidence = ROOT / "evidence"
    evidence.mkdir(exist_ok=True)
    exchanges = []
    with TemporaryDirectory(prefix="day04-http-") as directory:
        environment = {**os.environ, "TASK_DB_PATH": str(Path(directory) / "tasks.db")}
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        with (evidence / "server.log").open("w", encoding="utf-8") as server_log:
            def start():
                process = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
                    cwd=ROOT, env=environment, stdout=server_log, stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                try:
                    for _ in range(100):
                        if process.poll() is not None:
                            raise RuntimeError("Server exited; see evidence/server.log")
                        try:
                            if httpx.get(base + "/tasks", timeout=1).status_code == 200:
                                return process
                        except httpx.TransportError:
                            pass
                        time.sleep(0.1)
                    raise RuntimeError("Server readiness timeout")
                except BaseException:
                    stop(process)
                    raise

            def stop(process):
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)

            def request(method, path, expected, payload=None):
                kwargs = {"json": payload} if payload is not None else {}
                response = httpx.request(method, base + path, timeout=5, **kwargs)
                body = response.json() if response.content else None
                exchanges.append({"method": method, "path": path, "request": payload, "status": response.status_code, "response": body})
                assert response.status_code == expected, exchanges[-1]
                print(f"PASS {method} {path} -> {expected}")
                return body

            process = start()
            try:
                task = request("POST", "/tasks", 201, {"title": "Complete Day 04", "description": "Verified over real HTTP"})
                path = f"/tasks/{task['id']}"
                assert request("GET", "/tasks", 200) == [task]
                assert request("GET", path, 200) == task
                updated = request("PATCH", path, 200, {"status": "completed"})
                assert updated["status"] == "completed"
                request("POST", "/tasks", 422, {"title": "   "})
                request("POST", "/tasks", 422, {"title": "Invalid status", "status": "done"})
                request("GET", "/tasks/999", 404)
                request("GET", "/tasks/abc", 422)
            finally:
                stop(process)
            print("STOPPED first Uvicorn process; restarting against the same SQLite file")
            process = start()
            try:
                assert request("GET", path, 200) == updated
                print("PASS task ID, fields, updated status, and timestamp survived process restart")
                request("DELETE", path, 204)
                request("GET", path, 404)
                assert request("GET", "/tasks", 200) == []
            finally:
                stop(process)
            process = start()
            try:
                assert request("GET", "/tasks", 200) == []
                print("PASS deletion survived second process restart")
            finally:
                stop(process)
    (evidence / "http-exchanges.json").write_text(json.dumps(exchanges, indent=2) + "\n", encoding="utf-8")
    print(f"PASS all {len(exchanges)} real HTTP exchanges; server processes stopped")


if __name__ == "__main__":
    main()
