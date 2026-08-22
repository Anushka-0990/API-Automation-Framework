"""Reusable response validators — keeps tests declarative and DRY."""


def assert_valid_product(body, *, expect_id=None):
    """Assert a product JSON body has the right shape and sane values.

    Usage:  assert_valid_product(resp.json(), expect_id=1)
    """
    for field in ("id", "name", "price", "stock", "category"):
        assert field in body, f"Missing field '{field}' in {body}"
    assert isinstance(body["id"], int), "id must be an integer"
    assert isinstance(body["name"], str) and body["name"], "name must be a non-empty string"
    assert isinstance(body["price"], (int, float)) and body["price"] > 0, "price must be > 0"
    assert isinstance(body["stock"], int) and body["stock"] >= 0, "stock must be >= 0"
    assert isinstance(body["category"], str), "category must be a string"
    if expect_id is not None:
        assert body["id"] == expect_id, f"Expected id {expect_id}, got {body['id']}"
    return body


def assert_error_detail(resp, detail):
    body = resp.json()
    assert "detail" in body, f"Error response missing 'detail': {body}"
    assert body["detail"] == detail, f"Expected detail '{detail}', got '{body['detail']}'"
