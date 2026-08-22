"""Products CRUD tests — happy paths, validation, auth guards, edge cases."""
import pytest
import requests

from utils.validators import assert_valid_product, assert_error_detail


@pytest.mark.smoke
def test_list_products_returns_seed_data(base_url, auth_headers):
    resp = requests.get(f"{base_url}/products", headers=auth_headers, timeout=10)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 4
    assert {p["id"] for p in items} >= {1, 2, 3, 4}
    for item in items:
        assert_valid_product(item)


def test_get_product_by_id(base_url, auth_headers):
    resp = requests.get(f"{base_url}/products/1", headers=auth_headers, timeout=10)
    assert resp.status_code == 200
    body = assert_valid_product(resp.json(), expect_id=1)
    assert body["name"] == "Wireless Mouse"
    assert body["price"] == pytest.approx(25.99)


def test_get_missing_product_returns_404(base_url, auth_headers):
    resp = requests.get(f"{base_url}/products/9999", headers=auth_headers, timeout=10)
    assert resp.status_code == 404
    assert_error_detail(resp, "Product not found")


def test_create_and_fetch_product(base_url, auth_headers):
    payload = {"name": "Portable SSD", "price": 129.99, "stock": 12, "category": "storage"}
    resp = requests.post(f"{base_url}/products", json=payload, headers=auth_headers, timeout=10)
    assert resp.status_code == 201
    created = assert_valid_product(resp.json())

    fetch = requests.get(
        f"{base_url}/products/{created['id']}", headers=auth_headers, timeout=10
    )
    assert fetch.status_code == 200
    assert fetch.json() == {**payload, "id": created["id"]}


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"name": "", "price": 5.0, "stock": 1},        # empty name
        {"name": "X", "price": -1.5, "stock": 1},      # negative price
        {"name": "X", "price": 5.0, "stock": -3},      # negative stock
        {"price": 5.0, "stock": 1},                    # missing name
    ],
    ids=["empty-name", "negative-price", "negative-stock", "missing-name"],
)
def test_create_invalid_product_returns_422(base_url, auth_headers, bad_payload):
    resp = requests.post(f"{base_url}/products", json=bad_payload, headers=auth_headers, timeout=10)
    assert resp.status_code == 422, f"Expected 422 for {bad_payload}, got {resp.status_code}"


def test_update_product(base_url, auth_headers):
    payload = {"name": "Wireless Mouse Pro", "price": 39.99, "stock": 42, "category": "accessories"}
    resp = requests.put(f"{base_url}/products/1", json=payload, headers=auth_headers, timeout=10)
    assert resp.status_code == 200
    body = assert_valid_product(resp.json(), expect_id=1)
    assert body["name"] == "Wireless Mouse Pro"
    assert body["price"] == pytest.approx(39.99)


def test_update_missing_product_returns_404(base_url, auth_headers):
    resp = requests.put(
        f"{base_url}/products/9999",
        json={"name": "X", "price": 1.0, "stock": 1},
        headers=auth_headers,
        timeout=10,
    )
    assert resp.status_code == 404
    assert_error_detail(resp, "Product not found")


def test_delete_product(base_url, auth_headers):
    created = requests.post(
        f"{base_url}/products",
        json={"name": "Temp Product", "price": 1.0, "stock": 1, "category": "temp"},
        headers=auth_headers,
        timeout=10,
    ).json()

    resp = requests.delete(
        f"{base_url}/products/{created['id']}", headers=auth_headers, timeout=10
    )
    assert resp.status_code == 204

    gone = requests.get(
        f"{base_url}/products/{created['id']}", headers=auth_headers, timeout=10
    )
    assert gone.status_code == 404


def test_delete_missing_product_returns_404(base_url, auth_headers):
    resp = requests.delete(f"{base_url}/products/424242", headers=auth_headers, timeout=10)
    assert resp.status_code == 404
    assert_error_detail(resp, "Product not found")


@pytest.mark.regression
def test_unauthenticated_requests_are_rejected(base_url):
    resp = requests.get(f"{base_url}/products", timeout=10)
    assert resp.status_code == 401
    assert_error_detail(resp, "Not authenticated")


@pytest.mark.regression
def test_invalid_token_is_rejected(base_url):
    resp = requests.get(
        f"{base_url}/products",
        headers={"Authorization": "Bearer tok-someone-else"},
        timeout=10,
    )
    assert resp.status_code == 401
    assert_error_detail(resp, "Not authenticated")
