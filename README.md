# Authentication & Access Control Audit

A local-only Flask portfolio project demonstrating secure authentication and authorization patterns for Web Application Security / VAPT learning.

## Purpose & Learning Objectives

- Implement session-based authentication with secure defaults
- Enforce horizontal authorization (user data isolation)
- Enforce vertical authorization (role-based access control)
- Apply CSRF protection on all state-changing endpoints
- Add security headers via middleware
- Validate and sanitize user inputs
- Write automated security tests

## Features & Security Controls

| Control | Implementation |
|---------|----------------|
| Authentication | Flask signed-cookie sessions and Werkzeug password hashing |
| Login/Logout | `POST /login` and `POST /logout` with CSRF tokens |
| Horizontal Authorization | Ownership checks on record routes (`GET`, `PUT`, `DELETE`) |
| Vertical Authorization | `@admin_required` decorator for admin-only routes |
| CSRF Protection | Flask-WTF `CSRFProtect` |
| Security Headers | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy` |
| Input Validation | Type and presence checks; rejects null, non-string, and empty titles |
| Session Fixation Prevention | `session.clear()` on login |
| Role Tampering Detection | Session cleared when a role mismatch is detected |

## Technology Stack

- Python 3.13
- Flask 3.1.3
- Flask-WTF 1.3.0
- Werkzeug 3.1.9
- pytest 9.1.1

## Local Setup (Windows PowerShell)

### 1. Clone the repository

```powershell
git clone https://github.com/samihathecss/auth-access-control-audit.git
cd auth-access-control-audit
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the application

```powershell
.\.venv\Scripts\python.exe app.py
```

The application is intended to run locally at `http://127.0.0.1:5000`.

### 5. Run the automated tests

Open another PowerShell terminal in the project directory and run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

## Test Results

**Latest recorded result: 37 tests passed.**

The recorded test run completed successfully with exit status `0`. See `evidence/pytest-final.txt` for the captured output.

### Automated Test Categories

| Category | Tests |
|----------|------:|
| Authentication and session handling | 7 |
| Horizontal authorization (user isolation) | 8 |
| Vertical authorization (admin vs. user) | 3 |
| CSRF protection | 8 |
| Input validation | 7 |
| Security headers | 1 |
| Unauthenticated access rejection | 5 |
| **Total executed tests** | **37** |

The automated suite contains 37 executed tests. Separately, `docs/test-plan.md` documents 32 planned test cases. These are different counts and should not be interpreted as a discrepancy.

## Documentation and Evidence

- `docs/security-assessment-report.md` — Security assessment report, findings, and recommendations
- `docs/test-plan.md` — Planned test cases across seven categories
- `docs/app-design.md` — Application architecture and route table
- `evidence/pytest-final.txt` — Captured automated test output
- `evidence/pytest-access-control.txt` — Additional test evidence

## Synthetic Accounts (Local-Only)

The application uses synthetic accounts and data for local testing. Plaintext demo passwords are intentionally not published in this README.

A separate local-only setup guide for demo credentials still needs to be created. Do not use synthetic lab credentials for real accounts or production systems.

| Username | Role |
|----------|------|
| `alice` | `user` |
| `bob` | `user` |
| `admin` | `admin` |

## Limitations

- Designed for a local-only synthetic environment and intended to bind to `127.0.0.1`
- Uses in-memory data structures; application data is not persistently stored
- Does not implement rate limiting, audit logging, or concurrent-session controls
- Uses client-side signed-cookie sessions rather than a server-side session store
- Does not enforce password complexity
- Is not a production-ready application

## Disclaimer

This is an educational portfolio project demonstrating secure coding patterns and authorization testing. It:

- Uses synthetic accounts and data
- Is intended for local testing only
- Does not target external systems
- Does not claim production readiness or compliance
- Is not evidence of a client engagement or a real-world penetration test

---

*Test status reflects the latest recorded local run; rerun the suite to verify the current code state.*
