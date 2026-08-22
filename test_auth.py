"""Auth tests — login happy paths, bad credentials, malformed payloads."""
import pytest
import requests

from utils.validators import assert_error_detail


@pytest.mark.smoke
@pytest.mark.parametrize(
    "username,password",
    [("qa_user", "qa123"), ("admin", "admin123")],
    ids=["qa-user", "admin-user"],
)
def test_valid_login_returns_token(base_url, username, password):
    resp = requests.post(
        f"{base_url}/auth/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["access_token"] == f"tok-{username}"
    assert data["token_type"] == "bearer"


def test_invalid_password_returns_401(base_url):
    resp = requests.post(
        f"{base_url}/auth/login",
        json={"username": "qa_user", "password": "wrong-password"},
        timeout=10,
    )
    assert resp.status_code == 401
    assert_error_detail(resp, "Invalid credentials")


def test_unknown_user_returns_401(base_url):
    resp = requests.post(
        f"{base_url}/auth/login",
        json={"username": "ghost", "password": "qa123"},
        timeout=10,
    )
    assert resp.status_code == 401
    assert_error_detail(resp, "Invalid credentials")


def test_login_missing_field_returns_422(base_url):
    """Pydantic rejects the body before the endpoint logic even runs."""
    resp = requests.post(f"{base_url}/auth/login", json={"username": "qa_user"}, timeout=10)
    assert resp.status_code == 422
    assert "detail" in resp.json()


@pytest.mark.regression
def test_token_works_on_protected_endpoint(base_url, auth_token):
    resp = requests.get(
        f"{base_url}/products",
        headers={"Authorization": f"Bearer {auth_token}"},
        timeout=10,
    )
    assert resp.status_code == 200
