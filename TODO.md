# TODO

AI Pulse: employees take an AI-usage diagnostic (MCQ + one LLM-scored open answer) → personal report; admins see a per-department dashboard. FastAPI + SQLAlchemy + React/Vite. Status as of 2026-10-28. Details: `docs/AUDIT.md`.

## 0. Assessment 
- [x] **Own feature: Risk → action** built, tested, ADR-007, README section
- [x] Rewrite `docs/AI_LOG.md` in plain first-person voice (read it through before submitting)
- [ ] **Rotate** `SECRET_KEY` / LLM key (they're in git history)
- [ ] Commit in small steps (keep history), push to your fork
- [x] Verify the Docker build with Docker Desktop running
- [ ] Record ≤5 min using `docs/WALKTHROUGH.md`, submit at forms.gle/rmTKe6ZLw7fqPFNZ9
- [ ] Prep for the live session: be able to explain and change every fix without AI

**Own feature (pick one, keep it small):**
- *Retake trend*: employee sees before/after, leadership sees each team's change. Needs submission history (today a retake replaces).
- *Risk → action*: each dashboard risk shows how many teams it affects (still applying min-5) plus a concrete policy step.

## 1. Client asks ✅
- [x] Min group size 5 → "Other teams" pool, hidden if still <5; risks + overall only from visible people
- [x] Right to delete: `DELETE /reports/me` + button; dashboards update immediately
- [x] Tests for both

## 2. Security / privacy ✅
- [x] Cross-org dashboard leak (org from token; test fixed)
- [x] `select-org` membership check
- [x] Salted PBKDF2 passwords
- [x] `.env` untracked, `.env.example` added (rotation still pending, see §0)
- [x] Default `SECRET_KEY` refused in production
- [x] CORS restricted
- [x] Prompt-injection hardening + output validation

## 3. Correctness ✅
- [x] Seniority rank (was string compare)
- [x] Robust LLM parsing: unscored on bad output, flag whitelist, LLM errors don't fail submit
- [x] Per-person department averages
- [x] One maturity scale
- [x] Submit validation (own questions, complete, no dups/empties); retake replaces

## 4. Infra
- [x] Dockerfile entrypoint + `.dockerignore` (build + run verified)
- [x] Tests on a temp DB
- [x] Dashboard single query
- [ ] `datetime.utcnow` deprecation (low)

## 5. Frontend ✅
- [x] Real dashboard table + risks
- [x] Diagnostic validation / loading / error / double-submit guard
- [x] `api.js` error handling, logout, 401 → login, switch org
- [x] Employees with a report land on it; Retake; delete
- [ ] Admins can't take the diagnostic (product question for client)

## 6. Docs / proof ✅
- [x] README (+ architecture, docs index, contributing), `docs/` (AUDIT, CHANGES, CLIENT_REQUEST_RESPONSE, APPROACH, AI_LOG, WALKTHROUGH)
- [x] ADR-001…007 (`docs/decisions/`), ARCHITECTURE, API (real examples), RUNBOOK (snippets verified), CHANGELOG, CLAUDE.md
- [x] 40 tests passing; manual browser runs of all roles

## Found on re-test
- [x] Vite port fallback broke login under the new CORS rule → `strictPort: true`
- [x] Admin can submit the diagnostic via API → employee-only
- [x] Login timing revealed which emails exist → dummy hash
- [ ] Dashboard differencing over time (design limit; asked the client)
- [ ] LLM call blocks submit up to 60s (low; background job if needed)
- [ ] No frontend automated tests

## Left on purpose (see AUDIT.md)
Login rate limiting · token revocation / httpOnly cookies · Alembic migrations · deletion audit log · live-LLM test against a real provider.
