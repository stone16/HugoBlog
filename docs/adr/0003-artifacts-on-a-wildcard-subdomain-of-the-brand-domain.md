---
status: accepted
---
# Artifacts are served from a wildcard subdomain of the brand domain

An Artifact is arbitrary HTML with inline JavaScript, so where it is served from
is a security boundary, not a naming preference. We serve it at
`<slug>.stometa.dev` — a distinct origin from the Admin, but the same site —
choosing a single coherent brand over the stronger isolation a separate
registrable domain would have given.

## Considered Options

Serving Artifacts from a second registrable domain (`<slug>.stometa.top`, already
owned) is what Vercel, Netlify, Cloudflare Pages and GitHub all do, because the
Public Suffix List boundary blocks cookie and CSRF paths that same-site
subdomains do not. Rejected in favour of brand coherence. Path-based
(`stometa.dev/s/<slug>`) was rejected outright: it runs third-party script on the
Admin's own origin.

## Consequences

Because same-site subdomains still attach `SameSite=Lax` cookies, the isolation
must be enforced by the browser rather than by discipline:

- the session cookie carries the `__Host-` prefix, which browsers reject if a
  `Domain` attribute is present, making host-only scoping unfalsifiable;
- every mutating API route checks the unforgeable `Origin` header against an
  exact allowlist;
- Artifact responses carry a `Content-Security-Policy`. **Corrected 2026-08-11:**
  `connect-src 'self'` alone is not a sufficient policy — a self-contained
  Artifact still needs `script-src 'unsafe-inline'`, `img-src data: blob:` and
  `font-src data:` to render at all. The full header is specified in
  `docs/designs/stometa-dev/artifact-hosting-spike.md`;
- infrastructure labels (`www`, `api`, `admin`, `mail`, `_dmarc`, …) are
  permanently reserved and never claimable as a Slug.

Drop any one of these and the decision stops being defensible. C5, C6 and C7 of
`docs/designs/stometa-dev/verification-cloudflare.md` verify the threat model this
rests on: `SameSite` is not an origin boundary, and an attacker-controlled
same-site subdomain can initiate credentialed requests even when CORS stops it
reading the response. The `Origin` check must fail **closed**.

**Routing correction 2026-08-11:** a `*.stometa.dev/*` Worker route does **not**
match the apex — Cloudflare: "If a route pattern hostname begins with `*.`, then
it only matches all subhosts." Configure `stometa.dev/*` as a separate route.

**Cost correction 2026-08-11:** Workers Free caps CPU at 10 ms per request, and
Cloudflare itself places auth/SSR-heavy work at 10–20 ms. This design should
budget **Workers Paid, US$5/month minimum**; Free is a prototype surface, not a
production assumption. That also restores 30-day D1 Time Travel (see ADR-0001).
