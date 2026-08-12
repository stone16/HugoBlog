---
status: accepted
---
# One Locale per Post, with optional Translation Groups

The site is bilingual but the writer is one person, so we model a Post as
belonging to exactly one Locale rather than as a container of translations.
Deliberately translated pairs are linked by a nullable Translation Group, which
is what emits a correct `hreflang` cluster; everything else stands alone.

## Considered Options

Full parity — every Post in both languages — was rejected because it turns each
Post into a permanent 2x writing commitment or an implicit commitment to machine
translation, and thin machine-translated duplicates are a negative quality
signal at the exact moment the site is trying to establish authority.

## Consequences

Each Locale's archive shows only its own Posts, so both look thinner than the
combined corpus. A reader landing on one Locale is offered the other only when a
Translation Group actually exists.
