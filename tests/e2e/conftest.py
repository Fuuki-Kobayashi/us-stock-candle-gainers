"""E2E test fixtures: start/stop the FastAPI server for Playwright tests."""

import shutil
import socket
import subprocess
import time
from collections.abc import Generator
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _wait_for_server(host: str, port: int, timeout: float = 15.0) -> None:
    """Wait until the server accepts TCP connections."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError:
            time.sleep(0.3)
    raise TimeoutError(f"Server did not start on {host}:{port} within {timeout}s")


@pytest.fixture(scope="session")
def base_url() -> Generator[str, None, None]:
    """Start uvicorn via uv, yield the base URL, then shut it down."""
    port = 8111  # Use a non-standard port to avoid conflicts
    uv_bin = shutil.which("uv")
    if uv_bin is None:
        raise RuntimeError("uv is not installed or not found in PATH")

    proc = subprocess.Popen(
        [
            uv_bin,
            "run",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        _wait_for_server("127.0.0.1", port)
        yield f"http://127.0.0.1:{port}"
    finally:
        proc.terminate()
        proc.wait(timeout=5)
