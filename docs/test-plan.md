# Authentication & Access Control Test Plan

**Project:** Authentication & Access Control Audit
**Scope:** Local-only testing with synthetic accounts
**Status:** Partially executed

---

## 1. Unauthenticated Access to Protected Pages

| ID | Objective | Required Account/Role | Action | Expected Secure Behavior | Evidence to Collect |
|----|-----------|----------------------|--------|-------------------------|---------------------|
| TC-01 | Verify protected routes reject unauthenticated requests | None (unauthenticated) | GET /dashboard, /profile, /admin/* | HTTP 401/403, redirect to login, no data leaked | Response code, headers, redirect location, response body |
| TC-02 | Verify API endpoints reject unauthenticated requests | None | GET /api/users, /api/records | HTTP 401, JSON error response | Response code, JSON error structure |
| TC-03 | Verify static assets in protected areas are not accessible | None | GET /protected/assets/* | HTTP 401/403 | Response code |

---

## 2. Valid and Invalid Login Attempts

| ID | Objective | Required Account/Role | Action | Expected Secure Behavior | Evidence to Collect |
|----|-----------|----------------------|--------|-------------------------|---------------------|
| TC-04 | Successful login with valid credentials | `user:alice / pass:Secret123!` | POST /login with valid credentials | HTTP 200/302, session cookie set, redirect to dashboard | Response code, Set-Cookie header, session ID format |
| TC-05 | Reject login with invalid password | `user:alice / pass:WrongPass` | POST /login with wrong password | HTTP 401, no session cookie, generic error message | Response code, absence of Set-Cookie, error message |
| TC-06 | Reject login with non-existent user | `user:unknown / pass:anything` | POST /login with unknown user | HTTP 401, same timing/error as TC-05 (no user enumeration) | Response code, timing consistency, error message |
| TC-07 | Reject login with empty credentials | None | POST /login with empty username/password | HTTP 400, validation error | Response code, validation error details |
| TC-08 | Account lockout after failed attempts | `user:alice` | 5+ failed POST /login attempts | Temporary lockout, HTTP 429 or consistent 401 | Response codes, lockout duration, headers |
| TC-09 | Password not logged or exposed | `user:alice` | POST /login (valid/invalid) | Password absent from logs, response bodies, URLs | Server logs, response bodies, network trace |

---

## 3. Logout and Session Invalidation

| ID | Objective | Required Account/Role | Action | Expected Secure Behavior | Evidence to Collect |
|----|-----------|----------------------|--------|-------------------------|---------------------|
| TC-10 | Logout terminates session | `user:alice` (authenticated) | POST /logout or GET /logout | Session destroyed, cookie cleared, redirect to login | Response code, Set-Cookie (expired), redirect |
| TC-11 | Session invalidated on server after logout | `user:alice` | 1. Login 2. Logout 3. Reuse old session cookie | HTTP 401 on subsequent requests with old cookie | Response code after logout with old cookie |
| TC-12 | Session expires after inactivity timeout | `user:alice` | Login, wait > timeout, make request | HTTP 401, session expired | Response code, timeout value |
| TC-13 | Concurrent sessions handled per policy | `user:alice` | Login from two browsers, logout from one | Policy: invalidate all / keep others | Session behavior in second browser |

---

## 4. Horizontal Authorization: User A vs User B Private Records

| ID | Objective | Required Account/Role | Action | Expected Secure Behavior | Evidence to Collect |
|----|-----------|----------------------|--------|-------------------------|---------------------|
| TC-14 | User cannot access another user's profile | `user:alice` (authenticated) | GET /profile/bob | HTTP 403/404, no data returned | Response code, response body |
| TC-15 | User cannot access another user's records via IDOR | `user:alice` | GET /api/records/42 (owned by bob) | HTTP 403/404 | Response code, response body |
| TC-16 | User cannot modify another user's data | `user:alice` | PUT /api/records/42 (owned by bob) | HTTP 403/404, no modification | Response code, verify data unchanged |
| TC-17 | User cannot delete another user's data | `user:alice` | DELETE /api/records/42 (owned by bob) | HTTP 403/404, no deletion | Response code, verify data exists |
| TC-18 | List endpoints filter by ownership | `user:alice` | GET /api/records | Returns only alice's records, not bob's | Response body, record count, ownership fields |

---

## 5. Vertical Authorization: Regular User vs Administrator Actions

| ID | Objective | Required Account/Role | Action | Expected Secure Behavior | Evidence to Collect |
|----|-----------|----------------------|--------|-------------------------|---------------------|
| TC-19 | Regular user cannot access admin panel | `user:alice` (role: user) | GET /admin/dashboard | HTTP 403/404 | Response code, response body |
| TC-20 | Regular user cannot call admin APIs | `user:alice` | GET /api/admin/users, POST /api/admin/* | HTTP 403 | Response code |
| TC-21 | Regular user cannot elevate privileges | `user:alice` | POST /api/users/alice/role with role=admin | HTTP 403, role unchanged | Response code, verify role in DB |
| TC-22 | Admin can access admin panel | `user:admin` (role: admin) | GET /admin/dashboard | HTTP 200, admin content | Response code, admin UI elements |
| TC-23 | Admin can perform admin actions | `user:admin` | POST /api/admin/users (create), DELETE /api/admin/users/42 | HTTP 200/201, action succeeds | Response code, verify side effects |

---

## 6. Direct HTTP Requests to Protected Routes

| ID | Objective | Required Account/Role | Action | Expected Secure Behavior | Evidence to Collect |
|----|-----------|----------------------|--------|-------------------------|---------------------|
| TC-24 | Direct GET to protected route without browser | None / `user:alice` | curl/wget /dashboard, /api/records | Same protection as browser: 401/403 or redirect | Raw HTTP response |
| TC-25 | Direct POST to state-changing endpoint | `user:alice` | curl -X POST /api/records with JSON | CSRF protection: 403 without token, 200 with | Response code, CSRF token behavior |
| TC-26 | Direct request with manipulated headers | `user:alice` | Add X-Forwarded-For, X-Original-URL, etc. | No bypass of authz checks | Response code, verify no bypass |
| TC-27 | HTTP method override attempts | `user:alice` | POST /api/records?_method=DELETE | Method override not honored or protected | Response code |

---

## 7. Regression Tests for Security Fixes

| ID | Objective | Required Account/Role | Action | Expected Secure Behavior | Evidence to Collect |
|----|-----------|----------------------|--------|-------------------------|---------------------|
| TC-28 | Fixed IDOR vulnerability remains fixed | `user:alice` | GET /api/records/42 (bob's) | HTTP 403/404 | Response code, compare to pre-fix behavior |
| TC-29 | Fixed privilege escalation remains fixed | `user:alice` | POST /api/users/alice/role=admin | HTTP 403 | Response code, verify role unchanged |
| TC-30 | Fixed session fixation remains fixed | None | 1. Get session ID 2. Login 3. Check session ID changed | New session ID issued on login | Session ID before/after login |
| TC-31 | Fixed password reset token reuse remains fixed | `user:alice` | Use same reset token twice | Second use rejected | Response codes, token invalidated |
| TC-32 | Fixed missing authz on new endpoints | `user:alice` | Access newly added protected endpoints | All new endpoints enforce authz | Response codes for each new endpoint |

---

## Test Execution Notes

- **Synthetic accounts:** `alice` (regular user), `bob` (regular user), `admin` (administrator)
- **Environment:** Local development only (`http://127.0.0.1:5000`)
- **Tools:** `curl`, `httpie`, browser dev tools, pytest (when implemented)
- **Evidence format:** Screenshots, raw HTTP request/response logs, server logs, database state snapshots
- **Status tracking:** Each test case starts as **PLANNED** â†’ **EXECUTED** â†’ **PASS/FAIL** with evidence attached

---

## Distinguishing Planned vs Executed Tests

| Status | Meaning |
|--------|---------|
| `PLANNED` | Test designed, not yet run |
| `EXECUTED` | Test run, result recorded |
| `PASS` | Expected secure behavior observed |
| `FAIL` | Vulnerability or misconfiguration found |
| `BLOCKED` | Cannot run due to missing implementation |

The numbered test cases above remain **PLANNED** until individually executed and documented. Seven original access-control checks and one additional automated regression test have passed locally; see the execution record below. These checks do not establish that the application is fully secure.
---

## Local Execution Record

**Environment:** Flask test client; synthetic accounts and records
**Evidence source:** Terminal output from local test runs

| Check | Action | Actual Result | Status |
|---|---|---|---|
| LAC-01 | Unauthenticated GET `/records/A1` | HTTP 302 | PASS |
| LAC-02 | Alice GET `/records/A1` | HTTP 200 | PASS |
| LAC-03 | Alice GET `/records/B1` | HTTP 404 | PASS |
| LAC-04 | Alice GET `/records` | Only A1 and A2 returned | PASS |
| VAC-01 | Unauthenticated GET `/admin` | HTTP 302 | PASS |
| VAC-02 | Alice GET `/admin` | HTTP 403 | PASS |
| VAC-03 | Admin GET `/admin` | HTTP 200 | PASS |
| VAC-04 | Alice session claims admin role | HTTP 403; session cleared | PASS |

**Interpretation:** The seven original checks and one additional inconsistent-session regression check produced their expected results in the local test environment. The eight automated tests are recorded in `evidence/pytest-access-control.txt`. The numbered test cases above have not automatically passed simply because these related checks passed. Additional cases, including CSRF protection, session security, and rate limiting, still require implementation or testing as applicable.
