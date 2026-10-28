# Runbook

Common operational tasks. Commands assume `cd backend` with the venv active.

## Reset demo data
**When:** before a demo, or after manual testing.
```bash
python -m app.seed
```
**Warning:** this drops and recreates **every table**. Never run it against a real database.

## An employee asks for their data to be deleted
1. Preferred: the employee does it themselves (Report → **Delete my data**), signed into the right organization.
2. If they can't: an engineer runs the same delete for that membership:
   ```python
   # python -c / shell, with DATABASE_URL pointing at the target DB
   from app.db import SessionLocal; from app import models
   db = SessionLocal()
   m = db.query(models.Membership).join(models.User).filter(models.User.email == "<email>", models.Membership.org_id == <org_id>).one()
   print(db.query(models.Response).filter_by(membership_id=m.id).delete()); db.commit()
   ```
3. Check: the admin dashboard no longer counts them (respondent numbers drop).
4. If live AI mode was used, the LLM provider may still hold copies, so follow the provider's deletion process.

## Rotate `SECRET_KEY`
**When:** a leak is suspected, and **now**, because the old `.env` is in git history.
1. Generate a key: `python -c "import secrets; print(secrets.token_urlsafe(48))"`
2. Set `SECRET_KEY` in the environment / `.env` and restart the API.
3. Effect: every existing token becomes invalid, so all users must log in again. No data changes.
4. Rollback: restore the previous key (this re-validates old tokens until they expire, within 12h).

## Switch AI scoring to live mode
1. Set `AI_MODE=live`, `LLM_API_URL` (chat-completions URL), `LLM_API_KEY`, `LLM_MODEL`. Restart.
2. Smoke test: submit one diagnostic and check the open answer's `reason` in the report isn't "AI score unavailable…".
3. If scoring fails, submissions still save (the answer is just unscored). Check the API logs for `LLM scoring failed`.
4. Rollback: `AI_MODE=mock`.

## Change the minimum group size
Set `MIN_GROUP_SIZE` and restart. Lowering it below 5 breaks the Northwind agreement, so get the client's sign-off first.

## Production checklist
- `APP_ENV=production` (startup refuses the default secret)
- `SECRET_KEY` set and rotated
- `CORS_ORIGINS` = the real frontend URL
- `DATABASE_URL` points to a persistent DB (not the container filesystem)
- Do **not** run `app.seed`
