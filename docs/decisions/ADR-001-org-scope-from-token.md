# ADR-001: Organization scope comes only from the signed token

## Status
Accepted

## Date
2026-10-28

## Context
Users can belong to several organizations (consultants, group HR). After login they choose one, and `/auth/select-org` issues a JWT with an `org` claim. The inherited code had two holes:
- `/auth/select-org` signed a token for **any** `org_id`, member or not.
- `GET /dashboard?org_id=N` read the org from the URL. An admin of Northwind could pass Bluepeak's id and read its data. The original test `test_admin_cannot_see_other_org` asserted `200 OK` for that request, which locked the leak in.

## Decision
- `select-org` returns 403 unless the user has a membership in that org.
- Every org-scoped endpoint gets its org from `current_membership` (token `sub` + `org`, re-checked against the `memberships` table on every request). No endpoint accepts an org id from the client. `GET /dashboard` takes no parameters.

## Alternatives Considered

### Keep `?org_id=` and validate it against the membership
- Pros: no API change for the frontend.
- Cons: two sources of truth, and every new endpoint has to remember the check.
- Rejected: one missed check reopens the leak; deriving scope from the token makes it impossible to forget.

### Put all memberships in one token
- Pros: no org switch round-trip.
- Cons: every endpoint must then decide which org is meant, which brings back the same ambiguity.
- Rejected.

## Consequences
- Switching org means calling `select-org` again (the UI has a "Switch org" button).
- Removing a membership takes effect on the next request even though the token is still valid, because the membership is looked up each time.
- Tests: `test_cannot_select_org_you_dont_belong_to`, `test_admin_cannot_see_other_org` (now asserts the URL param is ignored), `test_multi_org_user_sees_only_selected_org`, `test_token_without_org_is_rejected`.
