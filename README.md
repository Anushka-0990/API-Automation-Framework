# Inventory API — Pytest + Requests API Automation Framework

A production-style **REST API test automation framework** for the **Inventory API**
(a FastAPI service bundled in `api_server/`). It demonstrates session-scoped service
bootstrapping, auth-token fixtures, response-schema validation, parameterized negative
testing, and CI on GitHub Actions.

> Built as a portfolio project demonstrating **Test Automation / API Testing** skills
> (Pytest, Requests, FastAPI, contract validation, CI).

---

## ✨ Features

| Capability | How it's implemented |
|---|---|
| Self-contained | Framework boots the FastAPI service itself — no manual server start |
| Auth handling | `auth_token` / `auth_headers` fixtures; tokens never hardcoded in tests |
| Contract validation | `utils/validators.py` — reusable schema checks for product responses |
| Happy + unhappy paths | 200/201/204 flows, 401 (auth), 404 (missing), 422 (validation) |
| Data-driven negatives | `@pytest.mark.parametrize` with 4 malformed payloads |
| Markers | `@pytest.mark.smoke` / `@pytest.mark.regression` |
| HTML report | `pytest-html` → `reports/report.html` |
| CI | GitHub Actions runs the suite on every push/PR |

## 🏗️ Architecture

```
  tests/test_health.py      tests/test_auth.py      tests/test_products.py
         └───────────────────────┬───────────────────────┘
                                 │ requests + fixtures
                ┌────────────────▼────────────────┐
                │   conftest.py                   │
                │  api_server (session boot)      │
                │  auth_token / auth_headers      │
                └────────────────────────────────┘
                                 │ HTTP (JSON, Bearer token)
                ┌────────────────▼────────────────┐
                │  Inventory API (FastAPI +       │
                │  uvicorn, in-memory data)       │  ← the AUT
                └─────────────────────────────────┘

  utils/validators.py → shared schema assertions (single source of truth)
```

## 📁 Project structure

```
api-automation-framework/
├── api_server/
│   ├── __init__.py
│   └── app.py                  # Inventory API (FastAPI) — auth + products CRUD
├── tests/
│   ├── test_health.py          # liveness
│   ├── test_auth.py            # login happy paths, 401s, 422, token validity
│   └── test_products.py        # CRUD, validation, auth guards, edge cases
├── utils/
│   └── validators.py           # assert_valid_product, assert_error_detail
├── conftest.py                 # api_server, base_url, auth_token, auth_headers
├── pytest.ini
├── requirements.txt
└── .github/workflows/ci.yml
```

## 🚀 Quick start

**Prerequisite:** Python 3.10+

```bash
git clone https://github.com/<you>/api-automation-framework
cd api-automation-framework
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest                                  # full suite (server auto-starts)
pytest -m smoke                         # smoke slice only
pytest --html=reports/report.html --self-contained-html   # + HTML report
```

## 📡 API under test

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/health` | — | Liveness check |
| POST | `/auth/login` | — | `{username, password}` → bearer token |
| GET | `/products` | ✅ | List products |
| GET | `/products/{id}` | ✅ | Get one (404 if missing) |
| POST | `/products` | ✅ | Create (201, validates body → 422) |
| PUT | `/products/{id}` | ✅ | Replace (404 if missing) |
| DELETE | `/products/{id}` | ✅ | Delete (204, 404 if missing) |

Interactive docs when running locally: `http://127.0.0.1:8080/docs`

## 📊 Test results

| File | Tests | Covers |
|---|---|---|
| `test_health.py` | 1 | service liveness + payload |
| `test_auth.py` | 6 | valid logins (parametrized), bad password 401, unknown user 401, missing field 422, token works on protected route |
| `test_products.py` | 12 | list, get, get-missing 404, create+fetch round-trip, 4× invalid payloads 422, update, update-missing 404, delete, delete-missing 404, no-token 401, bad-token 401 |

## 🧠 QA decisions baked into the framework

- **Fixtures over helpers** — `auth_headers` means every test gets a working token with one line, and the login logic lives in exactly one place.
- **Validation errors as tests** — 422 responses prove the API's *contract* (Pydantic constraints), not just its behavior.
- **Round-trip assertions** — create, then fetch, then compare the full body: catches field drops and silent mutations.
- **Smoke/regression split** — CI can gate PRs on smoke and run regression nightly.
- **No sleeps, port-wait only** — the server fixture waits on the TCP port, so parallel/CI environments don't race.
