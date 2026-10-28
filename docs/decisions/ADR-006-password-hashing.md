# ADR-006: Salted PBKDF2-SHA256 from the standard library for passwords

## Status
Accepted

## Date
2026-10-28

## Context
Passwords were stored as unsalted SHA-256: fast to brute-force, and identical passwords give identical hashes (every seeded user had the same hash).

## Decision
`hashlib.pbkdf2_hmac("sha256", ...)` with 200,000 iterations and a random 16-byte salt, stored as `pbkdf2$<iterations>$<salt>$<hash>`. Verification uses `hmac.compare_digest`. Malformed stored values fail closed.

## Alternatives Considered

### bcrypt / argon2
- Pros: argon2 is the stronger modern choice.
- Cons: a new native dependency.
- Rejected for this pass: PBKDF2 at this cost is acceptable, and the stored format records the algorithm and iterations so a later migration can rehash on login.

## Consequences
- Old SHA-256 hashes don't verify. That's fine here because the database is created by the seed script; a real deployment with existing users would need rehash-on-login.
- Hashing is deliberately slow (measured ~0.07s per hash on the dev machine). The seed hashes the shared demo password once, otherwise the test suite took 33s instead of 6s.
- Test: `test_passwords_are_salted`.
