# Security Assessment Report

**Project:** Authentication & Access Control Audit
**Type:** Local-only portfolio project (educational)
**Date:** 2026-10-13
**Assessor:** Portfolio author (self-assessment)

---

## 1. Assessment Objective

Evaluate the authentication and authorization controls of a minimal Flask application designed to demonstrate secure coding practices for a Web Application Security / VAPT portfolio. The assessment is limited to local testing with synthetic accounts and data.

---

## 2. Scope

| In Scope | Out of Scope |
|----------|--------------|
| Flask application code (`app/`) | Production deployment, TLS, WAF, infrastructure |
| Test suite (`tests/test_access_control.py`) | Third-party library vulnerabilities |
| Session-based authentication | Password reset, MFA, rate limiting |
| Record ownership authorization (CRUD) | Database persistence, backup, recovery |
| Admin role-based access control | Concurrent session management |
| CSRF protection on state-changing endpoints | External penetration testing |
| Security headers middleware | Social engineering, physical security |
| Input validation on record creation/update | Client-side security |

**Test Environment:**
- Windows 10, Python 3.13.16, Flask 3.1.3
- Virtual environment at `.venv/`
- Server bound to `127.0.0.1:5000` only
- Synthetic accounts: `alice` (user), `bob` (user), `admin` (admin)
- In-memory data structures only (`app/models.py`)

---

## 3. Methodology

1. **Static code review** of all application modules (`app/__init__.py`, `app/auth.py`, `app/records.py`, `app/admin.py`, `app/models.py`)
2. **Automated test execution** via pytest (37 tests) covering authentication, authorization, CSRF, input validation, and security headers
3. **Adversarial test-case verification** using Flask test client to manually exercise:
   - IDOR/BOLA across GET, POST, PUT, DELETE
   - Mass assignment attempts
   - Session/role tampering
   - Malformed input handling
   - Security header presence
   (Results confirmed by automated regression tests)

---

## 4. Tested Security Controls

| Control | Implementation | Verified By |
|---------|----------------|-------------|
| Session-based authentication | Signed Flask cookies, `session["user_id"]`, `session["role"]` | 7 tests |
| Login/logout flow | `POST /login`, `POST /logout` with CSRF | 5 tests |
| Record ownership (horizontal authz) | Owner check on every record route | 8 tests |
| Admin role (vertical authz) | `@admin_required` decorator | 3 tests |
| CSRF protection | Flask-WTF `CSRFProtect` global | 8 tests |
| Security headers | `after_request` middleware (4 headers) | 1 test |
| Input validation | Type/presence checks on title | 7 tests |
| Session fixation prevention | `session.clear()` on login | 1 test |
| Role tampering detection | `admin_required` clears session | 1 test |

---

## 5. Findings

### 5.1 Remediated Issue: Input Validation Defect (CVE-None, Internal)

| Field | Value |
|-------|-------|
| **Title** | Null/Non-String Title Causes Unhandled Exception (500) |
| **Severity** | Medium — Local DoS via malformed request (qualitative assessment; no formal CVSS calculated) |
| **Component** | `app/records.py` — `create_record()` and `update_record()` |
| **Reproduction** | Send `POST /records` or `PUT /records/<id>` with JSON `{"title": null, "content": "x"}` or `{"title": 123, "content": "x"}` with valid CSRF token and authenticated session |
| **Expected** | HTTP 400 with validation error |
| **Actual (Before Fix)** | `AttributeError: 'NoneType' object has no attribute 'strip'` → HTTP 500 |
| **Impact** | Authenticated users could trigger server errors; potential DoS; error stack traces could leak internals if debug enabled |
| **Remediation** | Added `isinstance(title, str)` and `title.strip()` validation before processing; returns 400 "Title is required" |
| **Verification** | Tests `test_create_record_rejects_null_title`, `test_create_record_rejects_non_string_title`, `test_update_record_rejects_null_title`, `test_update_record_rejects_non_string_title` — all pass |

> **Status:** **REMEDIATED** — Fixed in commit prior to final test run. No longer exploitable.

---

### 5.2 Code-Review Observations (Not Exploitable in Current Scope)

| Observation | Component | Risk Context |
|-------------|-----------|--------------|
| Signed cookie sessions (client-side) | `app/__init__.py` | No server-side session store; session data in cookie. Acceptable for local portfolio; not suitable for production sensitive data. |
| `SESSION_COOKIE_SECURE=False` | `app/__init__.py` | Required for local HTTP testing; would need `True` for HTTPS production. |
| No rate limiting on `/login` | `app/auth.py` | Brute-force feasible locally; mitigated by synthetic-only scope. |
| Admin cannot access user records via `/records` API | `app/records.py` | By design per `docs/app-design.md`; admin has separate `/admin` panel (not implemented). |
| In-memory `RECORDS` dict | `app/models.py` | Data lost on restart; no persistence layer. |
| No audit logging | — | No record of authz decisions or failed attempts. |

---

## 6. Test Summary

| Metric | Value |
|--------|-------|
| Total tests | 37 |
| Passed | 37 |
| Failed | 0 |
| Exit status | 0 |
| Duration | ~5.5 seconds |
| Evidence file | `evidence/pytest-final.txt` |

**Test Categories:**
- Authentication & session: 7 tests
- Horizontal authorization (user isolation): 8 tests
- Vertical authorization (admin vs user): 3 tests
- CSRF protection: 8 tests
- Input validation: 7 tests
- Security headers: 1 test
- Unauthenticated access rejection: 5 tests

---

## 7. Limitations

1. **Local-only synthetic environment** — No network exposure, no real users, no production traffic patterns.
2. **No external dependency scanning** — Only Flask and stdlib used; no SAST/DAST tools run.
3. **No business logic testing beyond authorization** — No file upload, SSRF, XXE, deserialization, or template injection vectors exist.
4. **Client-side session storage** — Signed cookies expose session structure to client; not tested for tampering beyond role field.
5. **No password complexity enforcement** — Synthetic passwords only; no policy validation.
6. **No concurrent session limits** — Multiple logins per user allowed.

---

## 8. Responsible Use Statement

This project is an **educational portfolio artifact** demonstrating secure authentication and authorization patterns in Flask. It:

- Uses **only synthetic accounts and data**
- Runs **only on localhost (127.0.0.1)**
- **Does not target** any external system
- **Does not claim** production readiness or compliance with any standard
- Is intended for **learning and demonstration** purposes only

All findings are based on actual code review and automated test execution. No vulnerabilities were discovered in external systems. No exploit code or attack payloads are included beyond what is necessary to verify defensive controls.

---

*End of Report*
