# ADR-007: Risk → action (own feature)

## Status
Accepted

## Date
2026-10-28

## Context
AI Pulse flags risks (customer data shared, unreviewed output…), but the dashboard only listed a flag name and a count, and the employee report only listed names. Leadership was left asking "so what do we do, and where?", and employees were told they had a risk without being told how to fix it. The product's value is in changing behaviour, so a diagnosis with no next step stops halfway.

Risk names also lived in two places (the backend's allowed-flag list and a frontend label map), which could drift apart.

## Decision
One **risk catalog** (`backend/app/services/risks.py`) is the single source for each flag's label, a **team action** (for leadership) and a **personal action** (for the employee). The LLM's allowed flags are derived from it (`scoring.ALLOWED_FLAGS = set(RISKS)`).
- **Dashboard** `top_risks[]` now has `label`, `people`, `share` (of visible respondents), `teams` (which *visible* teams it's in: `people` of `of`), and `action`.
- **Report** `risks[]` is now `{risk, label, action}` with the personal action.
- The frontend shows these as-is; `frontend/src/risks.js` was removed.

## Alternatives Considered

### Retake trend (progress over time)
- Pros: shows improvement.
- Cons: needs a submissions table, would supersede ADR-005, and team trends over time open a new differencing risk (a team's change can reveal who retook).
- Rejected for the deadline. It's the natural next feature.

### Weakest skill per team
- Pros: also actionable.
- Cons: overlaps with risks; the actionable signal is clearer on risks.
- Deferred.

### LLM-generated actions per person
- Rejected: an untrusted, unreviewed recommendation is exactly the risk the product warns about. Fixed, human-written actions can be reviewed by the client.

## Consequences
- **Privacy holds automatically**: risk teams are built only from visible groups (≥ 5 respondents), so a hidden department never appears in "Where". The visible "Other teams" pool can appear.
- **API change**: `report.risks` changed from strings to objects, and `top_risks[]` gained fields. Only the bundled frontend consumes it.
- The actions are generic starting points written by us. The client may want their own policy wording (a question for Northwind).
- Tests: `test_dashboard_risks_show_where_and_what_to_do`, `test_risk_teams_include_visible_pool_but_never_hidden_departments`, `test_report_risks_come_with_a_personal_action`, `test_every_allowed_flag_has_label_and_actions`.
