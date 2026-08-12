---
status: accepted
---
# Success is cadence, and the cadence risk is accepted unmitigated

Success at six months is defined as **sustained publishing cadence** — volume and
consistency, roughly 30+ posts and a rhythm actually kept. Every structural
mitigation for cadence was offered and declined: no drafting pipeline, no
scheduled-post queue, no return of Nexus in any role.

## Consequences

This is the plan's central tension and it is recorded deliberately rather than
softened. [ADR-0007](0007-posts-are-written-by-hand.md) retires the pipeline that
produced 12 of the last 16 posts, and the hand-written era it returns to has two
multi-month gaps (Apr–Aug 2025, and Aug 2025–Feb 2026). The plan is therefore
**measured by the one variable it has no defence for.**

Two consequences follow:

- **No architectural decision can rescue this.** If the site is silent in six
  months, the cause will not be the platform. Reviewing the architecture at that
  point would be looking in the wrong place.
- **The only remaining safety is free and passive:** the Hugo site keeps serving
  `stometa.top` throughout the build, so publishing *can* continue during it and
  anything published migrates at cutover. Whether that capability is used is
  outside the architecture's control.

If cadence has not materialised by the first review, the honest response is to
reopen ADR-0007, not to add features.
