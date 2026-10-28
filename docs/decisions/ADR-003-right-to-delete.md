# ADR-003: Right to delete is a hard delete scoped to the selected organization

## Status
Accepted (open questions with the client)

## Date
2026-10-28

## Context
Northwind requires that any employee can delete all their answers and their report themselves, and that it disappears from every dashboard immediately. Answers live in `responses`, keyed by `membership_id`. Reports and dashboards are computed on request from `responses`; nothing is cached or precomputed.

## Decision
`DELETE /reports/me` hard-deletes every `Response` row for the caller's current membership (the org in their token) and returns `{"deleted": n}`. The report page has a "Delete my data" button with a confirm dialog.

## Alternatives Considered

### Soft delete (`deleted_at` flag)
- Pros: recoverable, auditable.
- Cons: the data still exists, every query must filter it, and one missed filter makes it reappear on a dashboard.
- Rejected: "delete" for a privacy request should mean gone.

### Delete across all of the user's organizations
- Pros: one click for consultants.
- Cons: an action taken while signed into org A silently changes org B's data.
- Rejected for now, and asked as a client question.

## Consequences
- "Immediately" holds because nothing caches results. Adding a cache later would require invalidating it on delete.
- No record that a deletion happened is kept. A compliance audit log (who/when, no content) is a client question.
- In live AI mode, copies of the answers already sent to the LLM provider are not covered.
- Tests: `test_employee_can_delete_their_data` (Support then drops below 5 and leaves the dashboard), `test_delete_only_affects_selected_org`.
