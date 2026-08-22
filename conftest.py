"""
Global pytest fixtures for the API automation framework.

  api_server   : boots the bundled Inventory API (FastAPI/uvicorn) per session
  base_url     : base URL of the running service
  auth_token   : bearer token for the default QA user
  auth_headers : ready-to-use Authorization header dict
"""
import os
import socket
import subprocess
import sys
import time

import pytest
import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = "127.0.0.1", 8080
BASE_URL = f"http://{HOST}:{PORT}"
VALID_USER = {"username": "qa_user", "password": "qa123"}


def _wait_for_port(host, port, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


@pytest.fixture(scope="session")
def api_server():
    """Start the Inventory API once for the whole session."""
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api_server.app:app",
         "--port", str(PORT), "--log-level", "warning"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not _wait_for_port(HOST, PORT, timeout=30):
        proc.terminate()
        raise RuntimeError("Inventory API did not start on port 8080")
    yield BASE_URL
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture()
def base_url(api_server):
    return api_server


@pytest.fixture()
def auth_token(base_url):
    """Log in as the default QA user and return the bearer token."""
    resp = requests.post(f"{base_url}/auth/login", json=VALID_USER, timeout=10)
    assert resp.status_code == 200, f"Fixture login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture()
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
