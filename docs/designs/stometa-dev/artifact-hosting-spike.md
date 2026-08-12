# Artifact hosting design spike

Status: proposed  
Target: `stometa.dev`, TanStack Start on Cloudflare Workers  
Reference implementation inspected: `/Users/stometa/dev/lavish-axi`, ref
`codex/queued-question-feedback` at `9060866` (read only)

## Executive decision

Use one Worker deployment, reached by two route families. Requests whose normalized
`Host` is exactly `stometa.dev` (and explicitly supported infrastructure hosts) go to
TanStack Start. A valid single-label `<slug>.stometa.dev` request bypasses TanStack's
router and goes to the artifact handler; every other host fails closed with `404`.
Store immutable artifact bodies in R2 and the current pointer/access metadata in D1.

Two requirements need a visible qualification rather than being silently blended:

1. Lavish/ht-ml.app creation is public when `password` is omitted, whereas the agreed
   stometa.dev policy defaults to `password` plus `noindex`. The proposed endpoint is
   **wire-compatible**, but cannot be behaviorally drop-in for an old client that omits
   `password`: it must either reject that request with `422 password_required`, or a
   separately named, explicitly enabled compatibility policy must preserve ht-ml.app's
   public default. This design chooses rejection.
2. Current Lavish allows unauthenticated creation and treats Bearer auth as optional
   ([`html-app.js:3-7`](file:///Users/stometa/dev/lavish-axi/src/html-app.js#L3-L7));
   stometa.dev requires an API key. An unchanged Lavish binary is compatible only when
   `LAVISH_AXI_HTML_APP_TOKEN`/`--token` is configured.

## 1. The actual Lavish share wire format

Lavish does **not** upload a directory, archive, multipart form, or asset bundle. It first
turns the source into one HTML string, then sends that string in one JSON document. Share
calls the same `buildSelfContainedHtml` transform as export and passes its returned `html`
directly to the publisher ([`cli.js:496-518`](file:///Users/stometa/dev/lavish-axi/src/cli.js#L496-L518)).

### Create request

```http
POST https://api.ht-ml.app/v1/sites HTTP/1.1
Content-Type: application/json
User-Agent: lavish-axi
Authorization: Bearer <optional-token>   # omitted when not configured

{"html_content":"<!doctype html>...one complete HTML string...","password":"optional"}
```

Precise client behavior:

- API base defaults to `https://api.ht-ml.app`, with trailing slashes removed
  ([`html-app.js:9-14`](file:///Users/stometa/dev/lavish-axi/src/html-app.js#L9-L14)).
- The body always has string field `html_content`. `password` is trimmed and included only
  when non-empty ([`html-app.js:16-20`](file:///Users/stometa/dev/lavish-axi/src/html-app.js#L16-L20)).
- The request is JSON, `POST`, with `User-Agent: lavish-axi`; a configured token becomes
  `Authorization: Bearer …` ([`html-app.js:35-54`](file:///Users/stometa/dev/lavish-axi/src/html-app.js#L35-L54)).
- The entire fetch plus response-body read has a 30-second abort timeout
  ([`html-app.js:10,44-65`](file:///Users/stometa/dev/lavish-axi/src/html-app.js#L10-L65)).

### Create response

The observed/tested success shape is:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "site_id": "abc123",
  "url": "https://abc123.ht-ml.app/",
  "update_key": "uk_secret",
  "status": "active"
}
```

`url` and `update_key` are mandatory to this client; missing either makes an otherwise 2xx
response fail. `site_id` and `status` may be absent and are normalized to empty strings
([`html-app.js:67-85`](file:///Users/stometa/dev/lavish-axi/src/html-app.js#L67-L85)). The
repository test asserts the exact method, URL, JSON body, optional auth behavior, and response
mapping ([`html-app.test.js:37-74`](file:///Users/stometa/dev/lavish-axi/test/html-app.test.js#L37-L74)).
The password itself is not returned; the CLI only reports whether the share was protected
([`cli.js:521-538`](file:///Users/stometa/dev/lavish-axi/src/cli.js#L521-L538)).

The client surfaces JSON `detail`, then `error`, then `message`; without those it gives special
descriptions for `422`, `401`, and `403` ([`html-app.js:88-94`](file:///Users/stometa/dev/lavish-axi/src/html-app.js#L88-L94)).
The ht-ml.app update and delete HTTP methods, paths, bodies, and status codes are **UNVERIFIED**:
the inspected Lavish source does not implement those calls. Therefore only `POST /v1/sites`
can honestly be called drop-in compatible from this evidence.

## 2. Export and asset behavior

`buildSelfContainedHtml` produces one string. It turns local stylesheets and scripts into
inline blocks and local binary assets/fonts into data URIs; supported MIME types include CSS,
JS, common images, WOFF/WOFF2/TTF/OTF, media, JSON, and PDF
([`export-bundle.js:5-45`](file:///Users/stometa/dev/lavish-axi/src/export-bundle.js#L5-L45)). Reads
are confined lexically and after symlink resolution to the artifact directory, except trusted
caller mappings; default caps are 10 MiB per asset and 25 MiB total
([`export-bundle.js:47-50,114-151`](file:///Users/stometa/dev/lavish-axi/src/export-bundle.js#L47-L50)).
Root-absolute references are only inlined when Lavish's trusted `/design` resolver maps them
([`cli.js:512-516`](file:///Users/stometa/dev/lavish-axi/src/cli.js#L512-L516)).

Remote `http:`, `https:`, protocol-relative, and other explicit-scheme references are classified
as `skip` and left byte-for-byte as browser-time references; they are never fetched during export
([`export-bundle.js:2338-2363`](file:///Users/stometa/dev/lavish-axi/src/export-bundle.js#L2338-L2363)).
Local references that cannot be safely inlined remain references plus warnings and can break after
the HTML moves ([`cli.js:466-487`](file:///Users/stometa/dev/lavish-axi/src/cli.js#L466-L487)).

Consequences:

- Mermaid is not actually self-contained when it uses Lavish's recommended module import:
  it imports Mermaid from jsDelivr at render time
  ([`design-reference.js:13,19-21`](file:///Users/stometa/dev/lavish-axi/src/design-reference.js#L13-L21)).
  Offline viewing, CDN failure, blocking, or a CSP that omits that origin leaves the source
  container unrendered.
- A remote CSS/font reference similarly depends on the viewer's network, the CDN's CORS behavior,
  and `style-src`/`font-src`. A stylesheet may in turn fetch relative font URLs from its own origin.
- Pin remote assets to immutable versions and SRI where the element supports it. For artifacts that
  must be durable/offline, vendor those files locally before Lavish export so they become inline.

## 3. One Worker for apex and wildcard hosts

### Verified deployment mechanism

TanStack Start's server entry is a universal `fetch` handler. Its official custom-entry example
creates `src/server.ts`, imports `handler`/`createServerEntry`, and delegates with
`handler.fetch(request)`; that file is the entry for SSR, server routes, and server functions
([TanStack Start: Server entry point](https://tanstack.com/start/latest/docs/framework/react/guide/server-entry-point)).
Cloudflare's TanStack guide says to point Wrangler `main` at `src/server.ts` for a custom entry
([Cloudflare: TanStack Start custom entrypoints](https://developers.cloudflare.com/workers/framework-guides/web-apps/tanstack-start/#custom-entrypoints)).
This is the correct interception point; a TanStack file route is too late because an arbitrary
host must not enter blog/admin middleware or inherit its cookies/headers.

Cloudflare Worker Routes support a leading wildcard hostname, and `*.example.com` matches subhosts
but not the apex. Routes require matching proxied DNS; route matching prefers the most specific
pattern ([Cloudflare: Workers routes](https://developers.cloudflare.com/workers/configuration/routing/routes/)).
Cloudflare Custom Domains do **not** support wildcard DNS records, so do not attempt to declare
`*.stometa.dev` as `custom_domain: true`
([Cloudflare: Custom Domains](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/)).
Instead, configure an orange-clouded `*.stometa.dev` DNS record; Cloudflare documents that wildcard
DNS is proxied-capable and applies only when no exact record takes precedence
([Cloudflare: wildcard DNS records](https://developers.cloudflare.com/dns/manage-dns-records/reference/wildcard-dns-records/)).

Illustrative Wrangler trigger config (the exact apex choice may be a Custom Domain or a zone route):

```jsonc
{
  "main": "src/server.ts",
  "routes": [
    { "pattern": "stometa.dev/*", "zone_name": "stometa.dev" },
    { "pattern": "*.stometa.dev/*", "zone_name": "stometa.dev" }
  ],
  "r2_buckets": [{ "binding": "ARTIFACTS", "bucket_name": "stometa-artifacts" }],
  "d1_databases": [{ "binding": "DB", "database_name": "stometa-dev", "database_id": "…" }]
}
```

### Host branch, before TanStack

```ts
import startHandler, { createServerEntry } from '@tanstack/react-start/server-entry'

export default createServerEntry({
  async fetch(request, env, ctx) {
    const url = new URL(request.url)
    const host = url.hostname.toLowerCase().replace(/\.$/, '')

    if (host === 'stometa.dev' || host === 'www.stometa.dev') {
      return startHandler.fetch(request, { context: { env, ctx } })
    }

    const suffix = '.stometa.dev'
    const slug = host.endsWith(suffix) ? host.slice(0, -suffix.length) : null
    if (!slug || slug.includes('.') || !isValidSlug(slug) || RESERVED.has(slug)) {
      return new Response('Not found', { status: 404 })
    }

    return serveArtifact(request, env, ctx, slug)
  },
})
```

The exact second argument used by the installed TanStack Start version must be confirmed while
implementing; the current official interface documents optional request options, while Cloudflare's
custom-entry sample shows the environment in its Workers entry shape. The above context plumbing is
therefore **UNVERIFIED pseudocode**, not copy/paste implementation. The architectural invariant is
verified: inspect `URL.hostname`, branch, and return before `startHandler.fetch`.

`serveArtifact` performs `SELECT … WHERE slug = ? AND withdrawn_at IS NULL`. No row, withdrawn row,
reserved/invalid label, non-root artifact path, or absent R2 object returns the same small `404` with
`Cache-Control: no-store`; never fall through to TanStack. Initially serve only `/` and reject every
other artifact path except the password POST endpoint and Cloudflare-managed `/cdn-cgi/` path.

## 4. Artifact response headers

### HTML

Recommended compatibility policy for today's Lavish output:

```http
Content-Type: text/html; charset=utf-8
Content-Security-Policy: default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; script-src 'unsafe-inline' https:; style-src 'unsafe-inline' https:; img-src 'self' data: blob: https:; font-src data: https:; media-src data: blob: https:; connect-src 'self'; worker-src blob:; manifest-src 'none'; upgrade-insecure-requests
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
Cross-Origin-Opener-Policy: same-origin
```

Add `X-Robots-Tag: noindex, nofollow, noarchive, nosnippet` for `password` and `invited` visibility,
including gate/error responses. Public artifacts omit it (or explicitly use `index, follow`).

Why this CSP is deliberately permissive in specific places:

- Lavish emits inline `<script>`/`<style>` blocks, so a static response cannot use per-request
  nonces without parsing and rewriting user HTML. CSP requires `'unsafe-inline'`, a nonce, or a
  matching hash for inline scripts ([MDN: `script-src`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/script-src#unsafe_inline_script)).
- `data:` is needed for inlined images/fonts/media, but not in `script-src`. `blob:` is allowed only
  where common client renderers/workers need it.
- `connect-src 'self'` controls `fetch`, XHR, WebSocket, EventSource, and Beacon; it does not control
  module/script loading or fonts ([MDN: `connect-src`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/connect-src)).
  Thus it does not break a truly self-contained artifact, Mermaid's CDN module is governed by
  `script-src`, and CDN fonts are governed by `font-src`.

Counterpoint: `https:` in script/style/image/font sources is broad, and inline arbitrary script can
still signal through permitted resource loads. This policy is compatibility hardening, **not an
exfiltration boundary**. A stronger later mode should derive exact origins from the uploaded HTML
and store a per-revision CSP, but redirects/transitive module imports make that operationally brittle.
The accepted same-site wildcard architecture is materially weaker than a second registrable artifact
domain; apex `__Host-` cookies and exact-Origin checks on every mutating apex API remain mandatory.

Cache policy:

- `public`: `Cache-Control: public, max-age=60, s-maxage=31536000, immutable` is safe only when the
  R2 object URL/revision is immutable. The permanent slug response itself changes on replacement, so
  use `Cache-Control: public, max-age=60, s-maxage=60, stale-while-revalidate=300` there and purge the
  exact hostname on publish/withdraw. Return a strong ETag equal to the stored SHA-256 revision hash.
- `password`/`invited`, the gate, and authentication failures: `Cache-Control: private, no-store` and
  `Vary: Cookie`; never place decrypted/protected HTML in shared cache.

### PDF

Return `Content-Type: application/pdf`, `X-Content-Type-Options: nosniff`, the same robots/cache/access
headers, and `Content-Disposition: inline; filename="<safe-slug>.pdf"; filename*=UTF-8''<encoded>` so
browsers render it when supported. Offer an explicit download route/query that changes only this to
`attachment`. MDN defines `inline` as display and `attachment` as download
([MDN: Content-Disposition](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Disposition)).
CSP does not meaningfully sandbox a browser PDF viewer; access control and `nosniff` do the work.

## 5. Password gate

Use a signed, host-only capability cookie, not an apex cookie and not a password in the URL.

1. `GET https://slug.stometa.dev/` without a valid token returns a minimal server-owned password
   form and `no-store`/`noindex`.
2. `POST /_artifact/unlock` accepts the password, rate-limits by artifact plus IP bucket, verifies a
   salted password verifier, and on success returns `303 /` with:
   `Set-Cookie: __Host-artifact_access=<signed-token>; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800`.
   The `__Host-` prefix requires `Secure`, `Path=/`, and no `Domain`, making it host-only.
3. Token payload: version, artifact UUID, `access_version`, issued-at, expiry. Sign the canonical
   payload with HMAC-SHA-256 using a rotated Worker secret; compare MACs in constant time. Increment
   `access_version` whenever password/visibility changes or access must be revoked.
4. Verify the request host maps to the token's artifact ID before reading R2. Never accept the cookie
   on apex routes, even if a client sends it manually.

Store a salted verifier, never plaintext. PBKDF2-HMAC-SHA-256 via Workers Web Crypto is deployable,
but iteration count and CPU-limit behavior must be benchmarked before selection; the final password
KDF parameters are **UNVERIFIED**. Add exponential backoff/rate limiting because readable slugs make
online guessing easy.

Failure modes: cookie theft grants access until expiry; HMAC-key compromise grants all artifacts;
host XSS can read protected content despite `HttpOnly`; cookies vanish in strict/privacy browsing;
revocation needs an `access_version` D1 read unless cached briefly; wildcard same-site origins remain
same-site even though the cookie is host-only. A signed query parameter is rejected as the default
because it leaks into history, copy/paste, logs, referrers, and screenshots. It may be useful only as
a short-lived, single-use invitation exchanged immediately for the same host-only cookie.

## 6. Reserved slug list

Validate claimable slugs as lowercase ASCII `[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?`, then reject
the following set case-insensitively forever. Some underscore names cannot pass that hostname rule;
reserving them anyway prevents a future validator/DNS-management change from creating collisions.

| Group | Permanently reserved labels | Why |
|---|---|---|
| Product/infrastructure | `www`, `api`, `admin`, `staging`, `stage`, `app`, `cdn`, `assets`, `static`, `media`, `files`, `download`, `uploads`, `auth`, `login`, `account`, `dashboard`, `status`, `support`, `help`, `docs`, `blog`, `dev`, `test`, `preview`, `beta`, `internal`, `origin`, `gateway`, `webhook`, `hooks` | Keeps present/future first-party services, environments, origins, and operator surfaces from becoming permanent user addresses. Exact DNS records override wildcard DNS, so collisions otherwise change routing semantics. |
| Mail | `mail`, `email`, `smtp`, `imap`, `pop`, `pop3`, `mx`, `webmail`, `autodiscover`, `autoconfig`, `_dmarc`, `_domainkey`, `default._domainkey`, `selector1._domainkey`, `selector2._domainkey`, `_mta-sts`, `mta-sts` | Protects MX/client discovery, DKIM, DMARC and MTA-STS names from squatting or later DNS conflicts. Dotted DKIM owners are not single artifact labels, but their component labels are reserved defensively. |
| Verification/discovery | `_acme-challenge`, `_cf-custom-hostname`, `acme-challenge`, `cf-custom-hostname`, `well-known`, `.well-known`, `_well-known`, `security`, `pki-validation`, `google-site-verification`, `facebook-domain-verification`, `apple-domain-verification` | Preserves ACME/DCV, ownership-verification, security contact, and platform-validation namespaces. Cloudflare documents `_acme-challenge` for certificate DCV and `_cf-custom-hostname` for hostname ownership ([Cloudflare hostname validation](https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/security/certificate-management/issue-and-validate/validate-certificates/txt/)). `.well-known` is normally a path, not a host label; it is included as defense in depth. |
| Cloudflare/platform | `cloudflare`, `cf`, `cdn-cgi`, `cloudflareinsights`, `workers`, `pages` | Prevents misleading platform-looking hosts and leaves room for platform integration. Cloudflare's actual reserved surface here is the **path** `/cdn-cgi/`, which it manages and says cannot be customized ([Cloudflare `/cdn-cgi/`](https://developers.cloudflare.com/fundamentals/reference/cdn-cgi-endpoint/)); Cloudflare does not document all these words as reserved DNS labels, so the broader list is a stometa.dev policy, not a Cloudflare requirement. |
| DNS/service conventions | `ns`, `ns1`, `ns2`, `dns`, `ftp`, `ssh`, `vpn`, `proxy`, `localhost`, `broadcasthost`, `hostmaster`, `postmaster`, `abuse`, `noc`, `whois`, `wpad`, `_tcp`, `_udp`, `_tls`, `_sip`, `_xmpp`, `_caldav`, `_carddav` | Avoids nameserver/service-discovery, privileged contact, proxy-autodiscovery, and conventional operational collisions. |

Also reject the empty label, `-` edges, dots, Unicode/punycode (`xn--`) until an explicit IDN threat
model exists, IP-looking labels, and every current exact DNS owner obtained from the Cloudflare DNS
API at create time. The static list prevents future claims; the live DNS collision check catches names
introduced after deployment. A DB uniqueness constraint remains the final race-safe authority.

## 7. D1 schema and CLI contract

### Schema

```sql
CREATE TABLE artifacts (
  id TEXT PRIMARY KEY,                         -- UUIDv7
  slug TEXT NOT NULL COLLATE NOCASE UNIQUE,
  kind TEXT NOT NULL CHECK (kind IN ('html', 'pdf')),
  visibility TEXT NOT NULL DEFAULT 'password'
    CHECK (visibility IN ('public', 'password', 'invited')),
  noindex INTEGER NOT NULL DEFAULT 1 CHECK (noindex IN (0, 1)),
  current_revision_id TEXT,
  password_verifier TEXT,                     -- encoded algorithm + params + salt + digest
  access_version INTEGER NOT NULL DEFAULT 1,
  update_key_hash BLOB NOT NULL,               -- HMAC/peppered hash; never the raw key
  created_by_key_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  withdrawn_at TEXT,
  CHECK (visibility <> 'password' OR password_verifier IS NOT NULL),
  CHECK (visibility <> 'public' OR noindex IN (0, 1))
);

CREATE TABLE artifact_revisions (
  id TEXT PRIMARY KEY,                         -- UUIDv7
  artifact_id TEXT NOT NULL REFERENCES artifacts(id) ON DELETE RESTRICT,
  object_key TEXT NOT NULL UNIQUE,             -- artifacts/<id>/<revision>.(html|pdf)
  sha256 BLOB NOT NULL,
  byte_length INTEGER NOT NULL CHECK (byte_length >= 0),
  content_type TEXT NOT NULL,
  csp TEXT,                                    -- exact policy served for this revision
  created_by_key_id TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX artifact_revisions_artifact_created
  ON artifact_revisions(artifact_id, created_at DESC);

CREATE TABLE api_keys (
  id TEXT PRIMARY KEY,
  key_hash BLOB NOT NULL UNIQUE,
  label TEXT NOT NULL,
  scopes TEXT NOT NULL,                        -- JSON array, e.g. ["artifacts:write"]
  created_at TEXT NOT NULL,
  last_used_at TEXT,
  revoked_at TEXT
);

CREATE TABLE artifact_invites (
  id TEXT PRIMARY KEY,
  artifact_id TEXT NOT NULL REFERENCES artifacts(id) ON DELETE CASCADE,
  subject TEXT NOT NULL,                       -- normalized email or principal id
  token_hash BLOB,
  expires_at TEXT,
  revoked_at TEXT,
  UNIQUE (artifact_id, subject)
);
```

D1 cannot atomically commit an R2 write with a SQL transaction. Upload the immutable R2 revision
first, then in one D1 transaction insert the revision and move `current_revision_id`; on D1 failure,
enqueue/delete the orphan object. Never overwrite an R2 key. Reads use the D1 pointer, so an orphan
is invisible and a failed update leaves the previous revision live. Foreign-key enforcement and the
exact D1 support/behavior for the chosen migration tool must be confirmed in implementation and are
**UNVERIFIED**.

### CLI/API contract

Authentication is `Authorization: Bearer sk_artifact_<secret>` over TLS. Store only a keyed hash of
API keys, scope them (`artifacts:write`, optionally `artifacts:admin`), support rotation/revocation,
and never reuse `update_key` as the account API key.

For Lavish compatibility:

```http
POST /v1/sites
Content-Type: application/json
Authorization: Bearer sk_artifact_…

{
  "html_content": "<!doctype html>…",
  "password": "required under the chosen safe-default policy",
  "slug": "optional-readable-slug",
  "visibility": "password"
}
```

`html_content` and optional `password` retain the ht-ml.app types. `slug` and `visibility` are
stometa.dev extensions ignored by old Lavish clients; absent slug is generated once from the title
plus a collision-resistant suffix. Since omission of password cannot create a password-protected
artifact, return `422` with `{"detail":"password is required; visibility defaults to password"}`.
PDF and richer metadata use a first-party endpoint rather than corrupting this JSON contract:

```http
POST /api/artifacts                 # application/json for HTML, or multipart/form-data for PDF
PUT  /api/artifacts/{slug}          # API key + update_key; creates immutable revision
DELETE /api/artifacts/{slug}        # API key + update_key; soft-withdraws, does not free slug
```

For first-party JSON HTML create, accept `slug`, `kind: "html"`, `content`, `visibility`, `password`,
and `noindex` (force `true` when non-public). For PDF multipart, accept one `file` part plus those
metadata fields, enforce MIME sniffing, size limits, and streaming to R2. Replacement and withdrawal
require both the account API key and `X-Artifact-Update-Key`; accepting the update key alone would
make a leaked one a permanent unaudited account bypass.

Success response (use `201 Created` for create):

```json
{
  "site_id": "019…",
  "slug": "readable-permanent-slug",
  "url": "https://readable-permanent-slug.stometa.dev/",
  "update_key": "uk_…",
  "status": "active",
  "visibility": "password",
  "noindex": true,
  "revision": "019…",
  "sha256": "base64url…"
}
```

Return the raw, high-entropy `update_key` only on create; D1 stores its keyed hash. Replacements keep
the same slug and update key unless an explicit rotation endpoint returns a new one. Withdrawal is a
tombstone forever: permanent readable URLs must never be reassigned. Use `400` malformed JSON,
`401` absent/invalid API key, `403` scope/update-key failure (avoid distinguishing which secret was
wrong), `409` slug collision/withdrawn slug, `413` too large, `415` wrong type, and `422` valid JSON
that violates visibility/password policy. All API responses use `Cache-Control: no-store`.

## Implementation verification gates

Before shipping, add end-to-end tests at the Worker boundary for Host branching (apex, known slug,
unknown slug, dotted host, reserved label), old Lavish JSON compatibility, default-password rejection,
R2/D1 failure ordering, update-key rotation/withdrawal, protected cache isolation, cookie host scope,
PDF inline/download headers, and the exact CSP against exported Mermaid/CDN-font fixtures. In a
staging Cloudflare zone, verify wildcard DNS/TLS, route precedence, purge behavior, and raw headers
with `curl` before treating the Wrangler design as production-proven.
