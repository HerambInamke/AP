# Changes (by file)

## Backend
| File | Change |
|---|---|
| `app/routes/dashboard.py` | Rewritten: org from token, min-5 rule + "Other teams", per-person averages, risks counted per person from visible groups only, single maturity scale, one joined query |
| `app/routes/reports.py` | `DELETE /reports/me` (right to delete) |
| `app/routes/diagnostic.py` | Submit validates against the user's own questions, rejects missing/duplicate/empty/foreign answers, caps lengths, retake replaces old answers |
| `app/routes/auth_routes.py` | `select-org` checks membership |
| `app/auth.py` | Salted PBKDF2 hashing, constant-time compare |
| `app/services/questions.py` | Seniority compared by rank |
| `app/services/scoring.py` | `parse_score()`: strips fences, validates score 1–5 int, whitelists flags, survives LLM errors |
| `app/services/llm.py` | Prompt fences the answer as data (injection hardening), `temperature: 0` |
| `app/config.py` | `APP_ENV`, `CORS_ORIGINS`, `MIN_GROUP_SIZE`; refuses the default secret in production |
| `app/main.py` | CORS from config |
| `app/seed.py` | +3 Support employees and more responses (demo shows the min-5 rule); password hashed once per seed |
| `Dockerfile`, `.dockerignore` | Correct entrypoint (`app.main:app`), layer-cached deps, no `.env`/DB in image |
| `.env` → `.env.example` | Secrets untracked |
| `app/services/risks.py` | **Own feature:** risk catalog (label, team action, personal action); source of the allowed AI flags |
| `app/routes/dashboard.py` | **Own feature:** `top_risks[]` gains `label`, `share`, `teams` (visible only), `action` |
| `app/routes/reports.py` | **Own feature:** `risks[]` are `{risk, label, action}` |

## Tests (8 → 40, all passing)
- `test_api.py`: isolation (cross-org, select-org, roles, org-less token), min-5 pooling, risks, overall, per-person average, delete, submit validation, retake, password salting
- `test_scoring.py`: every malformed mock response + LLM failure + every flag has label and actions
- Own feature: risk teams/share/action on the dashboard, hidden departments never listed, personal actions in the report
- `test_questions.py`: lead-seniority regression
- `conftest.py`: temp DB, `full_answers()` helper

## Frontend
| File | Change |
|---|---|
| `pages/Dashboard.jsx` | Real table, "Other teams" row, privacy note, "Top risks and what to do" table (risk, people %, where, action) |
| `pages/Report.jsx` | Delete my data (with confirm), Retake, empty state, each risk with "What to do" |
| `pages/Diagnostic.jsx` | All-answered check, submitting state, error display, labels linked to inputs |
| `App.jsx` | Log out, switch org, auto-logout on 401, employees with a report land on it |
| `api.js` | Survives non-JSON errors, emits `auth-expired` on 401 |
| `styles.css` | Table, danger/link buttons |

## Repo
- `.gitignore`: `.venv/`, `.env`, `graphify-out/`
- `docs/`: AUDIT, CHANGES, DECISIONS (+ ADR-001…007 in `docs/decisions/`), ARCHITECTURE, API, RUNBOOK, CLIENT_REQUEST_RESPONSE, APPROACH, AI_LOG, WALKTHROUGH
- `CHANGELOG.md`, `CLAUDE.md` (contributor/agent rules)
