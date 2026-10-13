# Application Design — Authentication & Access Control Audit

**Project:** Authentication & Access Control Audit
**Version:** 1.0 (First-Version Scope)
**Tech Stack:** Flask 3.x, Python 3.13, pytest
**Scope:** Local-only, synthetic data, portfolio project

---

## 1. Synthetic Accounts

| Username | Role | Password (synthetic) | Purpose |
|----------|------|---------------------|---------|
| `alice` | `user` | `Secret123!` | Regular user, owns records A1, A2 |
| `bob` | `user` | `Secret123!` | Regular user, owns records B1, B2 |
| `admin` | `admin` | `AdminPass456!` | Administrator, full access |

> **Note:** Passwords are synthetic placeholders for local testing only. No real secrets or user data.

---

## 2. Authentication Mechanism

- **Type:** Session-based authentication using Flask's signed cookie session (`flask.session`)
- **Login:** `POST /login` — validates credentials, sets `session["user_id"]` and `session["role"]`
- **Logout:** `POST /logout` — clears session, redirects to login
- **Session data:** `user_id` (string), `role` (`user` or `admin`)
- **Protection:** `@login_required` decorator checks `session.get("user_id")`
- **CSRF:** Flask-WTF CSRF protection on state-changing routes (deferred to secured version)

---

## 3. Protected Dashboard

- **Route:** `GET /dashboard`
- **Auth:** Required (`@login_required`)
- **Content:** Shows current user's username, role, and link to their records
- **Behavior:** Redirects to `/login` if unauthenticated

---

## 4. Private Records

### Data Model (in-memory for v1)
```python
RECORDS = {
    "A1": {"id": "A1", "owner": "alice", "title": "Alice's Note 1", "content": "..."},
    "A2": {"id": "A2", "owner": "alice", "title": "Alice's Note 2", "content": "..."},
    "B1": {"id": "B1", "owner": "bob", "title": "Bob's Note 1", "content": "..."},
    "B2": {"id": "B2", "owner": "bob", "title": "Bob's Note 2", "content": "..."},
}
```

### Record Routes
| Route | Method | Auth | Ownership Check | Purpose |
|-------|--------|------|-----------------|---------|
| `/records` | GET | Required | Filter by `session["user_id"]` | List current user's records |
| `/records/<id>` | GET | Required | `record["owner"] == session["user_id"]` | View single record |
| `/records` | POST | Required | Auto-assign `owner = session["user_id"]` | Create record |
| `/records/<id>` | PUT | Required | `record["owner"] == session["user_id"]` | Update own record |
| `/records/<id>` | DELETE | Required | `record["owner"] == session["user_id"]` | Delete own record |

---

## 5. Horizontal Authorization (User Isolation)

- **Rule:** A user may only access records where `record["owner"] == session["user_id"]`
- **Enforcement:** Every record route verifies ownership before read/write/delete
- **Failure:** Returns HTTP 403 (Forbidden) or 404 (Not Found) — no data leakage
- **Testable:** Pytest can assert alice cannot GET/PUT/DELETE bob's records

---

## 6. Vertical Authorization (Role-Based Access)

| Role | Dashboard | Own Records | Admin Panel | Admin Actions |
|------|-----------|-------------|-------------|---------------|
| `user` (alice, bob) | ✅ | ✅ (own only) | ❌ 403 | ❌ 403 |
| `admin` | ✅ | ✅ (all) | ✅ | ✅ |

### Admin-Only Routes
| Route | Method | Auth | Role Check | Purpose |
|-------|--------|------|------------|---------|
| `/admin` | GET | Required | `session["role"] == "admin"` | Admin dashboard |
| `/admin/users` | GET | Required | `session["role"] == "admin"` | List all users |
| `/admin/users/<id>` | DELETE | Required | `session["role"] == "admin"` | Delete user |
| `/admin/records` | GET | Required | `session["role"] == "admin"` | View all records |

---

## 7. Route Table

| Method | Route | Purpose | Auth Required | Role/Ownership Check |
|--------|-------|---------|---------------|---------------------|
| GET | `/` | Home / redirect to dashboard or login | No | — |
| GET | `/login` | Show login form | No | — |
| POST | `/login` | Process login | No | Credentials validation |
| POST | `/logout` | Destroy session | Yes | — |
| GET | `/dashboard` | User dashboard | Yes | `@login_required` |
| GET | `/records` | List own records | Yes | Owner filter |
| POST | `/records` | Create record | Yes | Auto-assign owner |
| GET | `/records/<id>` | View record | Yes | Owner match |
| PUT | `/records/<id>` | Update record | Yes | Owner match |
| DELETE | `/records/<id>` | Delete record | Yes | Owner match |
| GET | `/admin` | Admin dashboard | Yes | `role == "admin"` |
| GET | `/admin/users` | List all users | Yes | `role == "admin"` |
| DELETE | `/admin/users/<id>` | Delete user | Yes | `role == "admin"` |
| GET | `/admin/records` | View all records | Yes | `role == "admin"` |
| GET | `/health` | Health check | No | — |

---

## 8. Vulnerable vs Secured Version

### Vulnerable Version (Intentional Flaws for Learning)
| Flaw | Description |
|------|-------------|
| **Missing ownership checks** | Record routes skip `owner == session["user_id"]` verification |
| **Missing role checks** | Admin routes lack `@admin_required` decorator |
| **IDOR** | `/records/<id>` returns any record by ID regardless of owner |
| **Vertical bypass** | Regular user can access `/admin` and `/admin/*` routes |
| **No CSRF protection** | State-changing POST/PUT/DELETE lack CSRF tokens |
| **Session fixation** | Session ID not regenerated on login |
| **Verbose errors** | Stack traces expose internal structure |

### Secured Version (Fixes Applied)
| Fix | Implementation |
|-----|----------------|
| Ownership enforcement | Every record route calls `check_ownership(record, session["user_id"])` |
| Role enforcement | `@admin_required` decorator on all admin routes |
| IDOR prevention | Routes return 403/404 when ownership mismatches |
| Vertical authz | Admin routes verify `session["role"] == "admin"` |
| CSRF protection | Flask-WTF CSRF on all mutating routes |
| Session regeneration | `session.clear(); session["user_id"] = ...` on login |
| Generic errors | Custom error handlers, no stack traces in production |

> **Important:** This design documents *planned* differences. No vulnerabilities have been tested or discovered in this project. The vulnerable version exists only as a design concept for educational comparison.

---

## 9. Postponed Features (Out of v1 Scope)

| Feature | Reason |
|---------|--------|
| Password reset / forgot password | Requires email or token infrastructure |
| Account lockout after failed attempts | Requires persistent attempt tracking |
| Inactivity session timeout | Requires session timestamp tracking |
| Concurrent session management | Requires server-side session store |
| Password hashing (bcrypt/argon2) | v1 uses plaintext comparison for simplicity; will upgrade |
| Rate limiting | Requires Flask-Limiter or similar |
| Audit logging | Requires structured logging setup |
| HTTPS / TLS | Local-only `127.0.0.1`; not applicable |
| Database persistence | v1 uses in-memory dict; SQLite/PostgreSQL later |
| Multi-factor authentication | Out of scope for beginner portfolio |

---

## 10. Local-Only Development Requirements

- **Bind address:** `127.0.0.1` only (never `0.0.0.0`)
- **Port:** `5000` (default Flask)
- **Data:** Synthetic in-memory only (`RECORDS` dict, `USERS` dict)
- **No external dependencies:** No database, no email, no external APIs
- **No external targets:** Tests run only against local server
- **Environment variable:** `FLASK_ENV=development`
- **Run command:**
  ```powershell
  .\.venv\Scripts\python.exe app.py
  ```

---

## 11. Testability Design (pytest)

### Fixtures (planned for `tests/conftest.py`)
```python
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def alice_session(client):
    client.post("/login", data={"username": "alice", "password": "Secret123!"})
    yield client

@pytest.fixture
def bob_session(client):
    client.post("/login", data={"username": "bob", "password": "Secret123!"})
    yield client

@pytest.fixture
def admin_session(client):
    client.post("/login", data={"username": "admin", "password": "AdminPass456!"})
    yield client
```

### Test Categories (mapped to test-plan.md)
| Test File | Coverage |
|-----------|----------|
| `test_auth.py` | Login, logout, session validation |
| `test_horizontal.py` | Alice vs Bob record isolation (TC-14–TC-18) |
| `test_vertical.py` | User vs Admin access control (TC-19–TC-23) |
| `test_unauthenticated.py` | Unauthenticated access rejection (TC-01–TC-03) |
| `test_direct_requests.py` | curl-style direct HTTP (TC-24–TC-27) |
| `test_regression.py` | Fix verification (TC-28–TC-32) |

### Assertion Patterns
```python
# Horizontal: alice cannot access bob's record
def test_alice_cannot_read_bob_record(alice_session):
    resp = alice_session.get("/records/B1")
    assert resp.status_code in (403, 404)

# Vertical: user cannot access admin
def test_user_cannot_access_admin(alice_session):
    resp = alice_session.get("/admin")
    assert resp.status_code == 403

# Unauthenticated: redirect to login
def test_dashboard_requires_login(client):
    resp = client.get("/dashboard", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
```

---

## 12. Project Structure (v1)

```
auth-access-control-audit/
├── app.py                 # Entry point (unchanged from Milestone 2 Task 1)
├── .gitignore
├── app/
│   ├── __init__.py        # Flask app factory, config
│   ├── auth.py            # Login/logout, decorators (@login_required, @admin_required)
│   ├── records.py         # Record routes with ownership checks
│   ├── admin.py           # Admin routes with role checks
│   └── models.py          # In-memory USERS, RECORDS dicts
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Pytest fixtures
│   ├── test_auth.py
│   ├── test_horizontal.py
│   ├── test_vertical.py
│   ├── test_unauthenticated.py
│   ├── test_direct_requests.py
│   └── test_regression.py
├── docs/
│   ├── README.md
│   ├── test-plan.md
│   └── app-design.md      # This file
└── evidence/
    └── README.md
```

---

## 13. Implementation Order (v1)

1. **app/models.py** — Synthetic `USERS` and `RECORDS` data
2. **app/auth.py** — Login, logout, `@login_required`, `@admin_required`
3. **app/records.py** — Record CRUD with ownership enforcement
4. **app/admin.py** — Admin routes with role enforcement
5. **app/__init__.py** — App factory, register blueprints
6. **app.py** — Update to use factory (keep `/health` working)
7. **tests/conftest.py** — Pytest fixtures
8. **tests/test_*.py** — Implement test plan cases

---

## 14. Security Notes for Portfolio

- This project **intentionally designs** a vulnerable version for educational comparison
- The **secured version** demonstrates proper authorization patterns
- All testing is **local-only** with synthetic data
- No real vulnerabilities are exploited or disclosed
- Evidence folder collects test outputs, not exploit proofs
- Designed to showcase: authorization testing, pytest, Flask patterns, secure coding

---

*End of Application Design v1.0*
