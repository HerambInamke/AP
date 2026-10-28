# Decisions

Significant decisions are recorded as ADRs in [`decisions/`](decisions). Don't delete an ADR; if a decision changes, write a new one that supersedes it.

| ADR | Decision | Status |
|---|---|---|
| [001](decisions/ADR-001-org-scope-from-token.md) | Org scope comes only from the signed token | Accepted |
| [002](decisions/ADR-002-minimum-group-size.md) | Min 5 respondents, "Other teams" pool, no differencing | Accepted, client questions open |
| [003](decisions/ADR-003-right-to-delete.md) | Hard delete, scoped to the selected org | Accepted, client questions open |
| [004](decisions/ADR-004-untrusted-ai-output.md) | LLM output untrusted → "unscored", never guessed | Accepted |
| [005](decisions/ADR-005-submission-rules.md) | Complete submissions from own questions; retake replaces | Accepted |
| [006](decisions/ADR-006-password-hashing.md) | Salted PBKDF2 from stdlib | Accepted |
| [007](decisions/ADR-007-risk-to-action.md) | Own feature: Risk → action, one risk catalog | Accepted |

## Smaller decisions (no ADR needed)
- **Seed data extended**: Support has exactly 5 respondents, so the demo shows both a visible team and a hidden pool.
- **Kept the existing structure**: same routes / services / models layers, no new runtime dependencies.
- **One maturity scale**: `utils.maturity_level` is used everywhere; the dashboard's separate `level_for` was removed.
- **CORS and secrets from env**: `CORS_ORIGINS` defaults to the Vite dev URL; startup fails with the default `SECRET_KEY` when `APP_ENV=production`.
