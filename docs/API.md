# API reference

Base URL (dev): `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs` (FastAPI/Swagger).

**Auth:** `Authorization: Bearer <token>`. Tokens are HS256 JWTs valid for 12 hours. Org-scoped endpoints need a token from `/auth/select-org`.

**Errors:** always `{"detail": "<message>"}`.

| Code | Meaning |
|---|---|
| 400 | Invalid input, or token has no organization selected (`"Select an organization first"`) |
| 401 | Missing/invalid/expired token, or wrong email/password |
| 403 | Not a member of that org, or not an admin |
| 422 | Request body doesn't match the schema (FastAPI validation) |

The examples below were captured from the running API with the seed data.

---

### `POST /auth/login`
```json
// request
{"email": "ravi@consult.test", "password": "pulse123"}
// 200
{
  "token": "eyJ…",
  "name": "Ravi Kapoor",
  "organizations": [
    {"org_id": 1, "org_name": "Northwind Logistics", "role": "employee"},
    {"org_id": 2, "org_name": "Bluepeak Retail", "role": "admin"}
  ]
}
```

### `POST /auth/select-org`
Needs the login token. Returns a token scoped to the org.
```json
// request
{"org_id": 1}
// 200
{"token": "eyJ…", "org_id": 1}
// 403 (not a member)
{"detail": "Not a member of this organization"}
```

### `GET /diagnostic/questions`
**Employees only** (403 `"The diagnostic is for employees"` for admins). Questions for the caller's job role and seniority. Option points are never sent.
```json
// 200 (first item)
{
  "id": "common-freq",
  "type": "mcq",
  "roles": ["all"],
  "text": "How often do you use AI tools (ChatGPT, Copilot, Claude, Gemini, etc.) for work?",
  "options": ["Never", "A few times a month", "A few times a week", "Daily", "Many times a day, it's part of how I work"]
}
```

### `POST /diagnostic/submit`
Every question from `/diagnostic/questions`, exactly once. MCQ answers must match an option's text exactly. Replaces any previous answers.
```json
// request
{"answers": [{"question_id": "common-freq", "answer": "Daily"}, …]}
// 200
{"saved": 6}
// 400 (incomplete)
{"detail": "Please answer all questions (missing: common-data, common-open, common-policy, common-review, sup-drafts)"}
```
Other 400s: `Unknown question <id>`, `Each question can only be answered once`, `Answers cannot be empty`, `Invalid option for <id>`.

### `GET /reports/me`
```json
// 200
{
  "name": "Priya Nair",
  "organization": "Northwind Logistics",
  "answered": 2,
  "average_score": 2.5,
  "level": "Exploring",
  "risks": [
    {
      "risk": "customer_data_shared",
      "label": "Shared customer data with an AI tool",
      "action": "Before pasting, replace customer names, emails and IDs with placeholders, and only use the company-approved tool."
    }
  ],
  "next_steps": ["Use AI to draft first replies, then edit", "…"]
}
```
`average_score` is `null` and `level` is `"Not assessed"` when nothing has been scored.

### `DELETE /reports/me`
Deletes all of the caller's answers for the selected org ([ADR-003](decisions/ADR-003-right-to-delete.md)).
```json
// 200
{"deleted": 2}
```

### `GET /dashboard`
Admins only, for the org in the token. Takes no parameters; an `org_id` query param is ignored ([ADR-001](decisions/ADR-001-org-scope-from-token.md)).
```json
// 200
{
  "organization": "Northwind Logistics",
  "min_group_size": 5,
  "respondents": 8,
  "overall": {"respondents": 5, "average_score": 3.3, "level": "Practitioner"},
  "departments": [
    {"department": "Support", "employees": 6, "respondents": 5, "average_score": 3.3, "level": "Practitioner"}
  ],
  "other_teams": {"department": "Other teams", "includes": ["Engineering", "HR", "Sales"], "hidden": true},
  "top_risks": [
    {
      "risk": "customer_data_shared",
      "label": "Shared customer data with an AI tool",
      "people": 2,
      "share": 0.4,
      "teams": [{"team": "Support", "people": 2, "of": 5}],
      "action": "Approve one AI tool for customer work and run a 15-minute session on removing names, emails and order numbers before pasting."
    },
    {
      "risk": "unreviewed_output",
      "label": "Used AI output without reviewing it",
      "people": 1,
      "share": 0.2,
      "teams": [{"team": "Support", "people": 1, "of": 5}],
      "action": "Add a review step for AI-assisted work (e.g. a second read before anything goes to a customer) and share examples of AI mistakes."
    }
  ]
}
// 403 (employee)
{"detail": "Admins only"}
```
- `top_risks` (max 5): `share` = people ÷ visible respondents; `teams` lists only visible groups (possibly "Other teams"), never a hidden department; `action` is the team action from the risk catalog ([ADR-007](decisions/ADR-007-risk-to-action.md)).
- `overall` and `top_risks` only include people in visible groups. `overall` is `null` if no group is visible.
- `other_teams` is `null` when every group is visible. When `hidden` is `false` it also has `respondents`, `average_score` and `level`.

### `GET /health`
`{"status": "ok"}`
