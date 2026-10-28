# ADR-005: A submission must be complete, from the user's own questions, and a retake replaces it

## Status
Accepted (may be superseded if submission history is added)

## Date
2026-10-28

## Context
`POST /diagnostic/submit` accepted any question id in the bank (including ones for other roles or seniorities), partial sets, duplicates and empty strings. Each retake added new rows, so averages mixed old and new answers. The level shown to an employee and to leadership depended on how many times they had submitted.

## Decision
- Valid ids are exactly `questions_for(job_role, seniority)` for the caller's membership.
- Reject (400): unknown/foreign ids, duplicates, missing questions, empty answers. Length caps: answer 2000 characters, id 40.
- On success, delete the membership's previous responses and insert the new set in the same transaction.

## Alternatives Considered

### Keep history (versioned submissions)
- Pros: enables "progress over time".
- Cons: needs a `submissions` table and changes to every query that reads responses.
- Deferred: a candidate for the own-feature work. If built, it supersedes this ADR.

### Allow partial submissions
- Rejected: averages over different question sets aren't comparable between people.

## Consequences
- Scores are comparable within a role/seniority.
- A retake overwrites the previous result without a trace.
- Tests: `test_submit_and_retake_replaces_answers`, `test_submit_rejects_incomplete_foreign_and_duplicate`.
