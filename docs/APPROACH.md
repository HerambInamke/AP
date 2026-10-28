# How I did it

1. **Map before touching anything.** Read the README, the client request and every source file. Built a knowledge graph with graphify (151 nodes, 13 clusters: auth, dashboard, diagnostic, scoring, frontend…) to see who calls what, then wrote `TODO.md`.
2. **Get a baseline.** Installed deps (Python 3.14 failed, the pins need 3.12/3.13) and ran the tests: 7 passed, 1 failed. The failure proved the seniority bug before I changed anything.
3. **Prioritise by harm.** Order: data reaching the wrong people → client request → wrong numbers / crashes → ops → UI. Each item has a severity in `AUDIT.md`.
4. **Fix at the root, in the shared code.** For example, the org now comes from the token, so no endpoint can be handed a wrong org. There's one maturity scale instead of two, and one parser for all AI output.
5. **One test per fix.** Security and privacy fixes are tested the way an attacker would try them (wrong org id, foreign question ids, deleted data still showing). Every malformed mock AI response has its own test case.
6. **Check it for real.** Ran the backend + frontend and clicked through in a browser: admin dashboard (Support visible, others pooled and hidden), employee report, delete, retake with validation, scoring.
7. **Write it down.** AUDIT (what), DECISIONS (why), CLIENT_REQUEST_RESPONSE (client), AI_LOG (how AI was used), WALKTHROUGH (demo script).

8. **Re-test end to end after "done".** A second browser pass (multi-org switch, retake, bad token) found a bug my own CORS fix had introduced (AUDIT #23).

9. **Final skeptical review of auth and logic.** Found and measured login timing enumeration (4ms vs 77ms) and admins reaching the diagnostic API, both now fixed with tests. Also wrote down the over-time differencing limit instead of hiding it.

**Verified:** 40/40 backend tests, frontend production build, two manual browser passes covering admin, employee, multi-org, delete, retake, logout and bad-token flows.
**Also verified:** the Docker image builds, and the container seeds the data, answers `/health` and accepts a demo login.
**Not verified:** live LLM mode against a real provider, frontend automated tests (none exist).
