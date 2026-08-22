"""Health check — the cheapest way to verify the service is up."""
import requests


def test_health_returns_ok(base_url):
    resp = requests.get(f"{base_url}/health", timeout=10)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "inventory-api"
