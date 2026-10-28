# ADR-002: Minimum group size of 5 respondents, with an "Other teams" pool

## Status
Accepted (open questions with the client, see `docs/CLIENT_REQUEST_RESPONSE.md`)

## Date
2026-10-28

## Context
Northwind's legal and HR teams require that leadership never sees a department's scores or risks when fewer than 5 people in it completed the diagnostic, so that individuals can't be identified. The inherited dashboard showed every department, including ones with 1–2 respondents, and listed top risks across everyone.

Hiding rows is not enough on its own. If the dashboard shows an all-company average next to the visible departments, a hidden group's average can be recovered by subtraction (differencing). The first draft of this fix had exactly that leak.

## Decision
- Threshold: **5 respondents** (people with at least one saved answer), configurable via `MIN_GROUP_SIZE`.
- Departments under the threshold are pooled into **"Other teams"**. The pool shows numbers only if it also reaches the threshold; otherwise it is listed as hidden with no scores and no count.
- **Top risks** and the **overall** figure are computed only from people in visible groups. Risks count *people*, not answers.
- People with no department form a "No department" group under the same rule.

## Alternatives Considered

### Threshold on headcount instead of respondents
- Rejected: in a 20-person team where 2 answered, the scores shown would belong to 2 identifiable people.

### Drop small departments entirely
- Pros: simplest.
- Cons: leadership loses all signal from small teams.
- Rejected in favour of pooling, which the client explicitly offered as an option.

### Overall average across all respondents
- Rejected: enables recovering hidden scores by subtraction.

## Consequences
- The headline "overall" covers fewer people than "respondents" when groups are hidden. The UI shows both numbers.
- **Not solved: differencing over time.** Because dashboards are live, comparing two views taken just before and after one person submits or deletes reveals that person's effect on a visible team's average. Batched refreshes would fix it but conflict with ADR-003's "disappears immediately". This is raised with the client.
- The total respondent **count** is still shown (no scores). This is listed as a question for the client.
- With the original seed data no Northwind department reached 5, so the seed was extended. Support now has exactly 5 respondents.
- Tests: `test_small_departments_are_pooled_and_hidden`, `test_risks_only_come_from_visible_groups`, `test_overall_uses_visible_people_only`, `test_pool_becomes_visible_at_five`.
