# stometa.dev — Implementation Plan

**Status:** approved for build · **Date:** 2026-08-11 · **Supersedes:** `docs/designs/blog-enhancement.md`, root `DESIGN.md`

Source of authority: the twelve ADRs in [`docs/adr/`](../../adr/), all `accepted`.
Vocabulary: [`CONTEXT.md`](../../../CONTEXT.md). Evidence: the three sibling
documents in this directory. **Where this plan and an ADR disagree, the ADR wins.**

---

## 1. Goal, and the risk that owns it

Move `stometa.top` (Hugo → GitHub Pages) to `stometa.dev` (TanStack Start →
Cloudflare Workers + D1 + R2): a bilingual technical publication with first-party
comments, a hand-authored editorial front page, and a self-hosted artifact host
replacing ht-ml.app.

**Success at six months is cadence** — sustained publishing volume and rhythm,
~30+ posts. Not inbound, not citations. See [ADR-0012](../../adr/0012-success-is-cadence-and-the-cadence-risk-is-accepted.md).

> ⚠️ **The plan is measured by the one variable it has no defence for.**
> [ADR-0007](../../adr/0007-posts-are-written-by-hand.md) retires the pipeline
> that produced 12 of the last 16 posts. Every structural cadence mitigation was
> offered and declined. If this site is silent in six months, the cause is not
> the architecture, and re-architecting will not fix it. The only passive safety
> is that Hugo keeps serving `stometa.top` during the build, so publishing *can*
> continue and migrates at cutover.

---

## 2. Decision register

| # | Decision | ADR |
|---|---|---|
| D01 | D1 is the sole source of truth for Posts. No git mirror. | 0001 |
| D02 | Revisions are mandatory — every write appends a row. | 0001 |
| D03 | One Locale per Post; optional Translation Group for hand-written pairs. | 0002 |
| D04 | Artifacts at `<slug>.stometa.dev`, secured by four browser-enforced controls. | 0003 |
| D05 | First-party Comments in D1 replace Giscus. Anonymous + moderation. | 0004 |
| D06 | Address decoupled from access: `visibility` defaults to `password` + `noindex`. | 0005 |
| D07 | Hard fork of ShipAny, no upstream remote. Strip = 16.76% of tracked src. | 0006 |
| D08 | Nexus retired; posts hand-written. | 0007 |
| D09 | Markdown storage; rich mode refused unless the round-trip is byte-identical. | 0008 |
| D10 | Chinese at root, English at `/en`; slugs preserved byte-for-byte. | 0009 |
| D11 | Editorial publication design. Retire the purple→cyan `DESIGN.md` palette. | — |
| D12 | One cutover, behind a continuously deployed private staging host. | 0009 |
| D13 | Bot gate: rate limit + honeypot baseline, adaptive self-hosted ALTCHA. | 0004 |
| D14 | Artifacts support HTML **and** PDF, optional expiry, view tracking. `invited` deferred. | 0010 |
| D15 | Carry over search, `/links`, social cards. Drop Now, Projects, contributions graph. | 0011 |
| D16 | The X-algorithm flagship is **rewritten as clean markdown**, losing its bespoke CSS. | 0011 |
| D17 | Success = cadence; the cadence risk is accepted unmitigated. | 0012 |

---

## 3. Verified constraints

These were checked against primary sources — see [`verification-cloudflare.md`](verification-cloudflare.md).
They are not negotiable design inputs.

| Constraint | Consequence |
|---|---|
| Workers Free caps CPU at **10 ms/request**; Cloudflare places auth/SSR work at 10–20 ms | **Budget Workers Paid, US$5/mo minimum.** Free is a prototype surface only. |
| D1 Time Travel: **7 days Free, 30 days Paid** | Paid is required anyway; still schedule off-platform exports. |
| `*.stometa.dev/*` **does not match the apex** | Configure a second `stometa.dev/*` route. |
| Universal SSL covers **one** wildcard level | `<slug>.stometa.dev` is free; `x.y.stometa.dev` is not. Never nest. |
| Turnstile is **unsupported in Mainland China** | Hence D13. Do not reintroduce it. |
| `__Host-` cookies are rejected by browsers if they carry `Domain` | Host-only scoping becomes unfalsifiable. |
| `Origin` cannot be forged by page JS | Origin allowlist must **fail closed**. |
| Same-site subdomains still attach `SameSite=Lax` cookies | Origin check is the real wall, not SameSite. |
| Turndown **destroys markdown tables**; fenced code survives | The D09 round-trip gate is load-bearing. |
| `.dev` is HSTS-preloaded | HTTPS only, no http fallback during setup. |

---

## 4. Architecture

```
                    ┌─────────────────── one Worker deployment ───────────────────┐
  reader ──────────▶│  route: stometa.dev/*        → publication + admin (trusted)│
  recipient ───────▶│  route: *.stometa.dev/*      → artifacts (untrusted HTML)   │──▶ D1
  CLI (lavish) ────▶│  route: stometa.dev/api/*    → API-key ingest               │──▶ R2
                    └──────────────────────────────────────────────────────────────┘
```

### Host classification — allowlist, never "not the apex"

The `Host` header is attacker-controlled. Classification runs **before** the
TanStack router and **fails closed**:

1. Parse the hostname from the request URL (not the raw header); lowercase, strip
   port, reject trailing dots and non-ASCII/IDN unless explicitly normalized.
2. If the hostname is on the **infrastructure allowlist** (`stometa.dev`,
   `www.stometa.dev`, `staging.stometa.dev`) → publication/admin path.
3. Otherwise it must be **exactly one** additional ASCII label under
   `stometa.dev`, not on the reserved list, and present in `artifact` → artifact path.
4. Anything else → 404. No fallthrough to an authenticated route, ever.

Reserved and unclaimable: `www api admin staging app cdn assets mail smtp imap mx
_dmarc _domainkey autodiscover _acme-challenge`.

### The four D04 controls — indivisible

1. Session cookie uses the `__Host-` prefix.
2. Every mutating route validates `Origin` against an exact allowlist, failing closed.
3. Artifact responses carry the full CSP in §6.2 — `connect-src 'self'` alone is insufficient.
4. Host classification above, plus the reserved-slug list.

---

## 5. Data model

```sql
CREATE TABLE translation_group (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL);

CREATE TABLE post (
  id INTEGER PRIMARY KEY,
  slug TEXT NOT NULL,
  locale TEXT NOT NULL CHECK (locale IN ('zh','en')),
  title TEXT NOT NULL,
  description TEXT,
  body_markdown TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','published','unpublished')),
  editor_mode TEXT NOT NULL DEFAULT 'markdown' CHECK (editor_mode IN ('markdown','rich')),
  category TEXT,
  featured INTEGER NOT NULL DEFAULT 0,
  translation_group_id INTEGER REFERENCES translation_group(id),  -- NULL for unpaired
  cover_image TEXT,
  deleted_at TEXT,                    -- soft delete; revisions must outlive the post
  published_at TEXT,
  updated_at TEXT NOT NULL,
  UNIQUE (locale, slug)
);
CREATE INDEX idx_post_archive ON post (locale, status, published_at DESC);
-- At most one zh + one en per group. The uniqueness comes from SQL treating
-- NULLs as DISTINCT under UNIQUE, NOT from the WHERE clause -- a plain
-- UNIQUE(translation_group_id, locale) is equally correct and is what MySQL
-- (no partial indexes) must use. The predicate is only an index-size
-- optimisation. Do not "strengthen" the MySQL form; it is not weaker.
CREATE UNIQUE INDEX idx_post_group ON post (translation_group_id, locale)
  WHERE translation_group_id IS NOT NULL;

CREATE TABLE post_revision (
  id INTEGER PRIMARY KEY,
  post_id INTEGER NOT NULL REFERENCES post(id) ON DELETE RESTRICT,
  body_markdown TEXT NOT NULL,
  title TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX idx_revision_post ON post_revision (post_id, created_at DESC);

CREATE TABLE commenter (
  id INTEGER PRIMARY KEY, display_name TEXT NOT NULL, email TEXT,
  trusted INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL
);

CREATE TABLE comment (
  id INTEGER PRIMARY KEY,
  post_id INTEGER NOT NULL REFERENCES post(id) ON DELETE CASCADE,
  commenter_id INTEGER NOT NULL REFERENCES commenter(id),
  parent_id INTEGER REFERENCES comment(id),
  body TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','approved','spam')),
  created_at TEXT NOT NULL
);
CREATE INDEX idx_comment_post ON comment (post_id, status, created_at);
CREATE INDEX idx_comment_queue ON comment (status, created_at) WHERE status = 'pending';

CREATE TABLE artifact (
  slug TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('html','pdf')),
  current_revision_id INTEGER REFERENCES artifact_revision(id),
  visibility TEXT NOT NULL DEFAULT 'password'
    CHECK (visibility IN ('public','password','invited')),
  password_verifier TEXT,
  update_key_hash TEXT NOT NULL,
  access_version INTEGER NOT NULL DEFAULT 1,
  expires_at TEXT,
  withdrawn_at TEXT,
  created_at TEXT NOT NULL,
  CHECK (visibility <> 'password' OR password_verifier IS NOT NULL)
);

CREATE TABLE artifact_revision (     -- R2 objects are immutable; replace = new row
  id INTEGER PRIMARY KEY,
  artifact_slug TEXT NOT NULL REFERENCES artifact(slug) ON DELETE RESTRICT,
  r2_key TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE artifact_view (
  id INTEGER PRIMARY KEY,
  artifact_slug TEXT NOT NULL REFERENCES artifact(slug) ON DELETE CASCADE,
  viewed_at TEXT NOT NULL, country TEXT, referer TEXT
);
CREATE INDEX idx_view_artifact ON artifact_view (artifact_slug, viewed_at DESC);
```

**Retention.** `artifact_view` is append-only and must not grow unbounded: keep raw
rows **90 days**, roll older data into a per-artifact per-day count, and run the
prune on a scheduled Worker. Budget the write cost against the D1 daily quota.

**Deletion.** `post` is **soft-deleted** (`deleted_at`); revisions use
`ON DELETE RESTRICT` because after leaving git they are the only audit trail.
Hard purge is a separate, deliberate administrative procedure that exports first.

**Publish idempotency.** `UNIQUE(locale,slug)` prevents duplicate rows but is not
by itself a race protocol — two writers can both read "absent". Publishing is a
single transactional upsert carrying a client-supplied idempotency key and
returning the canonical row, so a retry is unambiguous. Test concurrent publishes.

`tags` is deliberately absent — existing tag data is dropped at migration. If tags
are wanted, add a normalized table **before** import.

---

## 6. Subsystems

### 6.1 Comments and the bot gate (D05, D13)

Always on: per-IP and per-post rate limits, plus a honeypot field. Escalate to a
self-hosted ALTCHA proof-of-work challenge when a submission looks risky (new
commenter, burst, suspicious UA), served first-party from `stometa.dev`.
Requirements: nonce expiry and single use, server-side proof verification,
exponential backoff, and a no-JavaScript accessibility fallback. A new Commenter's
first comment is held; approving it sets `trusted = 1`.

**The comment UI is itself bilingual** — form labels, validation and error copy,
and the moderation queue follow the page locale. A bilingual site does not get
bilingual comment controls for free.

### 6.2 Artifacts (D04, D06, D14)

Ingest is a drop-in for `lavish-axi share`: `POST` with a JSON body whose
`html_content` is one complete HTML string (`lavish-axi/src/html-app.js:17`),
authenticated by API key.

> **Known interface conflict:** lavish-axi publishes *public* when `--password` is
> omitted; our default is `password`. Reject with `422 password_required` rather
> than silently changing the caller's intent.

**Served paths are an allowlist**: `/` and `POST /_artifact/unlock` only. Every
other path on an artifact host 404s. R2 objects are immutable — replacing an
artifact writes a new `artifact_revision` and repoints `current_revision_id`.

```
Content-Security-Policy: default-src 'none'; base-uri 'none'; object-src 'none';
  frame-ancestors 'none'; form-action 'self'; script-src 'unsafe-inline' https:;
  style-src 'unsafe-inline' https:; img-src 'self' data: blob: https:;
  font-src data: https:; media-src data: blob: https:; connect-src 'self';
  worker-src blob:; manifest-src 'none'; upgrade-insecure-requests
X-Robots-Tag: noindex, nofollow      (unless visibility = public)
Cache-Control: private, no-store     (unless visibility = public)
Vary: Cookie
```

**Password gate.** A signed, **host-only** capability cookie scoped to the artifact
host — never an apex cookie, never a password in the URL. The token is bound to
the artifact slug and `access_version`. Verification uses a **constant-time MAC
comparison**; the KDF and its parameters must be **benchmarked against the Workers
CPU budget** before selection (proof verification is CPU, and CPU is the metered
resource). Rate-limit per artifact+IP with exponential backoff.

**Revocation is partial and must be stated:** bumping `access_version` invalidates
issued tokens, but cannot recall HTML a viewer has already loaded, cached or saved.

**Status semantics.** Expired → `410 Gone`; withdrawn → `410 Gone`; unknown slug →
`404`. This deliberately reveals that a slug once existed
([ADR-0010](../../adr/0010-artifact-scope-for-v1.md)) so a recipient learns the
link was real and is over. Keep body, cache headers and timing uniform so it does
not become an enumeration oracle. If a future artifact needs concealment, it must
use `404` instead — decide per artifact, not globally.

### 6.3 Search (D15)

The static JSON index becomes a D1 query. **SQLite FTS5 standard tokenizers do not
segment Chinese** — a CJK-capable tokenizer (trigram, or an external segmenter)
must be chosen and tested against the real corpus. A design task, not a setting.

### 6.4 Social cards (D15)

Four card images per post exist today, generated off-site. On Workers this needs
satori + resvg in WASM, or Cloudflare Browser Rendering. **Its own spike.** CJK
glyph coverage is the crux — the font must be subset or the payload is large.

### 6.5 Links hub (D15)

`content/links.md` → a page at `/links`. Low complexity.

### 6.6 Post images

`static/images/<slug>/card*.png` has no equivalent once Hugo is gone. Post images
move to **R2**, served from the apex (not an artifact host), with the admin
uploader writing there and `cover_image` storing the key. This migration is
required in Phase 1 or existing covers 404.

---

## 7. Migration

Full inventory and per-post defects: [`post-migration-map.md`](post-migration-map.md).

**Redirects.** One bulk rule `stometa.top/*` → `stometa.dev/*` carries the 11
Chinese posts unchanged (percent-encoded CJK paths preserved byte-for-byte). Three
English posts get hand rules to `/en/posts/…`. A dedicated 301 for `/index.xml`
with the feed's self-`<link>` updated — **omit this and every RSS subscriber goes
silent without telling you.**

**Merged or unpublished posts need a URL policy.** The migration map recommends
retiring some thin posts; "every existing URL resolves" is only true if each such
post redirects to its merge target or returns 410. Decide per post before Phase 1's gate.

**Editorial work required before import** — not a lift-and-shift:

- 6 posts have no slug → use the migration map's derived slugs; never re-derive.
- 5 posts have no description → write them.
- Cloudflare+Resend post has neither category nor tags → set `category`.
- `Google UCP` uses a `summary` field with no target column → copy to `description`.
- **The flagship is rewritten as markdown (D16)** — 299 HTML tags, an inline
  `<style>` block and an in-body Google Fonts import go; content survives.
- **Unpaired posts import `translation_group_id = NULL`.** No group per post — that
  would emit false `hreflang` pairs. No pairs exist today, so no groups exist yet.

**Locale inversion** is *not* merely two config edits: `project.inlang/settings.json:3`
(`baseLocale`) and `vite.config.ts:70-99` (`urlPatterns`) change **together**, the
route tree is regenerated by the build (never hand-edited), and canonical,
alternate, RSS and redirect behaviour must all be retested for zh-at-root.

**Strip order:** follow [`shipany-strip-plan.md`](shipany-strip-plan.md) — call
sites first (`api/user/info.ts`, `sign-up.tsx`, `admin/users.tsx`,
`admin/route.tsx`), then routes, then modules, then all four schema files, then
`init-rbac.ts`. Build after each step.

---

## 8. Cross-cutting requirements

Named here because they belong to no single phase and are the classic omissions:

| Concern | Requirement |
|---|---|
| **Admin bootstrap** | One-time credential creation, rotated immediately after first login. Staging and production use separate credentials and isolated cookie scopes. Define an account-recovery path before there is content to lose. |
| **Backup & restore** | Time Travel is not a backup strategy. Scheduled `wrangler d1 export` to storage outside the same credential boundary, plus a **restore drill** performed once before cutover. |
| **Round-trip gate (D09)** | Compares **re-rendered HTML**, not markdown text: permit rich mode iff `render(md) == render(turndown(render(md)))`. Byte comparison was measured and fails on every input, so it would refuse rich mode permanently. Fixtures assert the measured truth: code fences, nested lists, footnotes, block HTML, CJK and links pass; **tables and blockquotes fail**. The toggle calls the same code path. |
| **Drafts & preview** | Draft posts must be viewable at a stable preview URL, `noindex`, without publishing. This is the main friction reducer permitted under ADR-0012. |
| **Error pages** | Localized 404 and 500 for the publication; distinct artifact 404 / 410 pages. HSTS makes setup failures user-visible, so these are not cosmetic. |

---

## 9. Phases

Hugo serves `stometa.top` untouched throughout. The app deploys continuously to a
password-protected, `noindex` staging host from Phase 0 — cutover is a DNS change
against a system that has been running for weeks.

| Phase | Content | Exit gate |
|---|---|---|
| **0 · Foundation** | Cloudflare zone; wildcard **and apex** routes; fork + strip; D1 + R2; Workers Paid; admin bootstrap; staging host | Clean build after **each** strip step; migrations applied; D1 read/write smoke test; admin can log in on staging |
| **1 · Publication** | Schema + indexes; locale inversion; image migration to R2; editorial work then import; markdown editor + round-trip fixtures; draft preview; editorial front page; RSS/sitemap/hreflang; error pages | Every existing URL resolves **or has a declared redirect/410**; round-trip fixtures pass; concurrent publish test passes |
| **2 · Conversation + sharing** | Comments + gate + bilingual queue; artifacts HTML+PDF, revisions, withdrawal, expiry, view tracking + prune job; the four D04 controls | An artifact host provably cannot reach an authenticated route; host-classification fuzz test passes; password gate resists timing analysis |
| **3 · Search + cards** | FTS5 with CJK tokenizer; social card pipeline; `/links` | Chinese full-text search returns correct results **on the real corpus** |
| **4 · Cutover** | Migrate anything published to Hugo meanwhile; DNS; bulk + hand redirects; feed 301; GA4 re-point; sitemap resubmit; archive HugoBlog | Old deep links resolve, feed readers follow, analytics continuous; restore drill completed |

---

## 10. Open items

1. ~~Is `stometa.dev` on Cloudflare nameservers?~~ **Resolved 2026-08-11: owned and already on Cloudflare.** No nameserver move needed; Phase 0 starts at zone configuration.
2. **Social card pipeline** — satori/resvg vs Browser Rendering. CJK font subsetting is the crux.
3. **FTS5 CJK tokenizer** — trigram vs external segmenter. Test on the real corpus.
4. **ALTCHA difficulty** under the Workers CPU budget.
5. **Editorial categories** — 工程实践 / 量化 / AI 工具 / 随笔 are inferred from content, not chosen by the author.
6. **Which thin posts are merged or unpublished**, and what their old URLs do.
7. **The blog route is still `/blog/<slug>`, not `/posts/<slug>`.** The template's
   route is `/blog`; every existing Hugo URL is `/posts/<slug>/`. D10 promises
   byte-for-byte slug preservation under one bulk 301, which is only true once
   the route is renamed. Until then the Phase 1 exit gate ("every existing URL
   resolves") cannot pass. Rename the route, do not add a second redirect layer.

---

*Reviewed adversarially 2026-08-11; 5 blockers and 5 major findings applied. See
[`plan-review.md`](plan-review.md) for the full findings table.*
