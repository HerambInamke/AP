# How I used AI tools

**Tools:** Claude Code (in the terminal) did most of the reading, drafting and checking. I used graphify to get a map of the code and Chrome DevTools MCP to click through the app in a real browser.

## What I used it for
- **Getting my bearings.** I built a code graph with graphify and had Claude read every file. That gave me the first TODO list.
- **Finding bugs.** Claude suggested suspects. I didn't fix anything until it was proven by a failing test or by running the code.
- **Fixes and tests.** Claude wrote the first drafts. I read every diff, and when something didn't fit the existing structure I pushed back.
- **Clicking through the app.** Claude drove Chrome through the admin, employee and multi-org flows. That's how the CORS bug below came to light.
- **Docs.** Claude wrote the first drafts and I edited them. I had every number and command checked against the running code.

## Where it got things wrong
1. **It added a privacy leak to its own privacy fix.** This is the one that matters. The first min-5 dashboard still showed an "overall" average across *everyone*. Take that and the visible Support average, and you can work out the hidden teams' average by subtraction, which is exactly what the client asked us to stop. I caught it while reviewing, before any test existed. Now the overall average and risks only count people in visible groups, and `test_overall_uses_visible_people_only` guards it.
2. **It stated a bug as fact before running anything.** The first TODO said the seniority test "should fail today", but the dependencies weren't even installed yet. It turned out to be right, but from then on I made it prove claims by running them.
3. **Wrong Python.** It set up the venv on Python 3.14, where the pinned pydantic won't build. I switched to 3.13, and the README now says so.
4. **It didn't think about the demo data.** With the original seed, the min-5 rule would have left the dashboard completely empty. That came up while writing tests, so I added Support employees to get one team over the threshold.
5. **A made-up number in a doc.** The first draft of ADR-006 said hashing takes "~0.1–0.3s". When I measured it, it was about 0.07s. After that, every number and command in the docs was checked: the API examples were captured from the real API and the runbook snippets were run.
6. **It slowed the tests down.** Switching to salted PBKDF2 meant the seed hashed 17 passwords on every test, and the suite took 33s. Hashing the shared demo password once brought it back to about 6s.
7. **Its CORS fix broke local dev.** Locking CORS to `http://localhost:5173` was the right call, but if 5173 is busy, Vite quietly moves to 5174, and login just says "Failed to fetch". No test caught it; I found it on a second pass through the app in the browser. The fix is `strictPort: true`. The lesson for me: after a fix, test the whole flow again, not just the unit tests.
8. **Variable shadowing in my own feature.** The first risk → action loop reused the name `people` and overwrote a dict that was needed a few lines later. Nine dashboard tests failed at once with a `TypeError`, so the tests I'd written earlier paid for themselves. Renaming the variable to `affected` fixed it.

## What I didn't let it do
- Add new dependencies or restructure the app.
- Commit or push for me.
