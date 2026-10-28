# Changelog

## [Unreleased] - 2026-10-28

### Security
- Admins could read any organization's dashboard via `?org_id=`. Org now comes only from the token ([ADR-001](docs/decisions/ADR-001-org-scope-from-token.md)).
- `/auth/select-org` issued tokens for orgs the user doesn't belong to. Now returns 403.
- Passwords moved from unsalted SHA-256 to salted PBKDF2 ([ADR-006](docs/decisions/ADR-006-password-hashing.md)).
- `backend/.env` removed from version control; `.env.example` added. **Rotate the old secrets.**
- CORS restricted to `CORS_ORIGINS`; startup fails with the default `SECRET_KEY` in production.
- Employee answers fenced in the LLM prompt to reduce prompt injection.
- Login no longer reveals which emails have accounts through response time.
- Diagnostic endpoints are employee-only (admins got 200 before).

### Added
- Dashboard hides groups under 5 respondents and pools them into "Other teams" ([ADR-002](docs/decisions/ADR-002-minimum-group-size.md)).
- `DELETE /reports/me` and a "Delete my data" button ([ADR-003](docs/decisions/ADR-003-right-to-delete.md)).
- **Risk → action** (own feature): dashboard risks show people and %, the teams they're concentrated in (visible teams only) and a concrete team action; the employee report gives a personal action per risk. One risk catalog drives flags, labels and actions ([ADR-007](docs/decisions/ADR-007-risk-to-action.md)).
- Real dashboard UI, retake, log out, switch org.
- Config: `APP_ENV`, `CORS_ORIGINS`, `MIN_GROUP_SIZE`.
- 32 new tests (8 → 40).

### Fixed
- Leads were not shown senior questions (seniority compared alphabetically).
- Malformed LLM output crashed submissions or stored invalid scores and flags ([ADR-004](docs/decisions/ADR-004-untrusted-ai-output.md)).
- Department average divided by headcount instead of respondents.
- Dashboard and personal report used different maturity scales.
- Retakes duplicated answers; foreign, partial and empty submissions were accepted ([ADR-005](docs/decisions/ADR-005-submission-rules.md)).
- Dockerfile pointed at the wrong module (`main:app`).
- Tests wrote `test.db` into the working directory.
- Vite silently switched to another port, which the CORS rule then blocked (`strictPort: true`).

### Changed
- `GET /dashboard` no longer takes `org_id`.
- Top risks now count people, not answers, and only from visible groups.
- `GET /reports/me` → `risks` is a list of `{risk, label, action}` objects (was strings).
- Seed data: 3 more Northwind Support employees and more responses.
