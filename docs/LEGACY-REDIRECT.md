# Legacy `stometa.top` redirects

This repository is the legacy Hugo site still served at `stometa.top` through
GitHub Pages. Because GitHub Pages cannot return a server-side redirect for
arbitrary paths (and the domain is not delegated to Cloudflare), this layer is
necessarily a **soft redirect**. Every rendered document declares its final
`stometa.dev` URL with `rel="canonical"`, emits a zero-second meta refresh, and
shows a visible link for browsers that block refreshes. Canonical URLs are the
SEO signal available here, but they are measurably weaker than an HTTP 301:
consolidation can be slower or incomplete, and the old response still has a
200 status.

The RSS output is handled separately. `index.xml` advertises
`https://stometa.dev/index.xml`, and every item link and GUID points to the
mapped `stometa.dev` post URL. The three English posts receive the `/en/`
prefix; the eleven Chinese posts retain their existing `/posts/<slug>/` path,
including percent-encoded CJK segments.

## Upgrade path to a real 301

1. At the registrar, replace the current dnsowl.com nameservers with the two
   nameservers Cloudflare assigns to the zone, then wait for delegation and
   DNSSEC/DS changes to settle.
2. Recreate every existing DNS record in Cloudflare before switching traffic:
   the GitHub Pages apex/www records, mail records (MX, SPF, DKIM, DMARC),
   verification records, and any subdomains. Keep the GitHub Pages `CNAME`
   file until the final cutover is verified.
3. In Cloudflare, add Redirect Rules for the three English exceptions first:
   `/posts/confirmation-bias/`, `/posts/flywheel-effect/`, and
   `/posts/google-ucp-goes-live-the-search-to-checkout-era-begins/` to their
   `/en/posts/.../` destinations. Then add the catch-all `/*` rule to
   `https://stometa.dev/$1`, preserving query strings, with status **301**.
4. Test representative encoded Chinese URLs, all English exceptions, home,
   taxonomy pages, `/links`, `/about`, and both feeds from multiple networks.
   Only after the 301 responses are confirmed should the old Hugo deployment
   be retired.

During nameserver migration, DNS caches can send visitors to either the old
or new provider. Missing or mistyped records can take the site offline, break
mail delivery, invalidate domain verification, or make HTTPS certificates
temporarily fail. DNSSEC with a stale DS record can make the entire zone
unresolvable. Cloudflare proxying can also change origin IP visibility and
cache behavior. Plan a rollback by restoring the old nameservers and records;
do not remove the soft-redirect build until propagation and mail checks pass.
