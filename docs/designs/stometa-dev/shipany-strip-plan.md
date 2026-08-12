# ShipAny strip feasibility (read-only audit)

Target: `/Users/stometa/dev/shipany-tanstack`, current checkout (working tree; no files modified). Counts below were run against `src` with `find`/`wc -l`.

## Verdict on the 60% claim

`src` contains **1,078 files / 64,940 lines**. The six proposed service modules are **6 files / 1,735 lines (2.67%)**, not 60%. Their feature routes are 26 files / 3,767 lines (5.80%); modules plus routes total 5,502 lines (8.47%, files 32/1,078 = 2.97%). The nominated keep-set (`core/i18n`, `core/auth`, `core/db`, `core/storage`, `modules/posts`, `modules/taxonomy`, `modules/rbac`, `modules/apikeys`, `routes/admin`) is 33 files / 6,774 lines (10.43%). These sets overlap neither by path, and keep-set is not the complement of all `src`; therefore no defensible interpretation produces ~60%.

Per doomed module: payment 1/626, credits 1/297, subscriptions 1/101, invite-codes 1/221, tickets 1/337, ai-tasks 1/153 (files/lines).

## Coupling found

- Payment imports credits and subscriptions at `src/modules/payment/service.ts:19-29`; AI tasks imports credits at `src/modules/ai-tasks/service.ts:3-6`.
- Signup itself does not auto-grant credits. `src/routes/(auth)/sign-up.tsx:126-151` calls better-auth then invite validation/redeem. The server user-info path is coupled to invite-codes: `src/routes/api/user/info.ts:3-6,18-28` calls `getUserPlan` and gates access on invite configuration. Removing invite-codes requires rewriting this endpoint and signup's invite branch (including `/api/invite-codes/*` calls), not merely deleting a module.
- Admin navigation enumerates doomed pages at `src/routes/admin/route.tsx:35,41-49,59` (invite-codes, payments, subscriptions, credits, tickets). Remove those entries and the billing group; retain users/content shell.
- No kept table has a foreign key to a doomed table. In `src/config/db/schema.ts`, doomed tables reference only `user` (e.g. order `:194-196`, subscription `:260-262`, credit `:317-319`, ticket `:611`, invite `:666/681-684`); ticket_message references ticket (`:631-633`) and user. However all three schema variants (`schema.ts`, `schema.sqlite.ts`, `schema.postgres.ts`, `schema.mysql.ts`) define the doomed tables and exported types, so all must be edited consistently.
- RBAC seed is coupled semantically: `scripts/init-rbac.ts:126-158` seeds payments/subscriptions/credits permissions; `:245-266` seeds AI-task permissions; admin defaults include their wildcards at `:293-304`. Delete these permission records and wildcard entries (and regenerate existing DB seed data as appropriate).
- No imports from doomed modules were found in kept core/components/posts/taxonomy/rbac/apikeys/admin code beyond the explicit routes above. Shared UI is still feature-coupled by data/URLs: `src/routes/admin/users.tsx` contains credit grant UI and calls `/api/admin/users/credits`; this must be removed or rewritten.

## Ordered deletion plan (keep build green)

1. First remove/replace call sites: rewrite `src/routes/api/user/info.ts` to return auth/profile data without plan/invite gating; remove invite validation/redeem block in `src/routes/(auth)/sign-up.tsx`; remove credit UI/query/mutation from `src/routes/admin/users.tsx`; remove doomed nav entries in `src/routes/admin/route.tsx`.
2. Delete feature routes (26 paths):
   `src/routes/settings/{tickets,payments,credits}.tsx`, `src/routes/admin/{subscriptions,invite-codes,tickets,payments,credits}.tsx`, `src/routes/api/{credits.ts,tickets.ts,tickets/$id.ts,payment/checkout.ts,payment/callback.ts,payment/notify/$provider.ts}`, `src/routes/api/admin/{credits.ts,subscriptions.ts,invite-codes.ts,tickets.ts,tickets/$id.ts,users/credits.ts}`, `src/routes/api/user/{credits.ts,subscriptions/current.ts,subscriptions/cancel.ts,subscriptions/index.ts}`, and `src/routes/api/invite-codes/{validate.ts,redeem.ts}`. Also delete `src/routes/api/admin/orders.ts` and `src/routes/api/user/orders.ts` if payment/order functionality is in scope (they are order routes even though filenames do not contain `payment`). Delete `src/routes/(auth)/redeem-invite.tsx`.
3. Remove module-to-module imports before deleting services: payment's credits/subscription logic and AI-task's credit calls must either be deleted with their routes or AI tasks must be retained and rewritten to use a replacement quota service.
4. Edit all four schema files (`src/config/db/schema.ts`, `schema.sqlite.ts`, `schema.postgres.ts`, `schema.mysql.ts`): remove order, subscription, credit, ticket/ticketMessage, inviteCode/userInvite, and aiTask table blocks plus their exported types. Preserve kept tables and auth/RBAC/content foreign keys. Generate a migration rather than silently dropping production data.
5. Remove doomed services: `src/modules/payment/service.ts`, `credits/service.ts`, `subscriptions/service.ts`, `invite-codes/service.ts`, `tickets/service.ts`, `ai-tasks/service.ts`. Remove payment provider core only if no non-payment product needs it (`src/core/payment` is separate from `modules/payment`).
6. Edit `scripts/init-rbac.ts` permission declarations/default role lists cited above; remove stale translation keys/components only after TypeScript reports no references. Regenerate `src/routeTree.gen.ts` via the normal build tooling; do not hand-edit it.
7. Run `pnpm build` after each phase; run schema generation/migration checks after schema edits.

## What breaks / rewrite-required

Deleting payment removes checkout/webhook/subscription lifecycle and order history; deleting credits removes quota accounting, initial-credit grants, admin grants, and AI-task consumption; deleting invite-codes removes invite-only signup and `getUserPlan` authorization; deleting tickets removes support UI/API and ticket_message data; deleting AI tasks removes task tracking (or requires a non-credit quota rewrite). Existing DBs require destructive table migrations and data-retention decisions. Admin users must lose credit controls and billing navigation. `core/payment` provider adapters and pricing blocks may still be independently referenced and need a separate import audit.

## Load-bearing template claims

`src/components/rich-text-editor.tsx:30-58` confirms markdown storage: `MarkdownIt({ html:false, linkify:true })` renders markdown to HTML, and Turndown (`headingStyle:'atx'`, `codeBlockStyle:'fenced'`, `bulletListMarker:'-'`, `emDelimiter:'*'`) converts edited HTML back; strikethrough and figure rules are added at `:46-51`.

Locale routing is Paraglide, not route folders. `vite.config.ts:70-99` sets `strategy: ['url','cookie','baseLocale']`; URL patterns map English to `/` or `/:path` and Chinese to `/zh` or `/zh/:path`. `src/router.tsx:12-17` applies `deLocalizeUrl` on input and `localizeUrl` on output. To invert Chinese-at-root, change `project.inlang/settings.json:3` baseLocale to `zh` and swap the localized URL pattern mappings (while deciding where English gets its explicit prefix, e.g. `/en`).

## Round-trip losslessness test

Using the installed `markdown-it` and `turndown` configs, a fenced code block with a language hint round-trips unchanged: ```` ```ts\nconst x = 1\n``` ````. A markdown table does **not**: markdown-it emits `<table>…</table>`, but Turndown's default output is plain paragraphs (`A\n\nB\n\n1\n\n2`), losing table structure. Thus headings, emphasis, links, lists, fenced code (language class), blockquotes/rules generally survive structurally, while tables, HTML (disabled on input), many attributes, and exact whitespace/escaping are not lossless. A migration must preserve original markdown or add a Turndown table plugin plus fixture tests.

## VERDICT

The hard-fork-and-strip idea is technically possible, but ADR-0006's “roughly 60%” and “cleanly removable” claims are disproved. The actual service share is 2.67% of `src` (8.47% including feature routes), with cross-cutting auth, navigation, RBAC seed, schema, and user-admin UI edits. Keep the fork, but execute the staged plan above, explicitly decide whether orders/core payment and AI tasks are in scope, and add migration plus markdown round-trip tests before declaring the strip complete.
