# Client request: how it was handled

Request from Northwind HR (see `CLIENT_REQUEST.md`): two changes before rollout.

## 1. No small groups on the dashboard

**Rule implemented:** a department appears on its own only when **≥ 5 people in it have completed the diagnostic** (`MIN_GROUP_SIZE`, configurable, default 5).

- Smaller departments are pooled into **"Other teams"**. Its numbers are shown only if the pool itself has ≥ 5 respondents. Otherwise the row says "Not shown" with no scores and no count.
- **Top risks** come only from people in visible groups and count *people*, not answers. A hidden team's risks never appear.
- **Overall average** uses only visible people. An all-company average would let someone subtract the visible teams and recover the hidden group's score. My first draft had exactly this leak (see AI_LOG.md).
- People without a department are treated as their own group, "No department", under the same rule.
- Code: `backend/app/routes/dashboard.py`. Tests: `test_small_departments_are_pooled_and_hidden`, `test_risks_only_come_from_visible_groups`, `test_overall_uses_visible_people_only`, `test_pool_becomes_visible_at_five`.

## 2. Right to delete

- `DELETE /reports/me` deletes all of the employee's answers **for the organization they're signed into**, which also removes their report.
- Dashboards are computed live from answers, so the data is gone from every dashboard on the next load. There is no cache to clear.
- UI: **"Delete my data"** button on the report, with a confirm step.
- Tests: `test_employee_can_delete_their_data` (also checks that Support drops off the dashboard once it falls to 4), `test_delete_only_affects_selected_org`.

## Questions to ask Northwind
1. **"5 people": respondents or headcount?** I used *respondents* (stricter, because a team of 20 where 2 answered would otherwise show 2 people's data).
2. If "Other teams" is still under 5 we **hide** it. Is that OK, or should those people be excluded completely?
3. Is showing the **total number of respondents** acceptable (it's only a count, no scores)?
4. Delete is **per organization**. A consultant working with two companies deletes each separately. Should one click delete everywhere?
5. Do you need a **record that a deletion happened** (who and when, no content) for compliance? Right now nothing is kept.
6. In live mode, answers are sent to an external LLM provider. Deleting here does not delete the provider's copy. Which provider and retention terms are approved?
7. Should a **retake** keep history (to show progress over time) or replace it? Right now it replaces.
8. **Live vs. delayed dashboards.** The 5-person rule hides small groups, but an admin who checks the dashboard right before and after one person answers or deletes can see that person's effect on a team's average. Refreshing dashboards on a schedule (e.g. daily) closes this, but then "disappears immediately" would mean "by the next refresh". Which matters more to you?
9. Should **admins** also take the diagnostic? Right now it's employees only.
