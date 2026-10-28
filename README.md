# AI Pulse

AI Pulse helps a company understand how well its people use AI at work, team by team.

- **Employees** sign in, pick their organization, and take a short diagnostic. Questions adapt to their job role and seniority. One open-ended answer is scored by an LLM.
- **Each employee** gets a personal report (maturity level, risks, next steps for their role) and can **delete their data** at any time.
- **Company admins** see a dashboard of AI maturity by department and the top risks. To protect individuals, **no group with fewer than 5 respondents is ever shown on its own**.
- Some users (consultants, group-company HR) belong to **more than one organization** and choose one after login. Each session only ever sees the selected organization's data.

## Stack

- Backend: Python 3.12/3.13, FastAPI, SQLAlchemy (SQLite by default)
- Frontend: React (Vite)
- AI: any OpenAI-compatible chat completions endpoint, or mock mode with canned responses

## Run it locally

You need **Python 3.12 or 3.13** and Node 18+. Python 3.14 does **not** work: the pinned pydantic has no 3.14 wheels, so `pip install` fails. If 3.14 is your default `python`, a plain `python -m venv` creates a broken 3.14 venv, so pick the version explicitly as shown below.

Use two terminals: one for the backend, one for the frontend.

### Backend (terminal 1)

Windows (PowerShell):

```powershell
cd backend
py -0                                  # lists installed Pythons; you need 3.12 or 3.13
py -3.13 -m venv .venv                 # or: py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1             # cmd.exe: .venv\Scripts\activate.bat
python --version                       # must print 3.12.x or 3.13.x
pip install -r requirements.txt
copy .env.example .env                 # optional; defaults work for local dev
python -m app.seed                     # demo data, password for all users: pulse123
uvicorn app.main:app --reload          # http://localhost:8000
```

If `Activate.ps1` is blocked ("running scripts is disabled"), run this once and try again: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

macOS / Linux:

```bash
cd backend
python3.13 -m venv .venv && source .venv/bin/activate   # or python3.12
python --version                       # must print 3.12.x or 3.13.x
pip install -r requirements.txt
cp .env.example .env                   # optional
python -m app.seed
uvicorn app.main:app --reload
```

Check it's up: open http://localhost:8000/health.

### Frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev                            # http://localhost:5173
```

Open http://localhost:5173 and sign in as `asha@northwind.test` / `pulse123`.

### Troubleshooting

| Symptom | Fix |
|---|---|
| `pip install` fails building `pydantic-core`, or `python --version` says 3.14 | The venv was made with 3.14. Delete `backend/.venv` and recreate it with `py -3.13 -m venv .venv` (or `python3.13`). |
| `ImportError: cannot import name ... from 'sqlalchemy' (unknown location)` | A half-finished install, usually because two installs ran at once. Delete `.venv`, recreate it and run `pip install` once. |
| `ModuleNotFoundError: No module named 'fastapi'` | The venv isn't active. Activate it (see above) and check `python --version`. |
| `Port 5173 is in use` | Another dev server is running. Close it. The port is fixed on purpose because the backend only allows `http://localhost:5173` (CORS). |
| Login says "Failed to fetch" | The backend isn't running on port 8000, or the frontend isn't on `http://localhost:5173`. |
| http://localhost:8000/health shows a "404 File not found" HTML page | Another program (e.g. `python -m http.server 8000`) also holds port 8000 and is answering `localhost`. Stop it, or run the backend on another port and point the frontend at it: `uvicorn app.main:app --reload --port 8001`, then in PowerShell `$env:VITE_API_URL="http://127.0.0.1:8001"; npm run dev` (bash: `VITE_API_URL=http://127.0.0.1:8001 npm run dev`). |
| Login fails for demo users | Run `python -m app.seed` (it **drops all tables** and recreates the demo data). |

Tests (40, use a throwaway temp database):

```bash
cd backend
python -m pytest
```

Docker (backend):

```bash
cd backend
docker build -t aipulse-api .
docker run -p 8000:8000 -e SECRET_KEY=change-me aipulse-api sh -c "python -m app.seed && uvicorn app.main:app --host 0.0.0.0"
```

## Configuration (`backend/.env`, see `.env.example`)

| Variable | Default | Notes |
|---|---|---|
| `SECRET_KEY` | dev value | **Required** when `APP_ENV=production` (startup fails otherwise) |
| `APP_ENV` | `dev` | `dev` or `production` |
| `DATABASE_URL` | `sqlite:///./aipulse.db` | |
| `CORS_ORIGINS` | `http://localhost:5173` | comma-separated |
| `MIN_GROUP_SIZE` | `5` | smallest group shown on the dashboard |
| `AI_MODE` | `mock` | `mock` or `live` |
| `LLM_API_URL`, `LLM_API_KEY`, `LLM_MODEL` | | live mode only |

## Demo accounts (password `pulse123`)

| Email | Organization(s) | Role |
|---|---|---|
| asha@northwind.test | Northwind Logistics | Admin |
| meera@bluepeak.test | Bluepeak Retail | Admin |
| ravi@consult.test | Both | Employee at Northwind, admin at Bluepeak |
| priya@northwind.test | Northwind Logistics | Employee (Support), has a report |
| dev@northwind.test | Northwind Logistics | Employee (Engineering, lead), no report yet |

The seed gives Northwind's Support team exactly 5 respondents, so the dashboard shows Support while Sales/Engineering/HR are pooled into a hidden "Other teams". If Priya deletes her data, Support drops out too.

## Architecture

FastAPI routes → services (question selection, LLM scoring) → SQLAlchemy models. A user's data is tied to a **membership** (user × organization), and every org-scoped request resolves that membership from the signed token. Details and diagram: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Why it's built this way: [ADRs](docs/DECISIONS.md).

## Documentation

| Doc | For |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How it fits together, data model, request flows |
| [docs/API.md](docs/API.md) | Endpoint reference with real request/response examples |
| [docs/DECISIONS.md](docs/DECISIONS.md) | ADR index (org scoping, min-5, delete, AI trust, submissions, passwords) |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | Reset data, manual deletion, rotate secrets, go live with the LLM |
| [docs/DEMO_ACCOUNTS.md](docs/DEMO_ACCOUNTS.md) | Every demo login (password `pulse123`) and what to try |
| [CHANGELOG.md](CHANGELOG.md) | What changed |
| [CLAUDE.md](CLAUDE.md) | Rules and gotchas for contributors and AI agents |

## Contributing

1. Read the "Rules that must not break" in [CLAUDE.md](CLAUDE.md).
2. Write a test for every fix or feature; privacy and security tests should try to break the rule.
3. `python -m pytest` and `npm run build` must pass.
4. Significant decision → add an ADR in `docs/decisions/`; user-visible change → `CHANGELOG.md`.

## API

Full reference: [docs/API.md](docs/API.md).

| Method | Path | Who |
|---|---|---|
| POST | `/auth/login` | anyone, returns a token and org list |
| POST | `/auth/select-org` | logged in, returns an org-scoped token (members only) |
| GET | `/diagnostic/questions` | employee: questions for their role/seniority |
| POST | `/diagnostic/submit` | employee: complete set only; a retake replaces previous answers |
| GET | `/reports/me` | personal report |
| DELETE | `/reports/me` | delete all my answers for this org |
| GET | `/dashboard` | admin of the selected org only |

## AI mode and trust

`AI_MODE=mock` (default) returns canned responses from `backend/data/mock_ai_responses.json`. Like a real model, they are not always well-formed. `AI_MODE=live` calls `LLM_API_URL`.

Every model reply goes through `parse_score()` (`app/services/scoring.py`). Only an integer score of 1–5 is accepted, and only the four known risk flags are kept. Anything else is saved as **unscored** with an honest message and left out of averages. Nothing is guessed. A model or network failure never loses the employee's submission. The employee's answer is fenced in the prompt as data to reduce prompt injection.

---

# Assessment notes

Details live in [`docs/`](docs). Summary:

### What I found wrong, what I fixed, what I left
Full table with severity: **[docs/AUDIT.md](docs/AUDIT.md)**. File-by-file: [docs/CHANGES.md](docs/CHANGES.md).
- **Fixed, critical:** an admin could read any organization's dashboard (`?org_id=`, and the original test asserted it). `select-org` signed tokens for orgs the user wasn't in. Small groups were visible. There was no way to delete data.
- **Fixed, high:** unsalted SHA-256 passwords; `.env` committed; seniority compared alphabetically (leads missed senior questions); LLM output parsed blindly (4/10 mock replies crash it or store bad data); department average divided by headcount; two different maturity scales; submissions duplicated on retake and accepted foreign questions.
- **Fixed, medium/low:** Dockerfile entrypoint, CORS `*`, default secret in prod, N+1 queries, tests writing to the working dir, placeholder dashboard, no validation/logout in the UI.
- **Deliberately left:** login rate limiting, token revocation / httpOnly cookies, DB migrations, deletion audit log, live-LLM testing against a real provider. Reasons in AUDIT.md.

### Honest status (2026-10-28)

**Verified working**
- 40/40 backend tests pass (`python -m pytest`); the frontend production build passes.
- Clicked through in a real browser:
  - **Admin dashboard:** Support visible; small teams pooled and hidden.
  - **Employee report:** delete my data (confirmed in a dialog), then retake with validation; the open answer is scored.
  - **Multi-org user:** Northwind employee, then switch org to Bluepeak admin, where both teams are under 5 and hidden.
  - **Session handling:** log out, a bad token logs you out, a wrong password shows an error.
- **Docker:** `docker build` succeeds (Docker 29.8). The container, started with the `docker run` command above, seeds the data, answers `/health` and lets a demo user log in.
- Runbook snippets executed against a throwaway DB. API doc examples were captured from the live API.

  - **Own feature (Risk → action):** the dashboard shows risk, people and %, where it's concentrated, and what to do; the employee report shows a personal action.

**Not done**
- Secrets that were in the committed `.env` have **not been rotated** (it's in git history).

**Not verified**
- **Live LLM mode**: only tested through the mock responses and parser tests, never against a real provider.
- **Frontend**: no automated tests; it was checked by hand only.

**Known issues still open** (none block the demo)
- The LLM call runs inside the submit request (up to a 60s timeout), so a slow provider means a slow submit.
- **Privacy limit (by design, not fixed):** dashboards are live. If an admin compares the dashboard just before and after one person answers or deletes, they can work out that person's effect on a visible team's average. Batched refreshes would fix this but would break "disappears immediately", so it's raised with the client ([AUDIT #27](docs/AUDIT.md)).
- The dashboard shows the total respondent *count* even when groups are hidden (count only, no scores). It's in the client questions.
- No login rate limiting, no token revocation, tokens in localStorage, no DB migrations, `datetime.utcnow` warnings. Reasons are in [AUDIT.md](docs/AUDIT.md).

### The client's request
**[docs/CLIENT_REQUEST_RESPONSE.md](docs/CLIENT_REQUEST_RESPONSE.md)**: min-5 *respondents* with an "Other teams" pool (hidden if still under 5), risks and overall built only from visible people (blocks recovery by subtraction), and hard delete per organization, which disappears from dashboards right away. It also lists 9 questions for the client.

### My own feature: Risk → action
**Problem:** AI Pulse told leadership *that* there were risks ("customer_data_shared: 2") and told employees they had one, but not **where** the risk sits or **what to do about it**. A diagnosis with no next step doesn't change behaviour, and changing behaviour is why a company buys this.

**What it does:**
- **Leadership dashboard:** every top risk shows a plain-language name, how many people it affects (and the % of respondents), **which teams it's concentrated in** ("Support: 2 of 5"), and **one concrete team action** (e.g. "Approve one AI tool for customer work and run a 15-minute session on removing names, emails and order numbers before pasting").
- **Employee report:** each personal risk comes with **what you can do about it**.
- **One risk catalog** (`backend/app/services/risks.py`) drives the allowed AI flags, the labels and both actions, so they can't drift apart.

**Why this one:** it's small (no schema change), it serves both audiences, and it builds on the privacy rules. "Where" only ever lists teams with at least 5 respondents, so it can't reveal a hidden team. I didn't pick "Retake trend": it needed a new table and its team trends create a new way to identify people. The actions are fixed, human-written text rather than LLM-generated, because unreviewed AI advice is the very risk the product measures. Details: [ADR-007](docs/decisions/ADR-007-risk-to-action.md).

### How I used AI tools
**[docs/AI_LOG.md](docs/AI_LOG.md)**. Where it went wrong: its first version of the min-5 dashboard leaked hidden teams' scores through the overall average (subtraction). It was caught on review and now has a test.

More: [how I worked](docs/APPROACH.md) · [decisions / ADRs](docs/DECISIONS.md) · [changelog](CHANGELOG.md) · [recording script](docs/WALKTHROUGH.md)
