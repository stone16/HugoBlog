---
status: accepted
---
# An Artifact's address is decoupled from its access rule

A Slug that is memorable is by definition guessable, so the address cannot also
be the lock. The Slug is readable and permanent; a separate visibility rule
(`public` | `password` | `invited`) governs entry and can change at any time
without breaking a link already sent. New Artifacts default to `password` and
`noindex`.

## Consequences

Encoding access in the label (`secure-<slug>`) was rejected twice over: it
publishes a map of which pages are worth attacking, and an Artifact's audience
changes far more often than its name should. Note also that a dotted prefix
(`<slug>.secure.stometa.dev`) exceeds Cloudflare Universal SSL's single wildcard
level and would silently fail TLS.
