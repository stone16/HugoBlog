---
status: accepted
---
# Posts are written by hand; Nexus is retired

Requirement was posts "in my own words", and 12 of the last 16 posts were
published autonomously by Nexus straight to live with no review gate — a loop
whose failures are already in the git log (a duplicate post from a publish race,
and a same-day revert). Nexus loses the blog entirely rather than being demoted
to a drafter.

## Consequences

Cadence now depends solely on the author, and the historical record is not
reassuring: the hand-written era ran Mar–Apr 2025, then went quiet until August,
then quiet again until Nexus started in Feb 2026. **Silence, not bad writing, is
the failure mode this decision creates**, and the plan must be judged against it.
ContentGenerator's Hugo adapter and publish engine become unused.
