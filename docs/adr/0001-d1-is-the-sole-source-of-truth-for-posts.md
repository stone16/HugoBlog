---
status: accepted
---
# D1 is the sole source of truth for Posts

Posts have lived as markdown in git since the blog began, published by Nexus
writing files and pushing commits. Moving to a database-backed site with a web
editor forces a choice, and we picked D1 as the only canonical copy: no git
mirror, no file export in the write path. Keeping git authoritative would have
meant rewriting the posts module, admin editor and taxonomy of the template we
adopted specifically to avoid that work.

## Consequences

- The `[nexus:<uuid>]` git-commit trail disappears, and with it the ability to
  review by diff what an autonomous agent published. **Revisions** in D1 replace
  it and are therefore not optional.
- Durability rests on Cloudflare: D1 Time Travel gives **7-day** point-in-time
  recovery on Workers Free, or 30 days on Workers Paid, and
  `npx wrangler d1 export <database_name> --remote --output=./database.sql`
  produces an on-demand SQL dump. *(Corrected 2026-08-11: the original text
  claimed 30 days unconditionally — see `docs/designs/stometa-dev/verification-cloudflare.md` C2.)*
  Restoring a mangled Post by rolling the database back also rolls back every
  Comment written since, which is why Revisions carry the real burden here.
- A sole-source-of-truth system must not treat Time Travel as its only backup.
  Export cadence, restore drills, and storage outside the same credential
  boundary need an explicit owner.
- Nexus's Hugo file adapter becomes dead code once an HTTP adapter replaces it.
