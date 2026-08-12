---
status: accepted
---
# stometa.dev is a hard fork of ShipAny with no upstream

ShipAny is a SaaS engine. Payment across four providers, credits,
subscriptions, invite codes, tickets and AI tasks are machinery a personal blog
will never run, and each ships live API routes and tables. We fork once, delete
them, and drop the upstream remote.

**Corrected 2026-08-11.** This ADR originally claimed those modules were
"roughly 60%" of the template and "cleanly removable". Both are false, measured:
measured against **tracked** source (`git ls-files src` = 228 files / 34,952
lines), the six service modules are **1,735 lines (4.96%)**, or **5,859 lines
(16.76%)** including their 29 feature routes. *(An earlier revision of this ADR
said 2.67%/8.47%; that measured the working tree, whose denominator is inflated
by generated files — `src/paraglide/**` and `src/routeTree.gen.ts` are
gitignored. The tracked figure is the meaningful one: generated code is not code
anyone maintains.)* The justification is
*attack-surface reduction*, not code volume — live payment webhooks and a credit
ledger have no upside here. Removal is also **not clean**: `api/user/info.ts`
gates on `getUserPlan`, `sign-up.tsx` has an invite branch, `admin/users.tsx`
embeds credit-grant UI, `scripts/init-rbac.ts` seeds their permissions, and all
four schema variants define their tables. See
`docs/designs/stometa-dev/shipany-strip-plan.md` for the ordered deletion plan.

## Consequences

The first schema change adds `locale`, `translation_group_id` and revisions to
`posts`, the very table the template owns, so every future upstream merge would
conflict in the hottest file for no benefit. The usual counter-argument —
security patches — does not apply: better-auth and drizzle fixes arrive through
`pnpm update`, not through template merges. `stone16/HugoBlog` is archived
read-only as the permanent record of the markdown era.
