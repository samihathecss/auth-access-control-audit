# Authentication & Access Control Audit

A local-only Flask portfolio project demonstrating secure authentication and authorization patterns for Web Application Security / VAPT learning.

## Purpose & Learning Objectives

- Implement session-based authentication with secure defaults
- Enforce horizontal authorization (user data isolation)
- Enforce vertical authorization (role-based access control)
- Apply CSRF protection on all state-changing endpoints
- Add security headers via middleware
- Validate and sanitize all user inputs
- Write comprehensive automated security tests

## Features & Security Controls

| Control | Implementation |
|---------|----------------|
| Authentication | Flask signed cookie sessions, password hashing (werkzeug) |
| Login/Logout | `POST /login`, `POST /logout` with CSRF tokens |
| Horizontal Authorization | Ownership checks on all record routes (GET, PUT, DELETE) |
| Vertical Authorization | `@admin_required` decorator for admin-only routes |
| CSRF Protection | Flask-WTF `CSRFProtect` global middleware |
| Security Headers | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy` |
| Input Validation | Type/presence checks; rejects null, non-string, empty titles |
| Session Fixation Prevention | `session.clear()` on login |
| Role Tampering Detection | Session cleared on role mismatch |

## Technology Stack

- Python 3.13
- Flask 3.1.3
- Flask-WTF 1.3.0 (CSRF)
- Werkzeug 3.1.9 (password hashing)
- pytest 9.1.1 (testing)

## Local Setup (Windows PowerShell)

```powershell
# 1. Clone and enter project
git clone <your-fork-url>
cd auth-access-control-audit

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
.\.venv\Scripts\python.exe app.py
# Server starts at http://127.0.0.1:5000

# 5. Run test suite
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

## Test Results

```
37 passed in ~5.5s (exit status 0)
```

**Test Categories:**
- Authentication & session: 7 tests
- Horizontal authorization (user isolation): 8 tests
- Vertical authorization (admin vs user): 3 tests
- CSRF protection: 8 tests
- Input validation: 7 tests
- Security headers: 1 test
- Unauthenticated access rejection: 5 tests

See `evidence/pytest-final.txt` for full output.

## Documentation

- `docs/security-assessment-report.md` — Full security assessment with findings
- `docs/test-plan.md` — 32 planned test cases across 7 categories
- `docs/app-design.md` — Application architecture and route table
- `evidence/pytest-final.txt` — Evidence of 37 executed automated tests

#### Synthetic Accounts (Local-Only)

| Username | Role |
|----------|------|
| `alice` | `user` |
| `bob` | `user` |
| `admin` | `admin` |

> **Note:** Demo credentials are intended for local testing only. A separate local-only setup guide still needs to be created. Plaintext passwords are intentionally omitted from this public README. Never reuse synthetic credentials in production.

> **Note:** These are synthetic credentials for local testing only. Never reuse in production.

## Limitations

- Local-only synthetic environment (binds to `127.0.0.1`)
- No database persistence — in-memory data structures
- No rate limiting, audit logging, or concurrent session controls
- Client-side signed cookie sessions (no server-side store)
- No password complexity enforcement
- Not a production-ready application

## Disclaimer

This is an **educational portfolio artifact** for demonstrating secure coding practices. It:

- Uses only synthetic accounts and data
- Runs only on localhost (`127.0.0.1`)
- Does not target any external system
- Does not claim production readiness or compliance
- Is intended for learning and demonstration purposes only

---

*Last verified: 37/37 tests passing*
