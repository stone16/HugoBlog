---
status: accepted
---
# One cutover, behind a continuously deployed staging host

The whole platform — blog, comments, artifacts, admin, redirects — is built to
completion before the domain moves, so nothing half-finished ever appears under
the author's own name. The two costs of a big-bang launch are structurally
removed rather than accepted.

## Consequences

- **Output does not pause.** The Hugo site keeps serving `stometa.top` throughout;
  anything published there during the build migrates into D1 at cutover.
- **The launch is not the first run.** The finished app is deployed continuously
  to a password-protected, `noindex` staging hostname from week one, so cutover
  is a DNS change against a system that has been running for weeks.
- Cutover is checklist-driven: bulk 301 `stometa.top/*` → `stometa.dev/*`, four
  hand rules for the English posts, a dedicated 301 for `/index.xml` with the
  feed's self-`<link>` updated, GA4 data stream re-pointed off the old hostname,
  and a fresh sitemap submitted to Search Console.
